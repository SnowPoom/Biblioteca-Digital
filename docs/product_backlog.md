# Product Backlog — Biblioteca Digital

Este documento contiene el Product Backlog completo para la plataforma de Biblioteca Digital, estructurado a partir de los requerimientos y reglas de negocio identificados en las especificaciones del sistema.

El backlog está organizado por Épicas (basadas en las Capacidades del Negocio) y contiene historias de usuario detalladas con sus respectivos criterios de aceptación y prioridad.

---

## Índice de Épicas
1. Épica 1: Autenticación y Perfil de Usuario
2. Épica 2: Gestión de Material Educativo (Libros)
3. Épica 3: Anotaciones y Enriquecimiento de Lectura
4. Épica 4: Colecciones Colaborativas
5. Épica 5: Revisión y Retroalimentación entre Pares
6. Épica 6: Exportación y Sistema de Cuotas
7. Épica 7: Feed de Actividad Académica (Red Social)
8. Épica 8: Recomendaciones Contextuales

---

## Épica 1: Autenticación y Perfil de Usuario
Orientada a la gestión de accesos, roles académicos y configuración básica del perfil.

### [US-01] Registro e Inicio de Sesión con Roles Académicos
*   **Descripción:** Como usuario académico (estudiante o docente), quiero registrarme e iniciar sesión en la plataforma para acceder a las funcionalidades personalizadas de lectura y publicación.
*   **Criterios de Aceptación:**
    *   El usuario debe registrarse proporcionando datos de autenticación básicos.
    *   Debe seleccionarse obligatoriamente un rol académico: "Estudiante" o "Profesor" (almacenados en PerfilUsuario).
*   **Prioridad:** Alta
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-PUB-01

### [US-02] Recuperación de Contraseña
*   **Descripción:** Como usuario registrado, quiero recuperar mi contraseña de manera segura a través de un código único para restablecer el acceso a mi cuenta en caso de olvido.
*   **Criterios de Aceptación:**
    *   El sistema genera un código de recuperación único (UUID) enviado al usuario.
    *   El enlace/código tiene una vigencia máxima de 24 horas y solo puede utilizarse una vez.
*   **Prioridad:** Alta
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** N/A (Implementación base en app `login`)

---

## Épica 2: Gestión de Material Educativo (Libros)
Permite a los usuarios publicar y gestionar sus materiales de estudio originales.

### [US-03] Publicación de Libros Originales
*   **Descripción:** Como usuario autenticado, quiero publicar un libro original en la biblioteca para compartir mi contenido con la comunidad.
*   **Criterios de Aceptación:**
    *   El libro debe tener un título, portada (imagen obligatoria), contenido de texto (no se permiten libros solo con imágenes) y pertenecer a al menos una categoría temática.
    *   El libro no debe exceder las 500 páginas.
    *   Al guardarse para publicación, el estado inicial debe ser "Borrador" para validación automatizada.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-PUB-01, RN-PUB-03, RN-PUB-04, RN-PUB-05, RN-PUB-07

### [US-04] Validación Automatizada de Material
*   **Descripción:** Como administrador del sistema, quiero que todo material nuevo pase por un proceso automático de validación de contenido para garantizar la relevancia académica y adecuación del contenido.
*   **Criterios de Aceptación:**
    *   El libro pasa a estado "Publicado" (visible a la comunidad) únicamente si pasa la validación automática.
    *   Si no la supera, se notifica al autor.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-PUB-02

### [US-05] Edición de Metadatos y Contenido de Libros
*   **Descripción:** Como autor de un libro, quiero editar la información y el contenido de mi libro publicado para mantenerlo actualizado.
*   **Criterios de Aceptación:**
    *   Si el autor modifica el título, contenido, categoría o portada del libro, este vuelve automáticamente al estado "Borrador" (oculto a otros usuarios) hasta pasar la validación automática.
    *   Un usuario no puede editar el libro de otro usuario.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-PUB-08, RN-PUB-09, RN-PUB-11

### [US-06] Retiro de Publicaciones
*   **Descripción:** Como autor de un libro, quiero poder retirar (despublicar) mi material para que deje de estar visible para el resto de la comunidad.
*   **Criterios de Aceptación:**
    *   El libro retirado deja de mostrarse en la biblioteca general, búsquedas y feeds.
    *   El libro sigue disponible de manera privada únicamente para su autor.
    *   Al retirar el libro, se eliminan todas las anotaciones que otros usuarios hayan hecho en él.
*   **Prioridad:** Media
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-PUB-10, RN-PUB-11, RN-ANO-08

