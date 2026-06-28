**Reglas de Negocio**

Biblioteca Digital — Especulación de Software

*Verificación y Validación de Software*

# Capacidad 1: Gestión de material y colecciones digitales originales

## Publicación de material educativo

Abarca la creación, edición, publicación y retiro de libros y colecciones dentro de la plataforma. El material publicado queda disponible para la comunidad académica y puede ser descubierto, consumido y republicado por otros usuarios.

| ID        | Regla de negocio                                                                                                                                                    |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RN-PUB-01 | Cualquier usuario autenticado, sea estudiante o docente, puede publicar material original en la plataforma.                                                         |
| RN-PUB-02 | Todo material publicado debe pasar por una validación automatizada de contenido apropiado y relevancia académica antes de quedar visible.                         |
| RN-PUB-03 | No se puede publicar un libro sin portada. La portada debe ser una imagen cargada por el autor.                                                                     |
| RN-PUB-04 | No se puede publicar un libro sin contenido textual. Un libro compuesto únicamente por imágenes no es válido.                                                    |
| RN-PUB-05 | Cada publicación puede tener un máximo de 500 páginas.                                                                                                           |
| RN-PUB-06 | Las publicaciones pueden incluir imágenes como contenido complementario al texto.                                                                                  |
| RN-PUB-07 | Un libro debe pertenecer al menos a una categoría temática al momento de su publicación.                                                                         |
| RN-PUB-08 | El autor puede editar los metadatos (título, descripción, categoría, portada) de un libro publicado en cualquier momento.                                        |
| RN-PUB-09 | Si el autor edita el contenido de un libro ya publicado, el material debe volver a pasar la validación automatizada antes de ser visible.                          |
| RN-PUB-10 | El autor puede retirar (despublicar) su propio material en cualquier momento; el material retirado deja de ser visible para otros usuarios.                         |
| RN-PUB-11 | Un usuario no puede editar ni eliminar material publicado por otro usuario.                                                                                         |
| RN-PUB-12 | Cualquier usuario puede republicar material de otro usuario en su propio perfil. La republicación preserva la autoría original y no crea una copia independiente. |
| RN-PUB-13 | El sistema registra métricas de actividad por publicación: número de visualizaciones, republicaciones y descargas. Estas métricas son visibles para el autor.   |
| RN-PUB-14 | Cada colección debe tener asignada al menos una etiqueta de categoría temática antes de ser publicada.                                                           |
| RN-PUB-15 | Una colección puede contener un máximo de 20 libros. El creador de la colección puede ajustar este límite, pero nunca por debajo de 5 libros.                   |
| RN-PUB-16 | Eliminar un libro de una colección no lo elimina de la biblioteca general.                                                                                         |

## Anotación y enriquecimiento de material

Permite a cualquier usuario crear anotaciones personales vinculadas a fragmentos específicos de texto o imágenes dentro de un libro. Las anotaciones son estrictamente privadas y forman parte del material enriquecido del usuario.

| ID        | Regla de negocio                                                                                                                                                                                      |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RN-ANO-01 | Las anotaciones son personales e intransferibles. Ningún otro usuario puede ver las anotaciones de otro, independientemente de sus permisos sobre el libro.                                          |
| RN-ANO-02 | Una anotación se crea seleccionando un fragmento de texto en el libro y eligiendo la opción de anotar. En el caso de imágenes, se puede optar por añadir una anotación sobre la imagen completa. |
| RN-ANO-03 | El contenido de una anotación tiene un límite máximo de 150 caracteres.                                                                                                                            |
| RN-ANO-04 | Un fragmento de texto puede tener como máximo una anotación activa. Para modificarla, el usuario debe editar la anotación existente.                                                               |
| RN-ANO-05 | Los fragmentos anotados deben mostrarse visualmente diferenciados en la página para que el usuario identifique rápidamente sus anotaciones.                                                         |
| RN-ANO-06 | El usuario puede editar o eliminar cualquiera de sus propias anotaciones en cualquier momento.                                                                                                        |
| RN-ANO-07 | Las anotaciones persisten entre sesiones. Si el usuario cierra y vuelve a abrir el libro, sus anotaciones siguen disponibles.                                                                         |
| RN-ANO-08 | Si un libro es eliminado de la plataforma, las anotaciones asociadas a ese libro se eliminan también.                                                                                                |

