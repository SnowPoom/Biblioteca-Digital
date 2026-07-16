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
    EN_REVISION = 'en_revision'
    PUBLICADO = 'publicado'
    RETIRADO = 'retirado'

    ESTADOS = [
        (BORRADOR, 'Borrador'),
        (EN_REVISION, 'En Revisión'),
        (PUBLICADO, 'Publicado'),
        (RETIRADO, 'Retirado'),
    ]

    titulo = models.CharField(max_length=255)
    portada = models.ImageField(upload_to='portadas/', blank=True)
    contenido_texto = models.TextField(blank=True, default='')
    numero_paginas = models.PositiveIntegerField(default=0)
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
        """Valida los requisitos de publicacion y cambia el estado a 'En Revision'.

        Reglas de negocio aplicadas:
        - RN-PUB-03: Portada obligatoria.
        - RN-PUB-04: Contenido textual obligatorio (no se permiten libros solo con imagenes).
        - RN-PUB-05: Maximo 500 paginas.
        - RN-PUB-07: Al menos una categoria tematica.

        Retorna True si la publicacion fue aceptada para revision, False en caso contrario.
        """
        if not self.tiene_portada():
            return False

        if not self.tiene_contenido_textual():
            return False

        if not self.tiene_categorias():
            return False

        if not self.esta_dentro_del_limite_de_paginas():
            return False

        self.estado = self.EN_REVISION
        self.save()
        return True

    def retirar(self):
        """Retira el libro de la plataforma y elimina las anotaciones asociadas.

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
        except Anotacion.DoesNotExist:
            return None
