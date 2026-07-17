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



class Publicacion(models.Model):
    """Material publicado por un usuario: libro o colección."""

    LIBRO = 'libro'
    COLECCION = 'coleccion'

    libro = models.OneToOneField(
        'materiales.Libro',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='publicacion_feed'
    )
    coleccion = models.OneToOneField(
        'materiales.Coleccion',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='publicacion_feed'
    )
    creado = models.DateTimeField(auto_now_add=True)

    @property
    def tipo(self):
        return 'coleccion' if self.coleccion else 'libro'
        
    @property
    def titulo(self):
        return self.libro.titulo if self.libro else self.coleccion.nombre if self.coleccion else ''

    @property
    def descripcion(self):
        return self.libro.contenido_texto[:100] if self.libro else self.coleccion.descripcion if self.coleccion else ''

    @property
    def autor(self):
        return self.libro.autor if self.libro else self.coleccion.creador if self.coleccion else None

    @property
    def categorias(self):
        return self.libro.categorias if self.libro else self.coleccion.categorias if self.coleccion else None

    @property
    def portada_url(self):
        if self.libro and self.libro.portada:
            return self.libro.portada.url
        return None

    @property
    def url(self):
        from django.urls import reverse
        if self.libro:
            return reverse('materiales:detalle_libro', args=[self.libro.pk])
        elif self.coleccion:
            return reverse('colecciones:detalle_coleccion', args=[self.coleccion.pk])
        return '#'

    @property
    def material_pk(self):
        return self.libro.pk if self.libro else self.coleccion.pk if self.coleccion else None

    def get_tipo_display(self):
        return 'Colección' if self.coleccion else 'Libro'

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

