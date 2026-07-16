# language: es

Característica: Exportación y acceso a material educativo
  Como usuario de la biblioteca digital
  Quiero descargar e imprimir libros desde la plataforma
  Para acceder al contenido sin necesidad de estar conectado

  Antecedentes:
    Dado que el usuario ha iniciado sesión en la plataforma

  Escenario: Descargar un libro exitosamente dentro de la cuota
    Dado que el usuario tiene una cuota de descarga mensual disponible
    Y la cantidad de páginas del libro no excede dicha cuota
    Cuando el usuario descarga un libro
    Entonces el libro queda disponible para acceso sin conexión
    Y la cuota del usuario se reduce según el número de páginas descargadas

  Escenario: Rechazo de descarga cuando el libro excede la cuota mensual disponible
    Dado que el usuario tiene una cuota de descarga mensual disponible
    Pero la cantidad de páginas del libro excede su cuota restante
    Cuando el usuario intenta descargar un libro
    Entonces el sistema rechaza la operación
    Y el sistema le informa que no tiene suficientes páginas en su cuota

  Escenario: Publicar un libro incrementa la cuota de descarga mensual
    Dado que el usuario publica un libro exitosamente en la plataforma
    Entonces la cuota de descarga mensual del usuario aumenta en 100 páginas adicionales

  Esquema del escenario: Descargar distintas porciones de un libro
    Dado que el usuario está visualizando un libro
    Cuando el usuario solicita descargar <porcion>
    Entonces el sistema genera el documento correspondiente a <porcion> listo para impresión

    Ejemplos:
      | porcion           |
      | la página actual  |
      | un rango de páginas |
      | el libro completo |

  Escenario: El archivo descargado en PDF/EPUB preserva la autoría original
    Dado que el usuario descarga un libro publicado por otro usuario en formato PDF o EPUB
    Cuando el usuario abre el archivo descargado
    Entonces el archivo incluye de forma mandatoria el nombre del autor original y la fuente de la publicación
