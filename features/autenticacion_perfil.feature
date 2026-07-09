# language: es

Característica: Autenticación y Perfil de Usuario
  Como usuario académico (estudiante o docente)
  Quiero registrarme e iniciar sesión en la plataforma
  Para acceder a las funcionalidades personalizadas de lectura y publicación

  Antecedentes:
    Dado que la plataforma de biblioteca digital está operativa

  Escenario: Registro exitoso con rol académico
    Dado que un visitante proporciona sus datos de autenticación básicos
    Y proporciona su nombre completo y un nickname
    Y selecciona obligatoriamente un rol académico
    Cuando el visitante completa el registro
    Entonces el sistema crea su cuenta exitosamente
    Y asigna el rol seleccionado a su perfil de usuario

  Escenario: Inicio de sesión exitoso
    Dado que un usuario académico está registrado en el sistema
    Cuando el usuario proporciona sus credenciales correctas
    Entonces el sistema le permite el acceso
    Y lo redirige a su panel personal

  # US-02: Recuperación de Contraseña
  Escenario: Solicitud de código de recuperación válida
    Dado que un usuario registrado requiere recuperar su contraseña
    Cuando el usuario solicita la recuperación de su cuenta
    Entonces el sistema genera un código de recuperación único
    Y envía el código al correo electrónico del usuario con una vigencia máxima de 24 horas

  Escenario: Uso de código de recuperación expirado
    Dado que un usuario posee un código de recuperación
    Pero el código ha superado su vigencia máxima de 24 horas o ya fue utilizado
    Cuando el usuario intenta utilizar el código
    Entonces el sistema rechaza la operación
    Y solicita que genere un nuevo código de recuperación
