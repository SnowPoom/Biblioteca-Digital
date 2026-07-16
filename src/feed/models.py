from django.conf import settings
from django.db import models


class Seguimiento(models.Model):
    """Relación entre un usuario que sigue (seguidor) y uno al que sigue (seguido)."""

    seguidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='siguiendo',
    )
    seguido = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seguidores',
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seguidor', 'seguido')
        ordering = ['-creado']

    def __str__(self):
        return f'{self.seguidor.username} sigue a {self.seguido.username}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Notificacion.objects.create(
                usuario=self.seguido,
                mensaje=f'El usuario {self.seguidor.username} ha comenzado a seguirte.'
            )


class Categoria(models.Model):
    """Etiqueta temática que puede asociarse a una Publicacion."""

    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Publicacion(models.Model):
    """Material publicado por un usuario: libro o colección."""

    LIBRO = 'libro'
    COLECCION = 'coleccion'

    TIPOS = [
        (LIBRO, 'Libro'),
        (COLECCION, 'Colección'),
    ]

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publicaciones',
    )
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, default='')
    tipo = models.CharField(max_length=20, choices=TIPOS, default=LIBRO)
    categorias = models.ManyToManyField(
        Categoria,
        blank=True,
        related_name='publicaciones',
    )
    creado = models.DateTimeField(auto_now_add=True)

    @property
    def portada_url(self):
        if self.tipo == self.LIBRO:
            from src.materiales.models import Libro
            try:
                libro = Libro.objects.get(pk=self.pk)
                if libro.portada:
                    return libro.portada.url
            except Libro.DoesNotExist:
                pass
        return None

    class Meta:
        # El feed debe entregarse del más reciente al más antiguo
        ordering = ['-creado']

    def __str__(self):
        return f'{self.titulo} ({self.get_tipo_display()}) — {self.autor.username}'



class Republicacion(models.Model):
    """
    Acción de un usuario seguido de compartir una Publicacion ajena.
    Preserva la autoría original a través de la FK a Publicacion.
    """

    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='republicaciones',
    )
    republicado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mis_republicaciones',
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('publicacion', 'republicado_por')
        ordering = ['-creado']

    def __str__(self):
        return (
            f'{self.republicado_por.username} republicó '
            f'"{self.publicacion.titulo}" de {self.publicacion.autor.username}'
        )


class Notificacion(models.Model):
    """
    Notificación para un usuario sobre algún evento, como ser seguido por otro usuario.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
    )
    mensaje = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, default='info')
    extra_data = models.JSONField(default=dict, blank=True)
    leida = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f'Notificación para {self.usuario.username}: {self.mensaje}'