# Capacidad 2: Exploración de material educativo digital

## Descubrimiento de recursos por recomendación contextual

El sistema analiza la actividad de cada usuario (historial de lectura, interacciones, descargas) y el comportamiento de usuarios con intereses similares para generar recomendaciones personalizadas de libros y colecciones.

| ID        | Regla de negocio                                                                                                                                                                                   |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RN-REC-01 | Las recomendaciones se generan considerando el historial de lectura del usuario, las áreas temáticas exploradas y sus interacciones previas como señales primarias.                             |
| RN-REC-02 | Las métricas de actividad colectiva de cada publicación (número de visualizaciones, republicaciones y descargas) se usan como señales de relevancia para determinar qué contenido recomendar. |
| RN-REC-03 | El contenido que el usuario ya ha consumido no debe aparecer entre las recomendaciones.                                                                                                            |
| RN-REC-04 | Si el usuario descarta una recomendación, ese contenido no debe volver a recomendarse. La señal negativa queda registrada para ajustar recomendaciones futuras.                                  |
| RN-REC-05 | Un usuario sin actividad suficiente recibe recomendaciones basadas en el contenido de mayor consumo general de la plataforma (arranque en frío).                                                  |
| RN-REC-06 | Las recomendaciones se actualizan de forma dinámica conforme el usuario interactúa con la plataforma.                                                                                            |
| RN-REC-07 | El sistema diferencia entre recomendaciones de libros y recomendaciones de colecciones; el usuario puede explorar ambos tipos por separado.                                                        |
| RN-REC-08 | La actividad reciente del usuario tiene mayor peso que la actividad antigua al determinar las recomendaciones, para reflejar sus intereses actuales.                                               |

## Exportación y acceso

Permite a los usuarios descargar e imprimir material para acceso offline. La plataforma establece límites de exportación para garantizar un uso equitativo y fomentar la contribución activa.

| ID        | Regla de negocio                                                                                                                                                                        |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RN-EXP-01 | Un usuario puede descargar libros disponibles en la plataforma dentro de los límites establecidos por su cuota de descarga, medida en número de páginas descargadas.                 |
| RN-EXP-02 | La cuota de descarga se renueva cada 30 días. Al alcanzar el límite dentro de ese ciclo, el usuario debe esperar al siguiente período o incrementar su cuota mediante contribución. |
| RN-EXP-03 | Por cada libro publicado por el usuario, su cuota de descarga mensual se incrementa en 100 páginas adicionales.                                                                        |
| RN-EXP-04 | Un usuario puede solicitar imprimir un libro completo, un rango de páginas o únicamente la página que está visualizando.                                                            |
| RN-EXP-05 | El sistema registra cada descarga como métrica de actividad de la publicación, independientemente de si el usuario alcanza o no su límite.                                           |
| RN-EXP-06 | La exportación respeta la autoría original: los archivos generados incluyen los metadatos del autor y la fuente de la publicación.                                                   |

## Seguimiento de actividad académica (Feed)

Proporciona al usuario un flujo cronológico de publicaciones y republicaciones realizadas por los usuarios que sigue, funcionando como una red social académica centrada en el contenido educativo.

