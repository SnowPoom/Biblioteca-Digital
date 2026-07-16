from django.conf import settings
from django.db import models


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

    def registrar_descarga(self):
        """RN-EXP-05: Incrementa el contador de descargas como metrica de la publicacion."""
        self.descargas += 1
        self.save()

    def generar_contenido_descarga(self, formato='pdf'):
        """Genera un archivo en formato PDF o EPUB con el contenido del libro
        y metadatos de autoria original (RN-EXP-06)."""
        if formato == 'epub':
            return self._generar_epub()
        return self._generar_pdf()

    def _extraer_texto_plano(self):
        """Extrae texto plano del contenido HTML del libro."""
        import re
        texto = self.contenido_texto or ''
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

    def _generar_pdf(self):
        """Genera un PDF valido con el contenido real del libro y metadatos obligatorios."""
        nombre_autor = self.autor.get_full_name() or self.autor.username
        fuente = "Biblioteca Digital"
        texto_contenido = self._extraer_texto_plano()

        # Construir las lineas de texto para el PDF
        # Encabezado con metadatos obligatorios
        linea_meta = f"Autor original: {nombre_autor}  |  Fuente: {fuente}"

        # Dividir contenido en lineas de maximo 80 caracteres
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

        # Construir stream de texto PDF con multiples lineas
        y_inicio = 740
        interlineado = 14
        comandos = ["/F1 11 Tf"]
        y = y_inicio
        for linea in lineas:
            # Escapar caracteres especiales de PDF
            linea_safe = linea.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            comandos.append(f"BT 60 {y} Td ({linea_safe}) Tj ET")
            y -= interlineado
            if y < 50:
                break  # Limite de una pagina

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

    def _generar_epub(self):
        """Genera un EPUB valido con el contenido real del libro y metadatos obligatorios."""
        import io
        import zipfile

        nombre_autor = self.autor.get_full_name() or self.autor.username
        fuente = "Biblioteca Digital"
        contenido_html = self.contenido_texto or '<p>Sin contenido.</p>'

        # Archivo mimetype (sin comprimir, segun especificacion EPUB)
        mimetype = 'application/epub+zip'

        # container.xml
        container_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
            '  <rootfiles>\n'
            '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
            '  </rootfiles>\n'
            '</container>'
        )

        # content.opf con metadatos obligatorios (RN-EXP-06)
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

        # nav.xhtml (tabla de contenidos requerida por EPUB 3)
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

        # chapter1.xhtml con contenido real y metadatos obligatorios
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

        # Construir el archivo ZIP (EPUB)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as epub:
            # mimetype debe ser el primer archivo y sin comprimir
            epub.writestr('mimetype', mimetype, compress_type=zipfile.ZIP_STORED)
            epub.writestr('META-INF/container.xml', container_xml)
            epub.writestr('OEBPS/content.opf', content_opf)
            epub.writestr('OEBPS/nav.xhtml', nav_xhtml)
            epub.writestr('OEBPS/chapter1.xhtml', chapter_xhtml)

        return buffer.getvalue()