### [US-07] Republicar Material de Terceros
*   **Descripción:** Como usuario, quiero poder republicar en mi perfil un libro creado por otro autor para recomendarlo a mi red de contactos.
*   **Criterios de Aceptación:**
    *   La republicación no duplica el contenido (no crea una copia independiente en la base de datos).
    *   Se debe preservar y mostrar claramente la autoría original en el perfil y feed.
    *   Se incrementa en 1 el contador de republicaciones del libro original.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-PUB-12, RN-PUB-13

### [US-08] Visualización de Métricas de Actividad (Autor)
*   **Descripción:** Como autor, quiero ver las métricas de interacción de mis libros para saber el impacto de mis publicaciones en la comunidad.
*   **Criterios de Aceptación:**
    *   El autor (y solo él) puede ver el total acumulado de visualizaciones, descargas y republicaciones en el detalle de su material.
*   **Prioridad:** Media
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-PUB-13

---

## Épica 3: Anotaciones y Enriquecimiento de Lectura
Permite personalizar la experiencia de lectura a través de notas privadas.

### [US-09] Creación de Anotaciones Privadas en Texto o Imágenes
*   **Descripción:** Como lector de un libro, quiero seleccionar fragmentos de texto o imágenes para agregar anotaciones personales que faciliten mi estudio.
*   **Criterios de Aceptación:**
    *   Las anotaciones son estrictamente privadas; ningún otro usuario puede visualizarlas.
    *   El contenido de la anotación tiene un límite estricto de 150 caracteres.
    *   Un fragmento de texto o imagen específico puede tener un máximo de una anotación activa por usuario.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-ANO-01, RN-ANO-02, RN-ANO-03, RN-ANO-04

### [US-10] Visualización y Gestión de Anotaciones Guardadas
*   **Descripción:** Como lector, quiero ver las anotaciones resaltadas en el libro y poder editarlas o eliminarlas para mantener mis apuntes organizados.
*   **Criterios de Aceptación:**
    *   Los fragmentos anotados se muestran visualmente destacados durante la lectura.
    *   Al tocar un fragmento anotado, el usuario puede editar el texto o eliminar la anotación directamente.
    *   Las anotaciones persisten de manera indefinida entre sesiones de lectura.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-ANO-05, RN-ANO-06, RN-ANO-07

---

## Épica 4: Colecciones Colaborativas
Permite agrupar libros y trabajar en equipo para construir recursos académicos.

### [US-11] Creación y Configuración de Colecciones
*   **Descripción:** Como usuario, quiero crear colecciones de libros (individuales o colaborativas) para agrupar material académico por temática.
*   **Criterios de Aceptación:**
    *   Se requiere asignar al menos una categoría temática al publicar la colección.
    *   Se puede definir la visibilidad: "Pública" (visible en búsquedas para todos) o "Privada" (solo visible para participantes).
    *   El creador de la colección es el administrador inicial.
    *   La colección puede contener un límite máximo de libros ajustable (por defecto 20, mínimo 5).
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-PUB-14, RN-PUB-15, RN-COL-03, RN-COL-08, Características de Visibilidad

### [US-12] Gestión de Colaboradores (Invitaciones y Solicitudes)
*   **Descripción:** Como administrador de una colección colaborativa, quiero invitar a otros usuarios o aprobar solicitudes de unión para formar un grupo de trabajo.
*   **Criterios de Aceptación:**
    *   Una colección puede albergar un máximo de 15 participantes activos (incluido el administrador).
    *   Los usuarios se unen mediante invitación del administrador o aprobando solicitudes de acceso de terceros en colecciones públicas.
    *   Solo el administrador puede ver las opciones de invitar, aceptar solicitudes o retirar miembros.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-COL-01, RN-COL-02, RN-COL-03, RN-COL-05

### [US-13] Adición y Remoción de Libros en Colecciones
*   **Descripción:** Como colaborador de una colección, quiero agregar o remover libros para mantener actualizado el catálogo del grupo.
*   **Criterios de Aceptación:**
    *   Cualquier miembro activo puede agregar libros (respetando el límite máximo establecido).
    *   Solo el administrador o el participante específico que agregó un libro pueden eliminarlo de la colección.
    *   Eliminar un libro de una colección no lo borra de la biblioteca general.
*   **Prioridad:** Alta
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-PUB-16, RN-COL-08, RN-COL-09

### [US-14] Salida y Retiro de Participantes
*   **Descripción:** Como participante de una colección, quiero poder salir voluntariamente de ella; o como administrador, poder retirar a un participante inactivo.
*   **Criterios de Aceptación:**
    *   Un miembro puede abandonar la colección en cualquier momento perdiendo permisos de edición.
    *   El administrador puede retirar a un miembro. Su estado cambia a "retirado".
    *   Los libros aportados por el participante saliente o retirado permanecen en la colección.
