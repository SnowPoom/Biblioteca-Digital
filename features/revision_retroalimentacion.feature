# language: es

Característica: Sistema de revisión y retroalimentación entre pares
  Como participante de una colección colaborativa
  Quiero poder comentar y proponer cambios sobre el contenido de la colección
  Para mejorar el material de manera conjunta con mis compañeros

  Antecedentes:
    Dado que estoy registrado en la plataforma
    Y he iniciado sesión en la aplicación
    Y soy participante de la colección "Recursos de Física"

  Escenario: Dejar un comentario de retroalimentación sobre un libro de la colección
    Dado que estoy viendo el libro "Mecánica Clásica" dentro de la colección
    Cuando toco la opción "Dejar retroalimentación"
    Y escribo "Este libro cubre muy bien los fundamentos, pero le faltan ejercicios resueltos"
    Y toco "Enviar"
    Entonces mi comentario queda guardado
    Y todos los participantes de la colección pueden verlo

  Escenario: Los comentarios solo son visibles para los miembros de la colección
    Dado que hay comentarios de retroalimentación en la colección
    Cuando un usuario que no es miembro de la colección la encuentra en la biblioteca
    Entonces ese usuario no puede ver los comentarios internos de retroalimentación

  Escenario: Proponer incluir un nuevo libro en la colección
    Dado que estoy dentro de la colección "Recursos de Física"
    Cuando toco "Proponer un libro" y selecciono "Termodinámica Aplicada"
    Y toco "Enviar solicitud"
    Entonces el administrador recibe la solicitud de inclusión
    Y el libro no se agrega hasta que el administrador la apruebe

  Escenario: Proponer excluir un libro de la colección
    Dado que estoy dentro de la colección "Recursos de Física"
    Cuando toco el libro "Óptica Geométrica" y elijo "Proponer exclusión"
    Y escribo la razón "Este libro está desactualizado"
    Y toco "Enviar solicitud"
    Entonces el administrador recibe la solicitud de exclusión
    Y el libro permanece en la colección hasta que el administrador decida

  Escenario: El administrador aprueba una solicitud de cambio
    Dado que soy administrador de la colección y recibí una solicitud para incluir un libro
    Cuando entro a la sección de solicitudes pendientes y toco "Aprobar"
    Entonces el libro se agrega a la colección
    Y el cambio queda registrado en el historial de actividad

  Escenario: Un comentario con contenido inapropiado es rechazado
    Dado que estoy dejando retroalimentación sobre un libro de la colección
    Cuando escribo un comentario con lenguaje inapropiado y toco "Enviar"
    Entonces el sistema detecta el contenido y no permite publicar el comentario
    Y veo el mensaje "El contenido no cumple con las normas de la comunidad"

  Escenario: El historial de revisiones no puede ser eliminado
    Dado que hay comentarios y propuestas de cambio registradas en la colección
    Cuando intento eliminar un comentario del historial de revisiones
    Entonces el sistema no me permite borrarlo
    Y veo el mensaje "Los registros de revisión son permanentes"
