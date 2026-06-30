# language: es

Característica: Seguimiento de actividad académica (Feed de seguimiento)
  Como usuario de la biblioteca digital
  Quiero ver en un feed el contenido publicado por los usuarios que sigo
  Para estar al día con los recursos de mi comunidad académica sin buscarlo activamente

  Antecedentes:
    Dado que el usuario ha iniciado sesión en la plataforma

  Escenario: Seguir a otro usuario
    Dado que el usuario está visitando el perfil público de otro usuario
    Cuando el usuario decide seguir a ese perfil
    Entonces el contenido que publique ese usuario comienza a aparecer en el feed de seguimiento

  Escenario: Dejar de seguir a un usuario elimina su contenido del feed de inmediato
    Dado que el usuario sigue a otro usuario cuyo contenido aparece en su feed
    Cuando el usuario deja de seguir a ese usuario
    Entonces el contenido de ese usuario desaparece del feed de seguimiento de forma inmediata

  Escenario: El feed de seguimiento muestra publicaciones en orden cronológico inverso
    Dado que el usuario sigue a uno o más usuarios que han publicado material recientemente
    Cuando el usuario accede al feed de seguimiento
    Entonces las publicaciones aparecen ordenadas de la más reciente a la más antigua

  Escenario: El feed de seguimiento no muestra contenido de usuarios no seguidos
    Dado que hay usuarios en la plataforma a los que el usuario no sigue
    Cuando el usuario accede al feed de seguimiento
    Entonces solo aparece contenido de los usuarios que sigue

  Esquema del escenario: Filtrar el feed de seguimiento por tipo de contenido
    Dado que el usuario accede al feed de seguimiento
    Cuando el usuario filtra por <tipo_contenido>
    Entonces el feed muestra únicamente <tipo_contenido> publicado por sus seguidos
    Y el otro tipo de contenido no aparece en esa vista

    Ejemplos:
      | tipo_contenido |
      | libros         |
      | colecciones    |

  Escenario: Una republicación en el feed preserva la autoría original
    Dado que un usuario seguido ha republicado contenido de un tercero
    Cuando el usuario accede al feed de seguimiento
    Entonces esa publicación aparece indicando quién la republicó
    Y la autoría original del contenido es visible

  Escenario: Cuando no hay seguidos ni publicaciones recientes se muestra el feed de recomendaciones
    Dado que el usuario no sigue a nadie o sus seguidos no tienen publicaciones recientes
    Cuando el usuario accede al feed de seguimiento
    Entonces el sistema muestra el feed de recomendaciones en su lugar

  Escenario: Acceder al detalle de una publicación desde el feed
    Dado que el usuario está revisando el feed de seguimiento
    Cuando el usuario selecciona una publicación
    Entonces el sistema lo redirige al detalle completo de ese libro o colección

  Escenario: Recibir notificación cuando alguien empieza a seguirte
    Dado que el usuario tiene un perfil público en la plataforma
    Cuando otro usuario comienza a seguirlo
    Entonces el usuario recibe una notificación informando quién lo empezó a seguir
