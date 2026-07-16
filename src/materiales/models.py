from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

LIMITE_MAXIMO_PAGINAS = 500


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    BORRADOR = 'borrador'
    PUBLICADO = 'publicado'
    RETIRADO = 'retirado'

    ESTADOS = [
        (BORRADOR, 'Borrador'),
        (PUBLICADO, 'Publicado'),
        (RETIRADO, 'Retirado'),
    ]

    titulo = models.CharField(max_length=255)
    portada = models.ImageField(upload_to='portadas/', blank=True)
    contenido_texto = models.TextField(blank=True, default='')
    numero_paginas = models.PositiveIntegerField(default=0)
    republicaciones = models.PositiveIntegerField(default=0)
    visualizaciones = models.PositiveIntegerField(default=0)
    descargas = models.PositiveIntegerField(default=0)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='libros',
    )
    categorias = models.ManyToManyField(
        Categoria,
        blank=True,
        related_name='libros',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=BORRADOR,
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
        ordering = ['-creado']

    def __str__(self):
        return f'{self.titulo} - {self.autor.get_full_name()}'

    def tiene_portada(self):
        return bool(self.portada and self.portada.name)

    def tiene_contenido_textual(self):
        return bool(self.contenido_texto and self.contenido_texto.strip())

    def tiene_categorias(self):
        return self.categorias.exists()

    def esta_dentro_del_limite_de_paginas(self):
        return self.numero_paginas <= LIMITE_MAXIMO_PAGINAS

    def publicar(self):
        """Valida los requisitos de publicacion, realiza la validacion
        automatizada de contenido y cambia el estado.

        Reglas de negocio aplicadas:
        - RN-PUB-03: Portada obligatoria.
        - RN-PUB-04: Contenido textual obligatorio.
        - RN-PUB-05: Maximo 500 paginas.
        - RN-PUB-07: Al menos una categoria tematica.
        - RN-PUB-02: Validacion automatizada de contenido.

        Retorna (True, 'mensaje') si la publicacion fue exitosa, o (False, 'mensaje') en caso de rechazo.
        """
        if not self.tiene_portada():
            return False, "Falta portada."

        if not self.tiene_contenido_textual():
            return False, "Falta contenido textual."

        if not self.tiene_categorias():
            return False, "Falta asignar categoría."

        if not self.esta_dentro_del_limite_de_paginas():
            return False, "Supera límite de páginas."

        # Validacion automatizada de contenido
        from src.materiales.validacion_contenido import ValidadorContenido
        validador = ValidadorContenido()
        resultado = validador.validar(self)

        if resultado['aprobado']:
            self.estado = self.PUBLICADO
            self.save()

            # RN-EXP-03: Incrementar la cuota del autor por cada libro publicado
            self.autor.perfil.incrementar_cuota_por_publicacion()

            # Crear o actualizar la publicación para el feed
            from src.feed.models import Publicacion, Categoria as FeedCategoria
            pub, created = Publicacion.objects.get_or_create(
                pk=self.pk,
                defaults={
                    'autor': self.autor,
                    'titulo': self.titulo,
                    'tipo': Publicacion.LIBRO,
                }
            )
            if not created:
                pub.titulo = self.titulo
                pub.save()
            
            # Sincronizar categorías
            pub.categorias.clear()
            for cat in self.categorias.all():
                feed_cat, _ = FeedCategoria.objects.get_or_create(nombre=cat.nombre)
                pub.categorias.add(feed_cat)

            return True, "Publicación exitosa."
        else:
            self.estado = self.BORRADOR
            self.save()
            from src.feed.models import Notificacion
            Notificacion.objects.create(
                usuario=self.autor,
                mensaje=resultado['mensaje'],
            )
            return False, resultado['mensaje']

    def editar(self, usuario_editor):
        """Aplica las reglas de negocio al editar un libro.
        
        Reglas de negocio aplicadas:
        - RN-PUB-11: Un usuario no puede editar ni eliminar material publicado por otro usuario.
        - RN-PUB-09: Si el autor edita un libro ya publicado, el material debe volver a pasar la validacion.
        """
        if self.autor != usuario_editor:
            raise PermissionError("No tiene permisos para editar este libro.")
        
        if self.estado == self.PUBLICADO:
            self.estado = self.BORRADOR
            
        self.save()

    def republicar(self, usuario):
        """Republica un libro preservando la autoría original.
        
        Reglas de negocio aplicadas:
        - RN-PUB-12: La republicación preserva la autoría original y no crea una copia independiente.
        - RN-PUB-13: Se incrementa el contador de republicaciones.
        """
        if self.estado != self.PUBLICADO:
            raise ValueError("Solo los libros publicados pueden ser republicados.")
            
        from django.db import transaction
        from django.db.models import F
        from src.feed.models import Publicacion, Republicacion
        
        with transaction.atomic():
            pub, pub_created = Publicacion.objects.get_or_create(
                pk=self.pk,
                defaults={
                    'autor': self.autor,
                    'titulo': self.titulo,
                    'tipo': Publicacion.LIBRO,
                }
            )
            if not pub_created:
                pub.titulo = self.titulo
                pub.save(update_fields=['titulo'])
                
            republicacion, created = Republicacion.objects.get_or_create(
                publicacion=pub,
                republicado_por=usuario
            )
            
            if created:
                self.republicaciones = F('republicaciones') + 1
                self.save(update_fields=['republicaciones'])
                self.refresh_from_db(fields=['republicaciones'])
                
        return republicacion, created

    def retirar(self):
        """Retira (despublica) el libro de la plataforma.

        Reglas de negocio aplicadas:
        - RN-PUB-10: El autor puede retirar su propio material en cualquier momento.
        - RN-ANO-08: Si un libro es retirado, las anotaciones asociadas se eliminan.
        """
        self.estado = self.RETIRADO
        self.save()
        # RN-ANO-08: Las anotaciones pierden sentido al retirar el libro
        self.anotaciones.all().delete()

        # RN-PUB-10: El libro comparte PK con su Publicacion en el feed; se
        # elimina para que deje de mostrarse en feeds y republicaciones ajenas.
        from src.feed.models import Publicacion
        Publicacion.objects.filter(pk=self.pk).delete()

    def registrar_descarga(self):
        """RN-EXP-05: Incrementa el contador de descargas como metrica de la publicacion."""
        self.descargas += 1
        self.save()

    def _obtener_contenido_paginas(self, inicio=None, fin=None):
        """Extrae unicamente el HTML correspondiente al rango de paginas indicado."""
        import re
        texto = self.contenido_texto or ''
        if inicio is None and fin is None:
            return texto
            
        paginas = re.split(r'<div\s+class=[\'"]page-gap[\'"][^>]*>\s*</div>', texto)
        
        idx_inicio = max(0, inicio - 1) if inicio is not None else 0
        idx_fin = fin if fin is not None else len(paginas)
        
        paginas_seleccionadas = paginas[idx_inicio:idx_fin]
        return '<div class="page-gap"></div>'.join(paginas_seleccionadas)

    def generar_contenido_descarga(self, formato='pdf', pagina_inicio=None, pagina_fin=None):
        """Genera un archivo en formato PDF o EPUB con el contenido del libro
        y metadatos de autoria original (RN-EXP-06)."""
        contenido_html = self._obtener_contenido_paginas(pagina_inicio, pagina_fin)
        if formato == 'epub':
            return self._generar_epub(contenido_html)
        return self._generar_pdf(contenido_html)

    def _extraer_texto_plano(self, texto):
        """Extrae texto plano del contenido HTML especificado."""
        import re
        texto = texto or ''
        # Reemplazar saltos de parrafo/divs con saltos de linea
        texto = re.sub(r'<br\s*/?>', '\n', texto)
        texto = re.sub(r'</p>', '\n', texto)
        texto = re.sub(r'</div>', '\n', texto)
        texto = re.sub(r'<[^>]+>', '', texto)
        # Decodificar entidades HTML basicas
        texto = texto.replace('&amp;', '&')
        texto = texto.replace('&lt;', '<')
        texto = texto.replace('&gt;', '>')
        texto = texto.replace('&nbsp;', ' ')
        texto = texto.replace('&quot;', '"')
        return texto.strip()

    def _generar_pdf(self, contenido_html):
        """Genera un PDF valido con el contenido proporcionado y metadatos obligatorios."""
        nombre_autor = self.autor.get_full_name() or self.autor.username
        fuente = "Biblioteca Digital"
        texto_contenido = self._extraer_texto_plano(contenido_html)

        linea_meta = f"Autor original: {nombre_autor}  |  Fuente: {fuente}"
        lineas = [linea_meta, f"Titulo: {self.titulo}", ""]
        for parrafo in texto_contenido.split('\n'):
            parrafo = parrafo.strip()
            if not parrafo:
                lineas.append("")
                continue
            while len(parrafo) > 80:
                corte = parrafo.rfind(' ', 0, 80)
                if corte == -1:
                    corte = 80
                lineas.append(parrafo[:corte])
                parrafo = parrafo[corte:].strip()
            if parrafo:
                lineas.append(parrafo)

        y_inicio = 740
        interlineado = 14
        comandos = ["/F1 11 Tf"]
        y = y_inicio
        for linea in lineas:
            linea_safe = linea.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            comandos.append(f"BT 60 {y} Td ({linea_safe}) Tj ET")
            y -= interlineado
            if y < 50:
                break

        stream = "\n".join(comandos)
        largo_stream = len(stream)

        objetos = []
        objetos.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
        objetos.append("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj")
        objetos.append(
            "3 0 obj\n<< /Type /Page /Parent 2 0 R "
            "/MediaBox [0 0 612 792] "
            "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj"
        )
        objetos.append(
            f"4 0 obj\n<< /Length {largo_stream} >>\n"
            f"stream\n{stream}\nendstream\nendobj"
        )
        objetos.append(
            "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj"
        )
        objetos.append(
            f"6 0 obj\n<< /Author ({nombre_autor}) "
            f"/Title ({self.titulo}) "
            f"/Producer ({fuente}) >>\nendobj"
        )

        cuerpo = "\n".join(objetos)
        encabezado = "%PDF-1.4\n"
        offset = len(encabezado)
        offsets = []
        for obj in objetos:
            offsets.append(offset)
            offset += len(obj) + 1

        xref_inicio = offset
        xref = "xref\n"
        xref += f"0 {len(objetos) + 1}\n"
        xref += "0000000000 65535 f \n"
        for pos in offsets:
            xref += f"{pos:010d} 00000 n \n"

        trailer = (
            f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R /Info 6 0 R >>\n"
            f"startxref\n{xref_inicio}\n%%EOF"
        )

        return (encabezado + cuerpo + "\n" + xref + trailer).encode('latin-1')

    def _generar_epub(self, contenido_html):
        """Genera un EPUB valido con el contenido proporcionado y metadatos obligatorios."""
        import io
        import zipfile

        nombre_autor = self.autor.get_full_name() or self.autor.username
        fuente = "Biblioteca Digital"
        if not contenido_html or not contenido_html.strip():
            contenido_html = '<p>Sin contenido.</p>'
        mimetype = 'application/epub+zip'
        container_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
            '  <rootfiles>\n'
            '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
            '  </rootfiles>\n'
            '</container>'
        )
        content_opf = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">\n'
            '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
            f'    <dc:title>{self.titulo}</dc:title>\n'
            f'    <dc:creator>{nombre_autor}</dc:creator>\n'
            f'    <dc:publisher>{fuente}</dc:publisher>\n'
            f'    <dc:source>{fuente}</dc:source>\n'
            '    <dc:language>es</dc:language>\n'
            f'    <dc:identifier id="uid">libro-{self.pk}</dc:identifier>\n'
            '    <meta property="dcterms:modified">2026-01-01T00:00:00Z</meta>\n'
            '  </metadata>\n'
            '  <manifest>\n'
            '    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>\n'
            '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>\n'
            '  </manifest>\n'
            '  <spine>\n'
            '    <itemref idref="chapter1"/>\n'
            '  </spine>\n'
            '</package>'
        )
        nav_xhtml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
            '<head><title>Navegacion</title></head>\n'
            '<body>\n'
            '<nav epub:type="toc">\n'
            '  <ol><li><a href="chapter1.xhtml">Contenido</a></li></ol>\n'
            '</nav>\n'
            '</body></html>'
        )
        chapter_xhtml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
            '<head>\n'
            f'  <title>{self.titulo}</title>\n'
            '  <style>body { font-family: serif; margin: 2em; } '
            '.metadata { color: #555; border-bottom: 1px solid #ccc; padding-bottom: 1em; margin-bottom: 2em; }</style>\n'
            '</head>\n'
            '<body>\n'
            f'  <div class="metadata">\n'
            f'    <p><strong>Autor original:</strong> {nombre_autor}</p>\n'
            f'    <p><strong>Fuente:</strong> {fuente}</p>\n'
            f'  </div>\n'
            f'  <h1>{self.titulo}</h1>\n'
            f'  {contenido_html}\n'
            '</body></html>'
        )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as epub:
            epub.writestr('mimetype', mimetype, compress_type=zipfile.ZIP_STORED)
            epub.writestr('META-INF/container.xml', container_xml)
            epub.writestr('OEBPS/content.opf', content_opf)
            epub.writestr('OEBPS/nav.xhtml', nav_xhtml)
            epub.writestr('OEBPS/chapter1.xhtml', chapter_xhtml)

        return buffer.getvalue()

    def metricas_para(self, usuario):
        """Devuelve las métricas acumuladas del libro si el usuario es el autor.

        Regla de negocio aplicada:
        - RN-PUB-13: El sistema registra métricas de visualizaciones,
          republicaciones y descargas, visibles únicamente para el autor.
        """
        if usuario != self.autor:
            return None
        return {
            'visualizaciones': self.visualizaciones,
            'republicaciones': self.republicaciones,
            'descargas': self.descargas,
        }

    def fragmentos_anotados_por(self, usuario):
        """Fragmentos con anotacion activa del usuario en este libro.

        Regla de negocio aplicada:
        - RN-ANO-05: Los fragmentos anotados deben mostrarse visualmente
          diferenciados durante toda la lectura, no solo al crearse.
        """
        return list(
            self.anotaciones.filter(usuario=usuario).values_list(
                'fragmento_texto', flat=True
            )
        )


