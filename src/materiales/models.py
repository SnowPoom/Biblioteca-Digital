from django.conf import settings
from django.db import models


LIMITE_MAXIMO_PAGINAS = 500
LIMITE_CARACTERES_ANOTACION = 150


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
        Reglas de negocio aplicadas:
        - RN-PUB-10: El autor puede retirar su material en cualquier momento.
        - RN-ANO-08: Al retirar un libro, las anotaciones asociadas se eliminan.
        """
        self.anotaciones.all().delete()
        self.estado = self.RETIRADO
        self.save()


class Anotacion(models.Model):
    """Anotacion personal vinculada a un fragmento de texto o imagen de un libro.

    Las anotaciones son estrictamente privadas (RN-ANO-01) y cada fragmento
    admite como maximo una anotacion activa por usuario (RN-ANO-04).
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
        # RN-ANO-04: Maximo una anotacion activa por fragmento por usuario
        unique_together = ['usuario', 'libro', 'fragmento_texto']
        ordering = ['-creado']

    def __str__(self):
        return f'Anotacion de {self.usuario.get_full_name()} en {self.libro.titulo}'

    def esta_activa(self):
        """Indica si la anotacion esta vigente (existe en base de datos y tiene contenido)."""
        return bool(self.pk and self.contenido)

    def pertenece_al_usuario(self, usuario):
        return self.usuario_id == getattr(usuario, 'id', None)

    def puede_ser_gestionada_por(self, usuario):
        return self.pertenece_al_usuario(usuario)

    def actualizar_contenido(self, nuevo_contenido):
        self.contenido = nuevo_contenido
        self.save(update_fields=['contenido', 'actualizado'])

    def serializar_para_lectura(self):
        return {
            'id': self.id,
            'fragmento_texto': self.fragmento_texto,
            'tipo_fragmento': self.tipo_fragmento,
            'contenido': self.contenido,
            'creado': self.creado.isoformat() if self.creado else None,
            'actualizado': self.actualizado.isoformat() if self.actualizado else None,
        }

    @staticmethod
    def validar_contenido(texto):
        """Valida que el contenido no supere el limite de caracteres.

        Regla de negocio: RN-ANO-03
        Retorna True si el texto es valido, False en caso contrario.
        """
        return len(texto) <= LIMITE_CARACTERES_ANOTACION

    @staticmethod
    def obtener_anotacion_existente(usuario, libro, fragmento_texto):
        """Recupera la anotacion existente de un usuario sobre un fragmento especifico.

        Regla de negocio: RN-ANO-04
        Retorna la instancia de Anotacion si existe, None en caso contrario.
        """
        try:
            return Anotacion.objects.get(
                usuario=usuario,
                libro=libro,
                fragmento_texto=fragmento_texto,
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
