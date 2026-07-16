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
    # RN-EXP-02: Fecha de la ultima renovacion de cuota para el ciclo de 30 dias
    fecha_ultima_renovacion = models.DateTimeField(null=True, blank=True)
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
        from src.feed.models import Notificacion
        Notificacion.objects.create(
            usuario=self.usuario,
            mensaje=(
                f'Tu cuota de descarga ha aumentado en 100 paginas por publicar '
                f'un libro. Tu nueva cuota disponible es de {self.cuota_descarga} paginas.'
            ),
        )

    def calcular_cuota_base(self):
        """Calcula la cuota base considerando los libros publicados del usuario.

        RN-EXP-03: La cuota base se incrementa en 100 paginas por cada
        libro en estado 'Publicado', incentivando la contribucion activa.
        """
        from src.materiales.models import Libro
        libros_publicados = Libro.objects.filter(
            autor=self.usuario,
            estado=Libro.PUBLICADO,
        ).count()
        return self.CUOTA_BASE + (libros_publicados * 100)

    def fecha_proxima_renovacion(self):
        """Calcula la fecha de la proxima renovacion de cuota.

        RN-EXP-02: La cuota se renueva cada 30 dias desde la ultima renovacion.
        Si no existe fecha previa, se toma la fecha de creacion del perfil.
        """
        fecha_base = self.fecha_ultima_renovacion or self.creado
        return fecha_base + datetime.timedelta(days=30)

    def renovar_cuota_si_corresponde(self):
        """Renueva la cuota de descarga si han transcurrido 30 dias.

        RN-EXP-02: Al cumplirse el ciclo de 30 dias, la cuota se restablece
        al cupo base (que incluye el bonus por libros publicados segun RN-EXP-03).
        """
        if self.fecha_ultima_renovacion is None:
            self.fecha_ultima_renovacion = self.creado or timezone.now()

        diferencia = timezone.now() - self.fecha_ultima_renovacion
        if diferencia.days >= 30:
            self.cuota_descarga = self.calcular_cuota_base()
            self.fecha_ultima_renovacion = timezone.now()
            self.save()
            from src.feed.models import Notificacion
            Notificacion.objects.create(
                usuario=self.usuario,
                mensaje=(
                    f'Tu cuota de descarga se ha renovado automaticamente. '
                    f'Tu cuota disponible es de {self.cuota_descarga} paginas.'
                ),
            )


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