LIMITE_CARACTERES_ANOTACION = 150


class Anotacion(models.Model):
    """Anotacion personal vinculada a un fragmento de texto o imagen de un libro.

    Reglas de negocio aplicadas:
    - RN-ANO-01: Las anotaciones son personales e intransferibles.
    - RN-ANO-02: Se crean seleccionando un fragmento de texto o una imagen.
    - RN-ANO-03: Limite maximo de 150 caracteres.
    - RN-ANO-04: Un fragmento puede tener como maximo una anotacion activa por usuario.
    """

    TEXTO = 'texto'
    IMAGEN = 'imagen'

    TIPOS_FRAGMENTO = [
        (TEXTO, 'Texto'),
        (IMAGEN, 'Imagen'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='anotaciones',
    )
    libro = models.ForeignKey(
        Libro,
        on_delete=models.CASCADE,
        related_name='anotaciones',
    )
    fragmento_texto = models.CharField(max_length=500)
    tipo_fragmento = models.CharField(
        max_length=10,
        choices=TIPOS_FRAGMENTO,
        default=TEXTO,
    )
    contenido = models.CharField(max_length=LIMITE_CARACTERES_ANOTACION)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Anotacion'
        verbose_name_plural = 'Anotaciones'
        # RN-ANO-04: Solo una anotacion activa por fragmento y usuario
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'libro', 'fragmento_texto'],
                name='unica_anotacion_por_fragmento_usuario',
            ),
        ]

    def __str__(self):
        return f'Anotacion de {self.usuario.username} en "{self.libro.titulo}"'

    def esta_activa(self):
        """Indica si la anotacion esta vigente para resaltado visual (RN-ANO-05)."""
        return bool(self.pk and self.contenido)

    def editar(self, nuevo_contenido):
        """Actualiza el contenido de la anotacion respetando el limite de caracteres.

        Reglas de negocio aplicadas:
        - RN-ANO-03: Limite maximo de 150 caracteres.
        - RN-ANO-06: El usuario puede editar sus propias anotaciones.
        """
        if len(nuevo_contenido) > LIMITE_CARACTERES_ANOTACION:
            raise ValueError(
                f"El contenido supera el limite de {LIMITE_CARACTERES_ANOTACION} caracteres."
            )
        self.contenido = nuevo_contenido
        self.save()

    def eliminar(self):
        """Elimina la anotacion del sistema.

        Regla de negocio aplicada:
        - RN-ANO-06: El usuario puede eliminar sus propias anotaciones.
        """
        self.delete()

    @classmethod
    def para_fragmento(cls, usuario, libro, fragmento_texto):
        """Recupera la anotacion del usuario asociada a un fragmento.

        Regla de negocio aplicada:
        - RN-ANO-06: Permite editar o eliminar la anotacion accediendo
          directamente desde el fragmento resaltado durante la lectura.
        """
        return cls.objects.filter(
            usuario=usuario, libro=libro, fragmento_texto=fragmento_texto
        ).first()