| ID        | Regla de negocio                                                                                                                                                                 |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RN-FED-01 | El feed de seguimiento muestra exclusivamente publicaciones y republicaciones de los usuarios que el usuario sigue, ordenadas cronológicamente de más reciente a más antigua. |
| RN-FED-02 | El usuario puede explorar el feed filtrando por tipo de contenido: solo libros o solo colecciones. Ambos tipos no se muestran simultáneamente.                                  |
| RN-FED-03 | Cuando un usuario seguido republica contenido de un tercero, el feed de seguimiento lo muestra indicando quién lo republicó y preservando la autoría original.                |
| RN-FED-04 | El feed de seguimiento no muestra contenido de usuarios que el usuario no sigue, sin excepción.                                                                                 |
| RN-FED-05 | Un usuario puede seguir a cualquier otro usuario de la plataforma sin necesidad de aprobación.                                                                                  |
| RN-FED-06 | Un usuario puede dejar de seguir a otro en cualquier momento. Al hacerlo, el contenido de ese usuario desaparece del feed de seguimiento de forma inmediata.                     |
| RN-FED-07 | Si el usuario no sigue a nadie, o sus seguidos no tienen publicaciones recientes, se muestra únicamente el feed de recomendaciones.                                             |
| RN-FED-08 | Desde el feed, el usuario puede acceder directamente al detalle de cualquier publicación mostrada.                                                                              |
| RN-FED-09 | El sistema notifica al usuario cuando alguien empieza a seguirlo.                                                                                                                |

# Capacidad 3: Colaboración en colecciones

## Coautoría y edición compartida de colecciones

Permite que múltiples usuarios colaboren en la construcción y mantenimiento de una colección compartida. La participación se rige por invitación o solicitud, y la permanencia en el grupo depende del nivel de contribución activa.

| ID         | Regla de negocio                                                                                                                                                               |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| RN-COL-01  | Una colección colaborativa puede tener un máximo de 15 participantes, incluyendo al creador.                                                                                 |
| RN-COL-02  | Un usuario puede unirse a una colección colaborativa solo mediante invitación del creador/administrador o mediante solicitud aprobada por este.                              |
| RN-COL-03  | El creador de la colección tiene el rol de administrador y es el único que puede invitar, aceptar solicitudes, asignar roles y retirar participantes.                        |
| RN-COL-03B | Si el creador de la colección es eliminado de la plataforma, el rol de administrador pasa automáticamente al participante con mayor índice de reputación de colaborador.   |
| RN-COL-04  | Cada participante tiene un índice de reputación de colaborador calculado en función de sus contribuciones activas (libros añadidos, ediciones, revisiones).                |
| RN-COL-05  | El administrador puede retirar a un participante de la colección, por ejemplo para dar lugar a otro colaborador más activo. El retiro es definitivo salvo nueva invitación. |
| RN-COL-06  | Un participante retirado pierde acceso de edición a la colección, pero el contenido que aportó permanece en ella salvo decisión del administrador.                         |
| RN-COL-07  | Un participante puede abandonar voluntariamente una colección en cualquier momento.                                                                                           |
| RN-COL-08  | Todos los participantes pueden añadir libros a la colección, sujeto al límite máximo configurado de libros por colección.                                                 |
| RN-COL-09  | Solo el administrador o el participante que añadió un libro puede eliminarlo de la colección.                                                                               |
| RN-COL-10  | Los cambios realizados por cualquier participante quedan registrados en un historial de actividad de la colección, visible para todos los miembros.                           |

## Sistema de revisión y retroalimentación entre pares

Permite que los participantes de una colección comenten y propongan cambios sobre el contenido incluido, promoviendo la mejora colectiva y la validación académica entre pares.

| ID        | Regla de negocio                                                                                                                                                    |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RN-REV-01 | Cualquier participante de una colección puede dejar comentarios de retroalimentación sobre los libros incluidos en ella.                                          |
| RN-REV-02 | Los comentarios de retroalimentación son visibles para todos los miembros de la colección, no para el público general.                                           |
| RN-REV-03 | Un participante puede proponer la inclusión o exclusión de un libro mediante una solicitud de cambio. Esta solicitud requiere aprobación del administrador.      |
| RN-REV-04 | Los comentarios de retroalimentación no pueden contener contenido inapropiado. El sistema aplica la misma validación automatizada que para el material publicado. |
| RN-REV-05 | El historial de revisiones y retroalimentación es permanente y no puede ser eliminado.                                                                             |
