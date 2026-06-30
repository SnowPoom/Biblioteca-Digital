# language: es

Característica: Descubrimiento de recursos por recomendación contextual
  Como usuario de la biblioteca digital
  Quiero recibir sugerencias de libros y colecciones según mis intereses
  Para descubrir contenido relevante sin tener que buscarlo manualmente

  Antecedentes:
    Dado que el usuario ha iniciado sesión en la plataforma

  Escenario: Ver recomendaciones basadas en el historial de lectura
    Dado que el usuario tiene historial de lectura en una o más áreas temáticas
    Cuando el usuario accede a la sección de recomendaciones
    Entonces el sistema presenta libros y colecciones relacionados con las áreas que más ha explorado
    Y no aparece contenido que el usuario ya haya consumido

  Escenario: Las recomendaciones consideran métricas colectivas de actividad
    Dado que el usuario ha explorado contenido en la plataforma
    Cuando el usuario accede a la sección de recomendaciones
    Entonces el sistema incluye publicaciones con alto número de visualizaciones, republicaciones y descargas como señal de relevancia

  Escenario: Usuario sin actividad suficiente recibe recomendaciones generales
    Dado que el usuario no tiene historial de actividad suficiente en la plataforma
    Cuando el usuario accede a la sección de recomendaciones
    Entonces el sistema presenta el contenido de mayor consumo general de la plataforma

  Escenario: El contenido ya consumido no aparece entre las recomendaciones
    Dado que el usuario ha leído un libro previamente
    Cuando el usuario accede a la sección de recomendaciones
    Entonces ese libro no aparece entre las sugerencias

  Escenario: Descartar una recomendación la excluye de sugerencias futuras
    Dado que el usuario visualiza una recomendación en su sección
    Cuando el usuario descarta esa recomendación
    Entonces ese contenido no vuelve a aparecer en recomendaciones futuras

  Escenario: La actividad reciente tiene mayor peso en las recomendaciones
    Dado que el usuario tiene historial de lectura de períodos distintos
    Cuando el usuario accede a la sección de recomendaciones
    Entonces el sistema prioriza recomendaciones relacionadas con la actividad más reciente del usuario

  Esquema del escenario: Explorar recomendaciones filtrando por tipo de contenido
    Dado que el usuario se encuentra en la sección de recomendaciones
    Cuando el usuario filtra por <tipo_contenido>
    Entonces el sistema muestra únicamente sugerencias de <tipo_contenido>
    Y no aparece el otro tipo de contenido en esa vista

    Ejemplos:
      | tipo_contenido |
      | libros         |
      | colecciones    |
