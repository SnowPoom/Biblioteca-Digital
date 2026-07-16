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
