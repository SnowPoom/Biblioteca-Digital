# language: es

Característica: Gestión de permisos y visibilidad en colecciones
  Como administrador de una colección colaborativa
  Quiero controlar quién puede ver y participar en mi colección
  Para garantizar que el acceso y la edición estén bien organizados

  Antecedentes:
    Dado que estoy registrado en la plataforma
    Y he iniciado sesión en la aplicación
    Y soy el administrador de la colección "Recursos de Literatura"

  Escenario: Configurar la colección como pública
    Dado que estoy en la configuración de mi colección
    Cuando selecciono la visibilidad "Pública"
    Y guardo los cambios
    Entonces cualquier usuario de la plataforma puede encontrar y ver la colección
    Y los usuarios pueden solicitar unirse como colaboradores

  Escenario: Configurar la colección como privada
    Dado que estoy en la configuración de mi colección
    Cuando selecciono la visibilidad "Privada"
    Y guardo los cambios
    Entonces la colección solo es visible para los participantes actuales
    Y no aparece en los resultados de búsqueda generales

  Escenario: Solo el administrador puede cambiar la visibilidad de la colección
    Dado que soy un participante regular de la colección
    Cuando entro a la configuración de la colección
    Entonces no veo la opción de cambiar la visibilidad
    Y el sistema no me permite modificar ese ajuste

  Escenario: Ver qué puede hacer cada participante dentro de la colección
    Dado que soy el administrador de la colección
    Cuando voy a la lista de participantes
    Entonces puedo ver el rol y el índice de reputación de cada uno
    Y tengo opciones para gestionar su participación

  Escenario: Un participante retirado pierde acceso de edición
    Dado que retiré a un participante de la colección
    Cuando ese usuario intenta acceder a la colección
    Entonces ya no puede agregar ni editar libros dentro de ella
    Pero si la colección es pública aún puede verla como lector

  Escenario: El contenido aportado por un participante retirado se mantiene en la colección
    Dado que retiré al participante "Luisa Pérez" de la colección
    Y ella había agregado tres libros a la colección
    Cuando reviso el contenido de la colección
    Entonces los tres libros aportados por "Luisa Pérez" siguen en la colección
    Y el historial indica que ella los agregó originalmente
