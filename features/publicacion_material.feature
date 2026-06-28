# language: es

Característica: Publicación de material educativo
  Como usuario autenticado de la biblioteca digital
  Quiero poder publicar mis propios libros y colecciones
  Para compartir mis recursos educativos con la comunidad académica

  Antecedentes:
    Dado que estoy registrado en la plataforma
    Y he iniciado sesión en la aplicación

  Escenario: Publicar un libro exitosamente
    Dado que estoy en la pantalla de creación de libro
    Y he escrito el título "Introducción al Álgebra Lineal"
    Y he subido una portada como imagen
    Y he agregado contenido de texto al libro
    Y he seleccionado la categoría "Matemáticas"
    Cuando toco el botón "Publicar"
    Entonces el sistema valida automáticamente el contenido
    Y el libro queda visible para la comunidad académica

  Escenario: No se puede publicar un libro sin portada
    Dado que estoy en la pantalla de creación de libro
    Y he escrito el título y el contenido del libro
    Pero no he subido ninguna imagen de portada
    Cuando toco el botón "Publicar"
    Entonces veo el mensaje "Debes subir una portada para poder publicar"
    Y el libro no se publica

  Escenario: No se puede publicar un libro sin texto
    Dado que estoy en la pantalla de creación de libro
    Y he subido la portada
    Pero el contenido del libro solo tiene imágenes sin texto
    Cuando toco el botón "Publicar"
    Entonces veo el mensaje "El libro debe tener contenido de texto"
    Y el libro no se publica

  Escenario: No se puede publicar un libro sin categoría
    Dado que estoy en la pantalla de creación de libro
    Y he llenado el título, portada y contenido del libro
    Pero no he seleccionado ninguna categoría
    Cuando toco el botón "Publicar"
    Entonces veo el mensaje "Debes seleccionar al menos una categoría"
    Y el libro no se publica

  Escenario: El libro no puede superar las 500 páginas
    Dado que estoy creando un libro
    Y el contenido del libro tiene más de 500 páginas
    Cuando intento publicarlo
    Entonces veo el mensaje "El libro no puede tener más de 500 páginas"
    Y el sistema no permite continuar hasta reducir el contenido

  Escenario: Editar los datos de un libro ya publicado
    Dado que tengo un libro publicado en mi perfil
    Cuando entro al libro y toco "Editar"
    Y cambio el título a "Álgebra Lineal Avanzada"
    Y toco "Guardar cambios"
    Entonces los datos del libro se actualizan de inmediato
    Y el contenido publicado sigue siendo visible

  Escenario: Editar el contenido de un libro ya publicado requiere nueva validación
    Dado que tengo un libro publicado en mi perfil
    Cuando entro al libro, toco "Editar" y modifico el contenido de texto
    Y toco "Guardar cambios"
    Entonces el libro queda en estado de revisión
    Y no es visible para otros usuarios hasta que pase la validación automática

  Escenario: Retirar un libro publicado
    Dado que tengo un libro publicado en mi perfil
    Cuando entro al libro y toco "Retirar publicación"
    Y confirmo la acción
    Entonces el libro deja de aparecer para otros usuarios
    Y solo yo puedo verlo desde mi perfil

  Escenario: No puedo editar el libro de otro usuario
    Dado que estoy viendo el libro de otro usuario
    Cuando intento acceder a la opción de editar
    Entonces no veo la opción "Editar" disponible
    Y el sistema no me permite realizar cambios

  Escenario: Republicar el material de otro usuario
    Dado que estoy viendo un libro publicado por otro usuario
    Cuando toco la opción "Republicar en mi perfil"
    Entonces el libro aparece en mi perfil
    Y la autoría original del otro usuario se conserva visible

  Escenario: Ver las métricas de mis publicaciones
    Dado que tengo al menos un libro publicado
    Cuando accedo al detalle de mi libro
    Entonces puedo ver el número de veces que fue visto
    Y cuántas veces fue republicado
    Y cuántas veces fue descargado

  Escenario: Publicar una colección sin categoría falla
    Dado que estoy creando una colección
    Y le he puesto un nombre y he agregado libros
    Pero no he seleccionado ninguna etiqueta de categoría
    Cuando toco "Publicar colección"
    Entonces veo el mensaje "La colección necesita al menos una categoría"
    Y la colección no se publica

  Escenario: Una colección puede tener hasta 20 libros
    Dado que tengo una colección con 20 libros
    Cuando intento agregar un libro más a la colección
    Entonces veo el mensaje "La colección ya alcanzó el límite de libros permitidos"
    Y el libro no se agrega

  Escenario: Eliminar un libro de una colección no lo borra de la biblioteca
    Dado que tengo una colección con un libro llamado "Física Cuántica"
    Cuando elimino ese libro de la colección
    Entonces el libro desaparece de la colección
    Pero sigue disponible para cualquier usuario en la biblioteca general