*   **Prioridad:** Media
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-COL-05, RN-COL-06, RN-COL-07

### [US-15] Bitácora de Actividad de la Colección
*   **Descripción:** Como participante de una colección, quiero ver el historial de cambios realizados para estar al tanto de las contribuciones del equipo.
*   **Criterios de Aceptación:**
    *   El sistema registra automáticamente quién agregó/quitó un libro, quién entró/salió de la colección y cambios de configuración.
    *   La bitácora muestra la acción, autor y marca de tiempo, visible únicamente para miembros.
*   **Prioridad:** Media
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-COL-10

### [US-16] Traspaso de Administración por Baja de Usuario
*   **Descripción:** Como sistema, quiero transferir automáticamente el rol de administrador de una colección colaborativa si su creador es eliminado de la plataforma, garantizando la continuidad del recurso.
*   **Criterios de Aceptación:**
    *   Ante la eliminación del creador, el participante activo con mayor índice de reputación de colaborador se convierte en el nuevo administrador de la colección.
*   **Prioridad:** Baja
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-COL-03B

---

## Épica 5: Revisión y Retroalimentación entre Pares
Fomenta la validación de materiales de estudio dentro de equipos colaborativos.

### [US-17] Comentarios de Retroalimentación en Colecciones
*   **Descripción:** Como participante de una colección, quiero dejar comentarios sobre los libros incluidos para sugerir mejoras o validar su contenido.
*   **Criterios de Aceptación:**
    *   Los comentarios son visibles únicamente para los participantes de la colección (privados al público general).
    *   El texto del comentario pasa por el filtro automático de palabras inapropiadas.
    *   El historial de comentarios de retroalimentación es permanente; no puede ser eliminado por ningún usuario.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-REV-01, RN-REV-02, RN-REV-04, RN-REV-05

### [US-18] Solicitudes de Inclusión/Exclusión de Libros (Propuestas de Cambio)
*   **Descripción:** Como colaborador, quiero proponer la inclusión o exclusión de un libro específico mediante una propuesta formal para que el administrador la evalúe.
*   **Criterios de Aceptación:**
    *   El colaborador envía la propuesta indicando la acción (incluir/excluir) y el motivo (ej. "libro desactualizado").
    *   El libro no es alterado en la colección hasta que el administrador de la colección apruebe o rechace la solicitud.
    *   Las propuestas de cambio aprobadas o rechazadas forman parte del historial permanente de revisiones.
*   **Prioridad:** Media
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-REV-03, RN-REV-05

---

## Épica 6: Exportación y Sistema de Cuotas
Regula la descarga y uso offline del material didáctico.

### [US-19] Descarga de Libros dentro del Límite de Cuota
*   **Descripción:** Como lector, quiero descargar un libro para leerlo sin conexión a internet.
*   **Criterios de Aceptación:**
    *   La descarga es exitosa únicamente si la cantidad de páginas del libro no excede la cuota de descarga mensual disponible del usuario.
    *   La descarga reduce las páginas de la cuota disponible.
    *   El sistema registra la descarga como métrica del libro (esta métrica alimenta el contador de descargas del libro).
    *   Los archivos descargados (PDF/EPUB) incluyen de forma mandatoria los metadatos del autor original y la fuente.
*   **Prioridad:** Alta
*   **Estimación:** L
*   **Reglas de Negocio asociadas:** RN-EXP-01, RN-EXP-05, RN-EXP-06

### [US-20] Gestión y Renovación de Cuota de Descarga
*   **Descripción:** Como usuario, quiero que mi cuota de descarga se controle mensualmente y aumente por mis aportes para incentivar la participación.
*   **Criterios de Aceptación:**
    *   La cuota de descarga se renueva automáticamente cada 30 días restableciendo el cupo.
    *   Al intentar descargar sin cuota disponible, el sistema bloquea la acción y muestra un mensaje informativo indicando la fecha de renovación.
    *   Por cada libro en estado "Publicado" por el usuario, su cuota mensual aumenta en 100 páginas adicionales.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-EXP-02, RN-EXP-03

### [US-21] Descarga de Páginas o Libros Completos
*   **Descripción:** Como lector, quiero descargar una página, un rango o el libro completo para trabajar con material en físico.
*   **Criterios de Aceptación:**
    *   El lector puede elegir entre 3 opciones de descargar: "Solo la página actual", "Rango de páginas" o "Libro completo".
    *   El sistema genera un archivo optimizado para descarga respetando la selección.
