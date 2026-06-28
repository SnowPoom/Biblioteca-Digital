# language: es

Característica: Seguimiento de actividad académica (Feed)
  Como usuario de la biblioteca digital
  Quiero ver en un feed lo que publican las personas que sigo
  Para estar al día con el contenido de mi comunidad académica

  Antecedentes:
    Dado que estoy registrado en la plataforma
    Y he iniciado sesión en la aplicación

  Escenario: Ver el feed con publicaciones de mis seguidos
    Dado que sigo a los usuarios "Ana García" y "Carlos López"
    Y ambos han publicado material recientemente
    Cuando entro a la sección de feed
    Entonces veo sus publicaciones ordenadas de la más reciente a la más antigua

  Escenario: El feed no muestra contenido de personas que no sigo
    Dado que hay usuarios en la plataforma que no sigo
    Cuando reviso mi feed
    Entonces solo aparece contenido de las personas que sigo
    Y no veo publicaciones de otros usuarios

  Escenario: Filtrar el feed para ver solo libros
    Dado que estoy en la sección de feed
    Cuando selecciono el filtro "Solo libros"
    Entonces el feed muestra únicamente los libros publicados por mis seguidos
    Y las colecciones no aparecen en esta vista

  Escenario: Filtrar el feed para ver solo colecciones
    Dado que estoy en la sección de feed
    Cuando selecciono el filtro "Solo colecciones"
    Entonces el feed muestra únicamente las colecciones de mis seguidos
    Y los libros individuales no aparecen en esta vista

  Escenario: Ver una republicación en el feed con la autoría original
    Dado que alguien que sigo republicó un libro de otro usuario
    Cuando reviso mi feed
    Entonces veo esa publicación indicando que fue republicada por la persona que sigo
    Y el nombre del autor original también aparece visible

  Escenario: Feed vacío cuando no sigo a nadie
    Dado que no sigo a ningún usuario todavía
    Cuando entro a la sección de feed
    Entonces veo el feed de recomendaciones generales de la plataforma
    Y no veo una pantalla vacía sin contenido

  Escenario: Feed vacío cuando mis seguidos no tienen publicaciones recientes
    Dado que sigo a usuarios que no han publicado nada recientemente
    Cuando entro a la sección de feed
    Entonces veo el feed de recomendaciones generales en lugar del feed vacío

  Escenario: Ir al detalle de una publicación desde el feed
    Dado que estoy revisando el feed y veo una publicación que me interesa
    Cuando toco esa publicación
    Entonces la app me lleva al detalle completo de ese libro o colección

  Escenario: Seguir a otro usuario
    Dado que estoy viendo el perfil de otro usuario
    Cuando toco el botón "Seguir"
    Entonces empiezo a seguir a ese usuario
    Y sus publicaciones empiezan a aparecer en mi feed

  Escenario: Dejar de seguir a un usuario elimina su contenido del feed de inmediato
    Dado que sigo a "María Torres" y su contenido aparece en mi feed
    Cuando entro a su perfil y toco "Dejar de seguir"
    Entonces las publicaciones de "María Torres" desaparecen de mi feed en ese momento

  Escenario: Recibir notificación cuando alguien empieza a seguirme
    Dado que soy usuario de la plataforma
    Cuando otro usuario toca "Seguir" en mi perfil
    Entonces recibo una notificación indicando que ese usuario empezó a seguirme
