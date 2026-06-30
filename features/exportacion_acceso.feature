# language: es

Característica: Exportación y acceso a material educativo
  Como usuario de la biblioteca digital
  Quiero descargar e imprimir libros desde la plataforma
  Para acceder al contenido sin necesidad de estar conectado

  Antecedentes:
    Dado que el usuario ha iniciado sesión en la plataforma

  Escenario: Descargar un libro dentro de la cuota disponible
    Dado que el usuario tiene cuota de páginas de descarga disponible en su cuenta
    Cuando el usuario descarga un libro
    Entonces el libro queda disponible para acceso sin conexión
    Y la cuota del usuario se reduce según el número de páginas descargadas

  Escenario: No se puede descargar si se agotó la cuota mensual
    Dado que el usuario ha agotado su cuota de descarga del ciclo actual
    Cuando el usuario intenta descargar un libro
    Entonces el sistema rechaza la operación
    Y el sistema informa la fecha en que se renueva la cuota

  Escenario: Publicar un libro incrementa la cuota de descarga mensual
    Dado que el usuario publica un libro exitosamente en la plataforma
    Entonces la cuota de descarga mensual del usuario aumenta en 100 páginas adicionales

  Esquema del escenario: Imprimir distintas porciones de un libro
    Dado que el usuario está visualizando un libro
    Cuando el usuario solicita imprimir <porcion>
    Entonces el sistema genera el documento correspondiente a <porcion> listo para impresión

    Ejemplos:
      | porcion           |
      | la página actual  |
      | un rango de páginas |
      | el libro completo |

  Escenario: El archivo descargado preserva la autoría original
    Dado que el usuario descarga un libro publicado por otro usuario
    Cuando el usuario abre el archivo descargado
    Entonces el archivo incluye el nombre del autor original y la fuente de la publicación

  Escenario: Cada descarga queda registrada como métrica de la publicación
    Dado que el usuario descarga un libro de la plataforma
    Cuando el autor del libro consulta las métricas de esa publicación
    Entonces el contador de descargas refleja la descarga realizada
