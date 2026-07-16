# language: es

Característica: Publicación de material educativo
  Como usuario autenticado de la biblioteca digital
  Quiero publicar libros y colecciones propias en la plataforma
  Para compartir mis recursos educativos con la comunidad académica

  Antecedentes:
    Dado que el usuario ha iniciado sesión en la plataforma

  Escenario: Publicar un libro que supera la validación automática de contenido
    Dado que el usuario ha preparado un libro con título, portada, contenido textual y categoría
    Y el contenido es enriquecido, tiene sentido y guarda relación con la categoría
    Y las imágenes y la portada tienen relación con el contenido
    Cuando el usuario solicita publicar el libro
    Entonces el sistema valida el contenido automáticamente de forma exitosa
    Y el libro pasa a estado "Publicado" visible para la comunidad académica

  Escenario: Rechazo de publicación por contenido sin sentido
    Dado que el usuario ha preparado un libro cuyo texto carece de sentido o es texto de relleno
    Cuando el usuario solicita publicar el libro
    Entonces el sistema rechaza la validación automática
    Y el libro no pasa a estado "Publicado"
    Y se notifica al autor detallando que el contenido carece de sentido o no es enriquecido

  Escenario: Rechazo de publicación por falta de relación temática
    Dado que el usuario ha preparado un libro donde el contenido no está apegado a la categoría o el título no tiene relación con el contenido
    Cuando el usuario solicita publicar el libro
    Entonces el sistema rechaza la validación automática
    Y el libro no pasa a estado "Publicado"
    Y se notifica al autor detallando la falta de relación temática entre título, contenido y categoría

  Escenario: Rechazo de publicación por imágenes no relacionadas al contenido
    Dado que el usuario ha preparado un libro donde las imágenes o la portada no tienen relación con el contenido textual
    Cuando el usuario solicita publicar el libro
    Entonces el sistema rechaza la validación automática
    Y el libro no pasa a estado "Publicado"
    Y se notifica al autor detallando que las imágenes no son coherentes con el contenido

  Esquema del escenario: No se puede publicar un libro con requisitos incompletos
    Dado que el usuario está creando un libro sin <requisito_faltante>
    Cuando el usuario intenta publicar el libro
    Entonces el sistema rechaza la operación
    Y el libro no queda publicado

    Ejemplos:
      | requisito_faltante |
      | portada            |
      | contenido textual  |
      | categoría          |

  Escenario: No se puede publicar un libro compuesto únicamente por imágenes
    Dado que el usuario ha preparado un libro cuyo contenido consiste solo en imágenes sin texto
    Cuando el usuario intenta publicar el libro
    Entonces el sistema rechaza la operación
    Y el libro no queda publicado

  Escenario: No se puede publicar un libro que supera el límite de páginas
    Dado que el usuario ha preparado un libro que excede las 500 páginas
    Cuando el usuario intenta publicar el libro
    Entonces el sistema rechaza la operación
    Y el libro no queda publicado hasta que el contenido sea reducido

  Escenario: Editar los metadatos de un libro publicado requiere nueva validación
    Dado que el usuario tiene un libro publicado en su perfil
    Cuando el usuario modifica los metadatos del libro
    Entonces el libro pasa a estado Borrador
    Y deja de ser visible para otros usuarios hasta superar la validación automática

  Escenario: Editar el contenido de un libro publicado requiere nueva validación
    Dado que el usuario tiene un libro publicado en su perfil
    Cuando el usuario modifica el contenido textual del libro
    Entonces el libro pasa a estado Borrador
    Y deja de ser visible para otros usuarios hasta superar la validación automática

  Escenario: Retirar un libro publicado lo hace invisible para otros usuarios
    Dado que el usuario tiene un libro publicado en su perfil
    Cuando el usuario retira la publicación del libro
    Entonces el libro deja de estar disponible para el resto de la comunidad
    Y el libro deja de aparecer en el feed de los usuarios que siguen al autor
    Y el usuario puede seguir accediendo a él desde su propio perfil

  Escenario: Un usuario no puede editar el material publicado por otro
    Dado que el usuario está visualizando un libro publicado por otro usuario
    Cuando el usuario intenta modificar ese libro
    Entonces el sistema rechaza la operación

  Escenario: Republicar el material de otro usuario preserva la autoría original
    Dado que el usuario está visualizando un libro publicado por otro usuario
    Cuando el usuario republica ese libro en su perfil
    Entonces el libro aparece en el perfil del usuario como contenido republicado
    Y la autoría original del libro se conserva visible

  Escenario: El autor puede ver las métricas de sus publicaciones
    Dado que el usuario tiene al menos un libro publicado
    Cuando el usuario accede al detalle de ese libro
    Entonces puede consultar el número de visualizaciones, republicaciones y descargas

  Escenario: Un usuario distinto al autor no puede ver las métricas de un libro
    Dado que el usuario tiene al menos un libro publicado
    Cuando otro usuario distinto al autor accede al detalle de ese libro
    Entonces no puede consultar las métricas de visualizaciones, republicaciones y descargas

  Escenario: No se puede publicar una colección sin categoría
    Dado que el usuario ha preparado una colección con nombre y libros pero sin categoría
    Cuando el usuario intenta publicar la colección
    Entonces el sistema rechaza la operación
    Y la colección no queda publicada

  Escenario: Una colección no puede superar el límite de libros configurado
    Dado que una colección ha alcanzado su límite máximo de libros
    Cuando el usuario intenta agregar un libro más a esa colección
    Entonces el sistema rechaza la operación
    Y el libro no se agrega a la colección

  Escenario: Eliminar un libro de una colección no lo elimina de la biblioteca
    Dado que el usuario tiene una colección que contiene un libro
    Cuando el usuario elimina ese libro de la colección
    Entonces el libro desaparece de la colección
    Y el libro sigue disponible para cualquier usuario en la biblioteca general
