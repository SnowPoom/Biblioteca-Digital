from django.conf import settings
from django.db import models


class HistorialLectura(models.Model):
    """Registro de cada lectura realizada por un usuario.

    Senales primarias para el motor de recomendaciones (RN-REC-01).
    La fecha permite ponderar la actividad reciente con mayor peso (RN-REC-08).
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='historial_lectura',
    )
    publicacion = models.ForeignKey(
        'feed.Publicacion',
        on_delete=models.CASCADE,
        related_name='lecturas',
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historial de lectura'
        verbose_name_plural = 'Historiales de lectura'
        ordering = ['-fecha']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'publicacion'],
                name='lectura_unica_por_usuario_publicacion',
            ),
        ]

    def __str__(self):
        return (
            f'{self.usuario.username} leyo '
            f'"{self.publicacion.titulo}" el {self.fecha:%Y-%m-%d}'
        )


class DescarteRecomendacion(models.Model):
    """Registro permanente de contenido descartado por el usuario.

    RN-REC-04: El descarte impide que el contenido se recomiende de nuevo
    y alimenta el ajuste de recomendaciones futuras.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='descartes',
    )
    publicacion = models.ForeignKey(
        'feed.Publicacion',
        on_delete=models.CASCADE,
        related_name='descartes',
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Descarte de recomendacion'
        verbose_name_plural = 'Descartes de recomendacion'
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'publicacion'],
                name='descarte_unico_por_usuario_publicacion',
            ),
        ]

    def __str__(self):
        return (
            f'{self.usuario.username} descarto '
            f'"{self.publicacion.titulo}"'
        )
