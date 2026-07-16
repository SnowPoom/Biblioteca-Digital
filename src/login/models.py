import datetime
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class PerfilUsuario(models.Model):
    ESTUDIANTE = 'estudiante'
    PROFESOR = 'profesor'

    TIPOS_USUARIO = [
        (ESTUDIANTE, 'Estudiante'),
        (PROFESOR, 'Profesor'),
    ]

    # RN-EXP-01: La cuota se mide en numero de paginas descargadas
    CUOTA_BASE = 500

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
    )
    rol = models.CharField(
        max_length=20,
        choices=TIPOS_USUARIO,
        default=ESTUDIANTE,
    )
    cuota_descarga = models.IntegerField(default=CUOTA_BASE)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.email} ({self.get_rol_display()})'

    def puede_descargar(self, paginas_libro):
        """RN-EXP-01: Verifica si la cantidad de paginas del libro no excede la cuota disponible."""
        return paginas_libro <= self.cuota_descarga

    def reducir_cuota(self, paginas_libro):
        """Reduce la cuota disponible segun las paginas del libro descargado."""
        self.cuota_descarga -= paginas_libro
        self.save()

    def incrementar_cuota_por_publicacion(self):
        """RN-EXP-03: Por cada libro publicado, la cuota aumenta en 100 paginas adicionales."""
        self.cuota_descarga += 100
        self.save()


class RecuperacionContrasena(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recuperaciones',
    )
    codigo = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    creado = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f'Recuperación de contraseña para {self.usuario.email}'

    def esta_vigente(self):
        limite = timezone.now() - datetime.timedelta(hours=24)
        return not self.usado and self.creado >= limite
