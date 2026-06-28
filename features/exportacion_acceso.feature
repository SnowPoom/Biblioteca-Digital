# language: es

Característica: Exportación y acceso a material educativo
  Como usuario de la biblioteca digital
  Quiero poder descargar e imprimir libros desde la app
  Para acceder al contenido sin necesidad de estar conectado

  Antecedentes:
    Dado que estoy registrado en la plataforma
    Y he iniciado sesión en la aplicación

  Escenario: Descargar un libro dentro de mi cuota disponible
    Dado que tengo cuota de descarga disponible en mi cuenta
    Cuando estoy viendo un libro y toco "Descargar"
    Entonces el libro se descarga en mi dispositivo
    Y mi cuota disponible se reduce según el número de páginas del libro

  Escenario: No puedo descargar si alcancé el límite mensual
    Dado que he agotado mi cuota de descarga del mes
    Cuando intento descargar un libro
    Entonces veo el mensaje "Alcanzaste tu límite de descargas este mes"
    Y se me informa la fecha en que se renueva mi cuota

  Escenario: Publicar un libro aumenta mi cuota de descarga
    Dado que tengo una cuota mensual base de descarga
    Cuando publico un libro exitosamente en la plataforma
    Entonces mi cuota de descarga mensual aumenta en 100 páginas adicionales

  Escenario: Imprimir solo la página que estoy viendo
    Dado que estoy leyendo la página 12 de un libro
    Cuando toco "Imprimir" y selecciono "Solo esta página"
    Entonces el sistema genera el documento listo para imprimir con solo esa página

  Escenario: Imprimir un rango de páginas del libro
    Dado que estoy en el detalle de un libro
    Cuando toco "Imprimir", selecciono "Rango de páginas" e ingreso de la página 5 a la 20
    Entonces el sistema genera el documento con ese rango de páginas para imprimir

  Escenario: Imprimir el libro completo
    Dado que estoy en el detalle de un libro
    Cuando toco "Imprimir" y selecciono "Libro completo"
    Entonces el sistema genera el documento completo listo para imprimir

  Escenario: El archivo descargado incluye la información del autor
    Dado que descargué un libro de otro usuario
    Cuando abro el archivo descargado
    Entonces veo el nombre del autor original
    Y la fuente de la publicación está indicada en el documento

  Escenario: La descarga queda registrada como métrica del libro
    Dado que descargué un libro de la plataforma
    Cuando el autor revisa las métricas de ese libro
    Entonces el número de descargas aumentó en uno
    Y esto se refleja sin importar si estaba dentro o fuera de mi cuota
