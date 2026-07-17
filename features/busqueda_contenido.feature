# language: es

Característica: Busqueda de contenido en la biblioteca
  Como usuario de la biblioteca digital
  Quiero buscar materiales, colecciones y usuarios
  Para encontrar recursos educativos de mi interes

  Antecedentes:
    Dado que el usuario ha iniciado sesión en la plataforma

  Escenario: Buscar material por nombre
    Dado que existen materiales publicados en la plataforma
    Cuando el usuario realiza una busqueda por el nombre de un material
    Entonces el sistema muestra los materiales cuyo titulo coincide con el termino buscado

  Escenario: Buscar por nombre de coleccion
    Dado que existen colecciones publicadas en la plataforma
    Cuando el usuario realiza una busqueda por el nombre de una coleccion
    Entonces el sistema muestra las colecciones cuyo nombre coincide con el termino buscado

  Escenario: Buscar por categoria
    Dado que existen materiales y colecciones asociados a categorias
    Cuando el usuario realiza una busqueda por el nombre de una categoria
    Entonces el sistema muestra los materiales y colecciones que pertenecen a esa categoria

  Escenario: Buscar material publicado por tipo de usuario
    Dado que existen materiales publicados por estudiantes y por profesores
    Cuando el usuario filtra la busqueda por rol de autor
    Entonces el sistema muestra unicamente los materiales publicados por usuarios con ese rol

  Escenario: Busqueda sin resultados
    Dado que existen materiales publicados en la plataforma
    Cuando el usuario realiza una busqueda con un termino que no coincide con ningun recurso
    Entonces el sistema informa que no se encontraron resultados
