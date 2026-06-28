# language: es

Característica: Anotación y enriquecimiento de material
  Como usuario que está leyendo un libro en la app
  Quiero poder agregar notas personales sobre fragmentos del contenido
  Para enriquecer mi experiencia de lectura y estudio

  Antecedentes:
    Dado que estoy registrado en la plataforma
    Y he iniciado sesión en la aplicación
    Y tengo abierto el libro "Introducción a la Filosofía"

  Escenario: Agregar una anotación sobre un fragmento de texto
    Dado que estoy leyendo una página del libro
    Cuando selecciono un fragmento de texto con el dedo
    Y toco la opción "Anotar"
    Y escribo "Este punto es clave para el examen"
    Y toco "Guardar"
    Entonces la anotación queda guardada sobre ese fragmento
    Y el texto queda visualmente resaltado en la página

  Escenario: Agregar una anotación sobre una imagen
    Dado que estoy en una página que tiene una imagen
    Cuando toco la imagen y elijo "Anotar imagen"
    Y escribo "Diagrama importante para la práctica"
    Y toco "Guardar"
    Entonces la anotación queda guardada sobre esa imagen

  Escenario: La anotación no puede superar los 150 caracteres
    Dado que seleccioné un fragmento de texto y abrí el campo de anotación
    Cuando escribo un texto de más de 150 caracteres
    Entonces el sistema no me permite ingresar más caracteres
    Y veo un indicador que muestra el límite alcanzado

  Escenario: Un fragmento solo puede tener una anotación activa
    Dado que ya tengo una anotación sobre un fragmento de texto
    Cuando selecciono ese mismo fragmento nuevamente
    Entonces el sistema me lleva directamente a editar la anotación existente
    Y no me permite crear una segunda anotación sobre el mismo fragmento

  Escenario: Las anotaciones persisten al cerrar y volver a abrir el libro
    Dado que tengo anotaciones guardadas en el libro
    Cuando cierro el libro y vuelvo a abrirlo más tarde
    Entonces todas mis anotaciones siguen apareciendo en los fragmentos correspondientes

  Escenario: Editar una anotación propia
    Dado que tengo una anotación guardada sobre un fragmento
    Cuando toco el fragmento resaltado y elijo "Editar anotación"
    Y cambio el texto de la nota
    Y toco "Guardar"
    Entonces la anotación queda actualizada

  Escenario: Eliminar una anotación propia
    Dado que tengo una anotación guardada sobre un fragmento
    Cuando toco el fragmento resaltado y elijo "Eliminar anotación"
    Y confirmo la acción
    Entonces la anotación desaparece
    Y el fragmento deja de estar resaltado

  Escenario: No puedo ver las anotaciones de otro usuario
    Dado que estoy leyendo un libro que también lee otro usuario
    Cuando navego por las páginas del libro
    Entonces solo veo mis propias anotaciones
    Y las notas del otro usuario no son visibles para mí en ningún momento

  Escenario: Las anotaciones se eliminan si el libro es retirado de la plataforma
    Dado que tengo anotaciones en un libro que fue retirado por su autor
    Cuando busco ese libro en mi historial
    Entonces el libro ya no está disponible
    Y las anotaciones asociadas a ese libro también han sido eliminadas