class Coleccion(models.Model):
    PUBLICA = 'publica'
    PRIVADA = 'privada'
    OPCIONES_VISIBILIDAD = [
        (PUBLICA, 'Pública'),
        (PRIVADA, 'Privada'),
    ]

    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, default='')
    visibilidad = models.CharField(
        max_length=20,
        choices=OPCIONES_VISIBILIDAD,
        default=PUBLICA,
    )
    limite_libros = models.PositiveIntegerField(
        default=20,
        validators=[
            MinValueValidator(5, message="El mínimo es de 5 libros"),
            MaxValueValidator(20, message="El máximo de libros es 20")
        ]
    )
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='colecciones_creadas',
    )
    categorias = models.ManyToManyField(
        Categoria,
        blank=True,
        related_name='colecciones',
    )
    libros = models.ManyToManyField(
        Libro,
        blank=True,
        related_name='colecciones_pertenecientes',
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Colección'
        verbose_name_plural = 'Colecciones'

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        super().save(*args, **kwargs)
        if es_nuevo and self.creador:
            self.agregar_participante(self.creador, rol=ParticipacionColeccion.ADMINISTRADOR)

    def publicar(self):
        if not self.categorias.exists():
            return False, "La colección debe tener al menos una categoría"
        self.visibilidad = self.PUBLICA
        self.save()
        return True, "Colección publicada"

    def es_administrador(self, usuario):
        return self.participaciones.filter(usuario=usuario, rol=ParticipacionColeccion.ADMINISTRADOR).exists()

    def agregar_participante(self, usuario, rol='participante'):
        ParticipacionColeccion.objects.get_or_create(
            coleccion=self,
            usuario=usuario,
            defaults={'rol': rol}
        )

    def invitar_usuario(self, admin, usuario_invitado):
        if not self.es_administrador(admin):
            raise PermissionError("Solo el administrador puede invitar usuarios.")
        
        if self.participaciones.count() >= 15:
            return False, "Se ha alcanzado el límite máximo de 15 participantes."
            
        invitacion = InvitacionColeccion.objects.filter(coleccion=self, usuario_invitado=usuario_invitado).first()
        if invitacion:
            if invitacion.estado != InvitacionColeccion.PENDIENTE:
                return False, "Ya existe una invitación procesada para este usuario."
            return True, "La invitación ya había sido enviada."
            
        invitacion = InvitacionColeccion.objects.create(
            coleccion=self,
            usuario_invitado=usuario_invitado,
            estado=InvitacionColeccion.PENDIENTE
        )
        
        from src.feed.models import Notificacion
        Notificacion.objects.create(
            usuario=usuario_invitado,
            mensaje=f"{admin.username} te ha invitado a colaborar en la colección '{self.nombre}'.",
            tipo='invitacion_coleccion',
            extra_data={'invitacion_id': invitacion.id, 'coleccion_id': self.id, 'estado': InvitacionColeccion.PENDIENTE}
        )
        return True, "Invitación enviada."

    def solicitar_acceso(self, usuario_solicitante):
        if self.visibilidad != self.PUBLICA:
            return False, "No se puede solicitar acceso a una colección privada."
            
        if self.participaciones.count() >= 15:
            return False, "Se ha alcanzado el límite máximo de 15 participantes."
            
        solicitud = SolicitudAccesoColeccion.objects.filter(coleccion=self, usuario_solicitante=usuario_solicitante).first()
        if solicitud:
            if solicitud.estado != SolicitudAccesoColeccion.PENDIENTE:
                return False, "Ya existe una solicitud procesada para este usuario."
            return True, "La solicitud ya había sido enviada."
            
        solicitud = SolicitudAccesoColeccion.objects.create(
            coleccion=self,
            usuario_solicitante=usuario_solicitante,
            estado=SolicitudAccesoColeccion.PENDIENTE
        )
        
        if self.creador:
            from src.feed.models import Notificacion
            Notificacion.objects.create(
                usuario=self.creador,
                mensaje=f"{usuario_solicitante.username} ha solicitado acceso para colaborar en tu colección '{self.nombre}'.",
                tipo='solicitud_acceso_coleccion',
                extra_data={'solicitud_id': solicitud.id, 'coleccion_id': self.id, 'estado': SolicitudAccesoColeccion.PENDIENTE}
            )
        return True, "Solicitud enviada."
        
    def retirar_participante(self, admin_usuario, participante_usuario):
        if not self.participaciones.filter(usuario=admin_usuario, rol=ParticipacionColeccion.ADMINISTRADOR).exists():
            raise PermissionError("Solo un administrador puede retirar participantes.")
        if self.creador == participante_usuario:
            raise PermissionError("No se puede retirar al creador de la colección.")
            
        participacion = self.participaciones.filter(usuario=participante_usuario).first()
        if participacion:
            participacion.delete()
            from src.feed.models import Notificacion
            Notificacion.objects.create(
                usuario=participante_usuario,
                tipo='sistema',
                mensaje=f'Has sido retirado de la colección "{self.nombre}".',
                extra_data={'coleccion_id': self.id}
            )
            return True
        return False
        
    def abandonar(self, usuario):
        participacion = self.participaciones.filter(usuario=usuario).first()
        if not participacion:
            return False
            
        if self.creador == usuario:
            otros_miembros = self.participaciones.exclude(usuario=usuario)
            if otros_miembros.exists():
                nuevo_admin = otros_miembros.first()
                nuevo_admin.rol = ParticipacionColeccion.ADMINISTRADOR
                nuevo_admin.save()
                self.creador = nuevo_admin.usuario
                self.save()
            else:
                self.creador = None
                self.save()
                
        participacion.delete()
        
        if self.creador and self.creador != usuario:
            from src.feed.models import Notificacion
            Notificacion.objects.create(
                usuario=self.creador,
                tipo='sistema',
                mensaje=f'{usuario.username} ha abandonado la colección "{self.nombre}".',
                extra_data={'coleccion_id': self.id}
            )
            
        return True

class ParticipacionColeccion(models.Model):
    ADMINISTRADOR = 'administrador'
    PARTICIPANTE = 'participante'

    OPCIONES_ROL = [
        (ADMINISTRADOR, 'Administrador'),
        (PARTICIPANTE, 'Participante'),
    ]

    coleccion = models.ForeignKey(
        Coleccion,
        on_delete=models.CASCADE,
        related_name='participaciones',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participaciones_coleccion',
    )
    rol = models.CharField(
        max_length=20,
        choices=OPCIONES_ROL,
        default=PARTICIPANTE,
    )
    fecha_union = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Participación en Colección'
        verbose_name_plural = 'Participaciones en Colecciones'
        unique_together = ('coleccion', 'usuario')

    def __str__(self):
        return f"{self.usuario.username} - {self.coleccion.nombre} ({self.rol})"

class InvitacionColeccion(models.Model):
    PENDIENTE = 'pendiente'
    ACEPTADA = 'aceptada'
    RECHAZADA = 'rechazada'
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (ACEPTADA, 'Aceptada'),
        (RECHAZADA, 'Rechazada'),
    ]

    coleccion = models.ForeignKey(Coleccion, on_delete=models.CASCADE, related_name='invitaciones')
    usuario_invitado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invitaciones_recibidas')
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    creada_en = models.DateTimeField(auto_now_add=True)

    def aceptar(self, usuario):
        from django.db import transaction
        if self.usuario_invitado != usuario:
            raise PermissionError("No puedes aceptar una invitación dirigida a otro usuario.")
            
        with transaction.atomic():
            invitacion = InvitacionColeccion.objects.select_for_update().get(id=self.id)
            if invitacion.estado != self.PENDIENTE:
                return False, "La invitación ya no está pendiente."
                
            coleccion = Coleccion.objects.select_for_update().get(id=self.coleccion.id)
            if coleccion.participaciones.count() >= 15:
                return False, "La colección ya ha alcanzado el límite máximo de participantes."
                
            invitacion.estado = self.ACEPTADA
            invitacion.save()
            coleccion.agregar_participante(usuario, rol=ParticipacionColeccion.PARTICIPANTE)
            
        self.estado = invitacion.estado
        self._actualizar_notificaciones()
        
        if self.coleccion.creador:
            from src.feed.models import Notificacion
            Notificacion.objects.create(
                usuario=self.coleccion.creador,
                tipo='sistema',
                mensaje=f'{usuario.username} aceptó tu invitación a la colección "{self.coleccion.nombre}".',
                extra_data={'coleccion_id': self.coleccion.id}
            )
        return True, "Invitación aceptada."

    def rechazar(self, usuario):
        from django.db import transaction
        if self.usuario_invitado != usuario:
            raise PermissionError("No puedes rechazar una invitación dirigida a otro usuario.")
            
        with transaction.atomic():
            invitacion = InvitacionColeccion.objects.select_for_update().get(id=self.id)
            if invitacion.estado != self.PENDIENTE:
                return False, "La invitación ya no está pendiente."
                
            invitacion.estado = self.RECHAZADA
            invitacion.save()
            
        self.estado = invitacion.estado
        self._actualizar_notificaciones()
        
        if self.coleccion.creador:
            from src.feed.models import Notificacion
            Notificacion.objects.create(
                usuario=self.coleccion.creador,
                tipo='sistema',
                mensaje=f'{usuario.username} rechazó tu invitación a la colección "{self.coleccion.nombre}".',
                extra_data={'coleccion_id': self.coleccion.id}
            )
        return True, "Invitación rechazada."
        
    def _actualizar_notificaciones(self):
        from src.feed.models import Notificacion
        notifs = Notificacion.objects.filter(usuario=self.usuario_invitado, tipo='invitacion_coleccion')
        for n in notifs:
            if n.extra_data.get('invitacion_id') == self.id:
                n.extra_data['estado'] = self.estado
                n.save()


