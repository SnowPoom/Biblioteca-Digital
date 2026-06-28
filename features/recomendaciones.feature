# language: es

Característica: Descubrimiento de recursos por recomendación contextual
  Como usuario de la biblioteca digital
  Quiero recibir sugerencias de libros y colecciones según mis intereses
  Para descubrir contenido relevante sin tener que buscarlo manualmente

  Antecedentes:
    Dado que estoy registrado en la plataforma
    Y he iniciado sesión en la aplicación

  Escenario: Ver recomendaciones basadas en mi historial de lectura
    Dado que he leído varios libros de la categoría "Biología"
    Cuando entro a la sección de recomendaciones
    Entonces veo sugerencias de libros y colecciones relacionadas con "Biología"
    Y el contenido que ya leí no aparece entre las sugerencias

  Escenario: El contenido ya visto no aparece en las recomendaciones
    Dado que ya leí el libro "Ecología básica"
    Cuando reviso mis recomendaciones
    Entonces ese libro no aparece entre las sugerencias

  Escenario: Descartar una recomendación hace que no vuelva a aparecer
    Dado que veo una recomendación de un libro que no me interesa
    Cuando toco la opción "No me interesa" en esa sugerencia
    Entonces ese libro desaparece de mis recomendaciones
    Y no vuelve a aparecer en sesiones futuras

  Escenario: Usuario nuevo recibe recomendaciones generales
    Dado que soy un usuario nuevo sin historial de actividad
    Cuando entro a la sección de recomendaciones
    Entonces veo los libros y colecciones más populares de la plataforma
    Y las sugerencias no están personalizadas todavía

  Escenario: Las recomendaciones se actualizan con la actividad reciente
    Dado que acabo de leer varios libros de "Derecho Constitucional"
    Cuando regreso a la sección de recomendaciones
    Entonces las sugerencias reflejan ese interés reciente
    Y el contenido nuevo tiene más peso que el que leí hace mucho tiempo

  Escenario: Explorar recomendaciones de libros por separado
    Dado que estoy en la sección de recomendaciones
    Cuando selecciono el filtro "Solo libros"
    Entonces solo veo sugerencias de libros individuales
    Y no aparecen colecciones en esa vista

  Escenario: Explorar recomendaciones de colecciones por separado
    Dado que estoy en la sección de recomendaciones
    Cuando selecciono el filtro "Solo colecciones"
    Entonces solo veo sugerencias de colecciones
    Y no aparecen libros individuales en esa vista
