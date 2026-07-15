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