class SolicitudAccesoColeccion(models.Model):
    PENDIENTE = 'pendiente'
    APROBADA = 'aprobada'
    RECHAZADA = 'rechazada'
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (APROBADA, 'Aprobada'),
        (RECHAZADA, 'Rechazada'),
    ]

    coleccion = models.ForeignKey(Coleccion, on_delete=models.CASCADE, related_name='solicitudes')
    usuario_solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes_acceso')
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    creada_en = models.DateTimeField(auto_now_add=True)

    def aprobar(self, admin_usuario):
        from django.db import transaction
        if not self.coleccion.participaciones.filter(usuario=admin_usuario, rol=ParticipacionColeccion.ADMINISTRADOR).exists():
            raise PermissionError("Solo un administrador puede aprobar solicitudes.")
            
        with transaction.atomic():
            solicitud = SolicitudAccesoColeccion.objects.select_for_update().get(id=self.id)
            if solicitud.estado != self.PENDIENTE:
                return False, "La solicitud ya no está pendiente."
                
            coleccion = Coleccion.objects.select_for_update().get(id=self.coleccion.id)
            if coleccion.participaciones.count() >= 15:
                return False, "La colección ya ha alcanzado el límite de participantes."
                
            solicitud.estado = self.APROBADA
            solicitud.save()
            coleccion.agregar_participante(self.usuario_solicitante, rol=ParticipacionColeccion.PARTICIPANTE)
            
        self.estado = solicitud.estado
        self._actualizar_notificaciones(admin_usuario)
        from src.feed.models import Notificacion
        Notificacion.objects.create(
            usuario=self.usuario_solicitante,
            tipo='sistema',
            mensaje=f'Tu solicitud para unirte a la colección "{self.coleccion.nombre}" ha sido aprobada.',
            extra_data={'coleccion_id': self.coleccion.id}
        )
        return True

    def rechazar(self, admin_usuario):
        from django.db import transaction
        if not self.coleccion.participaciones.filter(usuario=admin_usuario, rol=ParticipacionColeccion.ADMINISTRADOR).exists():
            raise PermissionError("Solo un administrador puede rechazar solicitudes.")
            
        with transaction.atomic():
            solicitud = SolicitudAccesoColeccion.objects.select_for_update().get(id=self.id)
            if solicitud.estado != self.PENDIENTE:
                return False, "La solicitud ya no está pendiente."
                
            solicitud.estado = self.RECHAZADA
            solicitud.save()
            
        self.estado = solicitud.estado
        self._actualizar_notificaciones(admin_usuario)
        from src.feed.models import Notificacion
        Notificacion.objects.create(
            usuario=self.usuario_solicitante,
            tipo='sistema',
            mensaje=f'Tu solicitud para unirte a la colección "{self.coleccion.nombre}" ha sido rechazada.',
            extra_data={'coleccion_id': self.coleccion.id}
        )
        return True
        
    def _actualizar_notificaciones(self, admin):
        from src.feed.models import Notificacion
        notifs = Notificacion.objects.filter(usuario=admin, tipo='solicitud_acceso_coleccion')
        for n in notifs:
            if n.extra_data.get('solicitud_id') == self.id:
                n.extra_data['estado'] = self.estado
                n.save()

from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete, sender=ParticipacionColeccion)
def reasingar_creador_al_eliminar_participacion(sender, instance, **kwargs):
    coleccion = instance.coleccion
    if coleccion.creador == instance.usuario:
        otros = coleccion.participaciones.exclude(usuario=instance.usuario)
        if otros.exists():
            nuevo_admin = otros.first()
            nuevo_admin.rol = ParticipacionColeccion.ADMINISTRADOR
            nuevo_admin.save()
            coleccion.creador = nuevo_admin.usuario
            coleccion.save()
        else:
            coleccion.creador = None
            coleccion.save()
