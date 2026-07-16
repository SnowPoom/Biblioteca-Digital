# language: es

Característica: Coautoría y edición compartida de colecciones
  Como usuario de la biblioteca digital
  Quiero colaborar con otros en la construcción de colecciones
  Para crear recursos académicos de manera conjunta con mi comunidad

  Antecedentes:
    Dado que el usuario ha iniciado sesión en la plataforma

  Escenario: Invitar a un usuario a colaborar en una colección
    Dado que el usuario es administrador de una colección que no ha alcanzado el límite de participantes
    Cuando el usuario invita a otro usuario a colaborar en esa colección
    Entonces el usuario invitado recibe la invitación
    Y queda pendiente hasta que la acepte o rechace

  Escenario: Unirse a una colección por invitación
    Dado que el usuario ha recibido una invitación para unirse a una colección
    Cuando el usuario acepta la invitación
    Entonces pasa a ser participante de esa colección
    Y puede agregar libros y editar junto a los demás miembros

  Escenario: Solicitar unirse a una colección colaborativa
    Dado que el usuario está visualizando una colección colaborativa disponible
    Cuando el usuario solicita unirse a esa colección
    Entonces el administrador de la colección recibe la solicitud
    Y el usuario queda en espera hasta que sea aprobada o rechazada

  Escenario: El administrador aprueba una solicitud de ingreso
    Dado que el administrador de una colección tiene una solicitud de ingreso pendiente
    Cuando el administrador aprueba la solicitud
    Entonces el solicitante pasa a ser participante de la colección

  Escenario: El administrador rechaza una solicitud de ingreso
    Dado que el administrador de una colección tiene una solicitud de ingreso pendiente
    Cuando el administrador rechaza la solicitud
    Entonces el solicitante no obtiene acceso a la colección
    Y es notificado del rechazo

  Escenario: No se puede invitar a más participantes si se alcanzó el límite de 15
    Dado que el usuario es administrador de una colección que ya tiene 15 participantes
    Cuando el usuario intenta invitar a un nuevo colaborador
    Entonces el sistema rechaza la operación

  Escenario: Solo el administrador puede gestionar participantes
    Dado que el usuario es un participante regular de una colección
    Cuando el usuario intenta invitar, aceptar solicitudes o retirar participantes
    Entonces el sistema rechaza la operación

  Escenario: Cualquier participante puede agregar libros a la colección
    Dado que el usuario es participante de una colección que no ha alcanzado su límite de libros
    Cuando el usuario agrega un libro a la colección
    Entonces el libro queda registrado en la colección
    Y el cambio es visible para todos los participantes

  Escenario: Cualquier participante puede eliminar un libro de la colección
    Dado que el usuario es un participante de la colección y hay un libro en ella
    Cuando el usuario intenta eliminar ese libro de la colección
    Entonces la operación es exitosa


  Escenario: El rol de administrador pasa al colaborador más activo si el creador es eliminado
    Dado que el creador de una colección es eliminado de la plataforma
    Entonces el sistema asigna automáticamente el rol de administrador al participante con mayor índice de reputación de colaborador en esa colección
