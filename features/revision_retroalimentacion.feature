# language: es

Característica: Sistema de revisión y retroalimentación entre pares
  Como participante de una colección colaborativa
  Quiero comentar y proponer cambios sobre el contenido de la colección
  Para mejorar el material de manera conjunta con mis compañeros

  Antecedentes:
    Dado que el usuario ha iniciado sesión en la plataforma
    Y que el usuario es participante de una colección colaborativa

  Escenario: Dejar un comentario de retroalimentación sobre un libro de la colección
    Dado que el usuario está visualizando un libro dentro de la colección
    Cuando el usuario deja un comentario de retroalimentación sobre ese libro
    Entonces el comentario queda guardado
    Y todos los participantes de la colección pueden verlo

  Escenario: Los comentarios de retroalimentación no son visibles fuera de la colección
    Dado que una colección tiene comentarios de retroalimentación registrados
    Cuando un usuario que no es miembro de la colección accede a ella
    Entonces ese usuario no puede ver los comentarios internos

  Escenario: Proponer incluir un nuevo libro en la colección
    Dado que el usuario está dentro de una colección colaborativa
    Cuando el usuario propone incluir un libro mediante una solicitud de cambio
    Entonces el administrador recibe la solicitud
    Y el libro no se agrega hasta que el administrador la apruebe

  Escenario: Proponer excluir un libro de la colección
    Dado que el usuario está dentro de una colección colaborativa
    Cuando el usuario propone excluir un libro mediante una solicitud de cambio con su justificación
    Entonces el administrador recibe la solicitud
    Y el libro permanece en la colección hasta que el administrador tome una decisión

  Escenario: El administrador aprueba una solicitud de cambio
    Dado que el administrador tiene una solicitud de cambio pendiente en la colección
    Cuando el administrador aprueba la solicitud
    Entonces el cambio propuesto se aplica a la colección
    Y queda registrado en el historial de actividad

  Escenario: El administrador rechaza una solicitud de cambio
    Dado que el administrador tiene una solicitud de cambio pendiente en la colección
    Cuando el administrador rechaza la solicitud
    Entonces el contenido de la colección no se modifica
    Y el solicitante es notificado del rechazo

  Escenario: Un comentario con contenido inapropiado es rechazado por el sistema
    Dado que el usuario intenta dejar un comentario de retroalimentación con contenido inapropiado
    Cuando el usuario envía el comentario
    Entonces el sistema detecta el contenido y rechaza la operación
    Y el comentario no queda registrado en la colección

  Escenario: El historial de revisiones no puede ser eliminado
    Dado que existen comentarios y propuestas de cambio registradas en la colección
    Cuando un participante intenta eliminar un registro del historial de revisiones
    Entonces el sistema rechaza la operación
    Y el registro permanece en el historial
