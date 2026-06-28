# language: es

Característica: Coautoría y edición compartida de colecciones
  Como usuario de la biblioteca digital
  Quiero poder colaborar con otros en la construcción de colecciones
  Para crear recursos académicos de manera conjunta con mi comunidad

  Antecedentes:
    Dado que estoy registrado en la plataforma
    Y he iniciado sesión en la aplicación

  Escenario: Invitar a un usuario a colaborar en mi colección
    Dado que soy el administrador de la colección "Recursos de Química"
    Y la colección tiene menos de 15 participantes
    Cuando voy a la configuración de la colección y toco "Invitar colaborador"
    Y busco y selecciono al usuario "Pedro Martínez"
    Entonces se le envía una invitación a "Pedro Martínez"
    Y queda pendiente hasta que él la acepte

  Escenario: Unirse a una colección por invitación
    Dado que recibí una invitación para unirme a la colección "Recursos de Química"
    Cuando toco "Aceptar" en la notificación de invitación
    Entonces paso a ser participante de esa colección
    Y puedo empezar a agregar libros y editar junto a los demás

  Escenario: Solicitar unirse a una colección colaborativa
    Dado que estoy viendo una colección colaborativa pública
    Cuando toco "Solicitar unirme"
    Entonces el administrador de la colección recibe mi solicitud
    Y quedo en espera hasta que él la apruebe o rechace

  Escenario: Una colección no puede tener más de 15 participantes
    Dado que soy administrador de una colección que ya tiene 15 participantes
    Cuando intento invitar a un nuevo colaborador
    Entonces veo el mensaje "La colección ya alcanzó el límite de 15 participantes"
    Y no puedo enviar la invitación

  Escenario: Solo el administrador puede invitar y gestionar participantes
    Dado que soy un participante regular de una colección
    Cuando entro a la configuración de la colección
    Entonces no veo las opciones de invitar, aceptar solicitudes ni retirar participantes

  Escenario: Retirar a un participante de la colección
    Dado que soy el administrador de una colección
    Cuando voy a la lista de participantes y toco "Retirar" junto al nombre de un colaborador
    Y confirmo la acción
    Entonces ese participante pierde acceso de edición a la colección
    Pero los libros que aportó permanecen en la colección

  Escenario: Abandonar una colección voluntariamente
    Dado que soy participante de la colección "Historia Latinoamericana"
    Cuando voy a la configuración y toco "Abandonar colección"
    Y confirmo la acción
    Entonces dejo de ser participante de esa colección
    Y ya no puedo editar ni agregar libros en ella

  Escenario: Cualquier participante puede agregar libros a la colección
    Dado que soy participante de una colección colaborativa
    Y la colección no ha alcanzado su límite de libros
    Cuando toco "Agregar libro" dentro de la colección
    Y selecciono un libro de la biblioteca
    Entonces el libro queda agregado a la colección
    Y el cambio es visible para todos los participantes

  Escenario: Solo el administrador o quien agregó el libro puede eliminarlo de la colección
    Dado que soy un participante que no agregó el libro "Cálculo Diferencial"
    Y tampoco soy el administrador de la colección
    Cuando intento eliminar ese libro de la colección
    Entonces no veo la opción de eliminar disponible para ese libro

  Escenario: Todos los cambios quedan registrados en el historial de la colección
    Dado que soy participante de una colección
    Cuando un colaborador agrega un libro a la colección
    Entonces puedo ver ese cambio registrado en el historial de actividad
    Y el historial muestra quién realizó la acción y cuándo

  Escenario: El rol de administrador pasa al colaborador más activo si el creador es eliminado
    Dado que el creador de la colección "Recursos de Biología" fue eliminado de la plataforma
    Entonces el sistema asigna automáticamente el rol de administrador
    Al participante con mayor índice de reputación de colaborador en esa colección
