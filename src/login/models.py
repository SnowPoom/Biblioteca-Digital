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
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.email} ({self.get_rol_display()})'


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