*   **Prioridad:** Baja
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-EXP-04

---

## Épica 7: Feed de Actividad Académica (Red Social)
Mantiene a los usuarios al día con el contenido e interacciones de la comunidad a la que siguen.

### [US-22] Feed de Actividad Académica Ordenado Cronológicamente
*   **Descripción:** Como usuario, quiero visualizar un feed de publicaciones y republicaciones realizadas por los usuarios que sigo para enterarme de nuevos recursos.
*   **Criterios de Aceptación:**
    *   El feed muestra exclusivamente publicaciones/republicaciones de cuentas seguidas.
    *   El orden debe ser estrictamente cronológico, del más reciente al más antiguo.
    *   Las republicaciones deben indicar claramente quién las republicó y mostrar los metadatos de autoría original.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-FED-01, RN-FED-03, RN-FED-04

### [US-23] Filtros en el Feed de Actividad
*   **Descripción:** Como usuario, quiero filtrar el feed por tipo de contenido para focalizar mi lectura en libros o en colecciones específicas.
*   **Criterios de Aceptación:**
    *   Opciones de filtrado: "Solo libros" o "Solo colecciones".
    *   Ambos tipos de contenido no pueden visualizarse simultáneamente al aplicar filtros.
*   **Prioridad:** Media
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-FED-02

### [US-24] Sistema de Seguimiento (Follow / Unfollow)
*   **Descripción:** Como usuario, quiero poder seguir o dejar de seguir a otros perfiles para configurar mi red académica.
*   **Criterios de Aceptación:**
    *   Se puede seguir a cualquier usuario sin requerir aprobación.
    *   Al dejar de seguir, las publicaciones del usuario en cuestión desaparecen del feed de forma inmediata.
*   **Prioridad:** Alta
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-FED-05, RN-FED-06

### [US-25] Notificaciones de Seguimiento
*   **Descripción:** Como usuario, quiero recibir una notificación en la plataforma cuando otro usuario comience a seguirme para estar al tanto de mi audiencia.
*   **Criterios de Aceptación:**
    *   Al activarse la acción de seguir por parte de un usuario A sobre un usuario B, se genera y registra una notificación para el usuario B.
*   **Prioridad:** Baja
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-FED-09

---

## Épica 8: Recomendaciones Contextuales
Genera un flujo inteligente y dinámico para descubrir nuevos materiales educativos.

### [US-26] Recomendaciones Contextuales Personalizadas
*   **Descripción:** Como usuario recurrente, quiero recibir recomendaciones automáticas de libros y colecciones para descubrir material de mi interés.
*   **Criterios de Aceptación:**
    *   Las recomendaciones se basan en el historial de lectura, áreas exploradas y comportamiento colectivo (vistas, descargas y republicaciones de la comunidad).
    *   La actividad reciente del usuario tiene mayor peso que la antigua.
    *   Se excluyen automáticamente los contenidos ya consumidos por el usuario.
    *   Se puede visualizar el flujo de recomendaciones filtrando entre "Solo libros" y "Solo colecciones".
*   **Prioridad:** Media
*   **Estimación:** L
*   **Reglas de Negocio asociadas:** RN-REC-01, RN-REC-02, RN-REC-03, RN-REC-06, RN-REC-07, RN-REC-08

### [US-27] Recomendaciones para Nuevos Usuarios (Arranque en Frío)
*   **Descripción:** Como usuario nuevo en la plataforma, quiero ver sugerencias de contenido general al ingresar por primera vez para no encontrar secciones vacías.
*   **Criterios de Aceptación:**
    *   A falta de historial suficiente de lectura, el feed de recomendaciones muestra el contenido más consumido general de la plataforma (libros y colecciones con mayor número de visualizaciones y descargas).
    *   Este comportamiento se aplica también en el feed de seguimiento si el usuario no sigue a nadie o si sus seguidos no registran publicaciones.
*   **Prioridad:** Alta
*   **Estimación:** M
*   **Reglas de Negocio asociadas:** RN-REC-05, RN-FED-07, RN-FED-08

### [US-28] Descarte de Recomendaciones
*   **Descripción:** Como usuario, quiero poder marcar una recomendación como "No me interesa" para depurar mi feed y que el sistema no la sugiera nuevamente.
*   **Criterios de Aceptación:**
    *   Al descartar un libro o colección, este desaparece del feed de recomendaciones.
    *   El descarte se registra de forma permanente (se asocia a DescarteRecomendacion) para ajustar los algoritmos de recomendación futuros.
*   **Prioridad:** Media
*   **Estimación:** S
*   **Reglas de Negocio asociadas:** RN-REC-04
