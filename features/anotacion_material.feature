# language: es

Característica: Anotación y enriquecimiento de material
  Como usuario que está leyendo un libro en la plataforma
  Quiero agregar notas personales sobre fragmentos del contenido
  Para enriquecer mi experiencia de lectura con anotaciones propias

  Antecedentes:
    Dado que el usuario ha iniciado sesión en la plataforma
    Y que el usuario ha abierto un libro disponible en la biblioteca

  Escenario: Crear una anotación sobre un fragmento de texto
    Dado que el usuario está leyendo una página del libro
    Cuando el usuario selecciona un fragmento de texto y elige anotarlo
    Y escribe el contenido de la anotación
    Entonces la anotación queda asociada a ese fragmento
    Y el fragmento se muestra visualmente diferenciado en la página

  Escenario: Crear una anotación sobre una imagen
    Dado que el usuario está en una página que contiene una imagen
    Cuando el usuario elige anotar esa imagen
    Y escribe el contenido de la anotación
    Entonces la anotación queda asociada a esa imagen

  Escenario: No se puede guardar una anotación que supera el límite de caracteres
    Dado que el usuario ha abierto el campo de anotación sobre un fragmento
    Cuando el usuario intenta ingresar un texto que supera los 150 caracteres
    Entonces el sistema no permite continuar ingresando texto
    Y se indica visualmente que se alcanzó el límite

  Escenario: Un fragmento con anotación existente no permite crear una segunda
    Dado que el usuario tiene una anotación guardada sobre un fragmento de texto
    Cuando el usuario selecciona ese mismo fragmento para anotar nuevamente
    Entonces el sistema lleva al usuario a editar la anotación existente
    Y no permite crear una anotación adicional sobre el mismo fragmento

  Escenario: Las anotaciones persisten entre sesiones
    Dado que el usuario tiene anotaciones guardadas en un libro
    Cuando el usuario cierra el libro y vuelve a abrirlo en una sesión posterior
    Entonces todas las anotaciones siguen visibles en los fragmentos correspondientes

  Escenario: Editar una anotación existente
    Dado que el usuario tiene una anotación guardada sobre un fragmento
    Cuando el usuario accede a esa anotación y modifica su contenido
    Entonces la anotación refleja el contenido actualizado
    Y el fragmento permanece visualmente diferenciado

  Escenario: Eliminar una anotación propia
    Dado que el usuario tiene una anotación guardada sobre un fragmento
    Cuando el usuario elimina esa anotación
    Entonces la anotación desaparece del sistema
    Y el fragmento deja de estar visualmente diferenciado

  Escenario: Las anotaciones de un usuario no son visibles para otros
    Dado que el usuario tiene anotaciones guardadas en un libro
    Cuando otro usuario accede al mismo libro
    Entonces ese usuario no puede ver las anotaciones del primero

  Escenario: Las anotaciones se eliminan cuando el libro es retirado de la plataforma
    Dado que el usuario tiene anotaciones en un libro
    Cuando ese libro es retirado de la plataforma por su autor
    Entonces las anotaciones asociadas a ese libro son eliminadas del sistema

  Esquema del escenario: Crear anotaciones en distintos libros y fragmentos
    Dado que el usuario está visualizando <nombre_libro>
    Cuando el usuario selecciona <fragmento_texto> y escribe la anotación <contenido_anotacion>
    Entonces la anotación queda asociada a <fragmento_texto> en <nombre_libro>

    Ejemplos:
      | nombre_libro              | fragmento_texto     | contenido_anotacion                     |
      | Introducción a la Química | reacción exotérmica | Libera energía al entorno               |
      | Cálculo Diferencial       | derivada parcial    | Variación respecto a una variable       |
      | Historia Universal        | Revolución Francesa | Contexto socioeconómico del siglo XVIII |
