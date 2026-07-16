import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


class Libro(models.Model):
    FORMATOS = [
        ('PDF', 'PDF'),
        ('EPUB', 'EPUB'),
    ]

    titulo = models.CharField(max_length=255)
    paginas = models.PositiveIntegerField()
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='libros',
    )
    archivo_formato = models.CharField(
        max_length=10,
        choices=FORMATOS,
        default='PDF',
    )
    descargas = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} ({self.autor.username})'

    def registrar_descarga(self):
        """Incrementa el contador de descargas como metrica de la publicacion (RN-EXP-05)."""
        self.descargas += 1
        self.save()

    def generar_contenido_descarga(self):
        """Genera un archivo PDF valido incluyendo metadatos de autoria original (RN-EXP-06)."""
        nombre_autor = self.autor.get_full_name() or self.autor.username
        fuente = "Biblioteca Digital"

        # Texto visible en el cuerpo del PDF
        lineas_texto = [
            f"Autor original: {nombre_autor}",
            f"Fuente: {fuente}",
            f"Titulo: {self.titulo}",
            f"Formato: {self.archivo_formato}",
        ]

        # Construccion de un PDF minimo valido segun la especificacion PDF 1.4
        texto_pagina = "  ".join(lineas_texto)
        stream = f"BT /F1 12 Tf 72 720 Td ({texto_pagina}) Tj ET"
        largo_stream = len(stream)

        objetos = []
        # 1 - Catalogo
        objetos.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
        # 2 - Paginas
        objetos.append("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj")
        # 3 - Pagina
        objetos.append(
            "3 0 obj\n<< /Type /Page /Parent 2 0 R "
            "/MediaBox [0 0 612 792] "
            "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj"
        )
        # 4 - Contenido
        objetos.append(
            f"4 0 obj\n<< /Length {largo_stream} >>\n"
            f"stream\n{stream}\nendstream\nendobj"
        )
        # 5 - Fuente
        objetos.append(
            "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj"
        )
        # 6 - Metadatos del documento
        objetos.append(
            f"6 0 obj\n<< /Author ({nombre_autor}) "
            f"/Title ({self.titulo}) "
            f"/Producer ({fuente}) >>\nendobj"
        )

        cuerpo = "\n".join(objetos)
        encabezado = "%PDF-1.4\n"

        # Tabla de referencias cruzadas
        offset = len(encabezado)
        offsets = []
        for obj in objetos:
            offsets.append(offset)
            offset += len(obj) + 1  # +1 por el salto de linea

        xref_inicio = offset
        xref = "xref\n"
        xref += f"0 {len(objetos) + 1}\n"
        xref += "0000000000 65535 f \n"
        for pos in offsets:
            xref += f"{pos:010d} 00000 n \n"

        trailer = (
            f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R /Info 6 0 R >>\n"
            f"startxref\n{xref_inicio}\n%%EOF"
        )

        return (encabezado + cuerpo + "\n" + xref + trailer).encode('latin-1')
