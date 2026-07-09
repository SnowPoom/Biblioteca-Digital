# Estándares de Programación y Buenas Prácticas

Este documento define los lineamientos y estándares de codificación para el desarrollo de la plataforma. El objetivo principal es garantizar que el código sea legible, mantenible y escalable, facilitando la colaboración entre los miembros del equipo.

## 1. Convenciones de Nomenclatura

Se seguirá la convención de estilo oficial de Python, **PEP 8**, para todo el código base.

* **Variables y Funciones:** Se utilizará `snake_case` (minúsculas separadas por guiones bajos).
  * ✅ `libro_destacado = ...`
  * ✅ `def buscar_autor():`
  * ❌ `libroDestacado = ...`
* **Clases y Modelos (Django):** Se utilizará `PascalCase` (cada palabra inicia con mayúscula, sin guiones bajos). Los nombres de los modelos deben ir en singular.
  * ✅ `class RecursoEducativo(models.Model):`
  * ❌ `class recurso_educativo:` o `class Recursos:`
* **Consistencia de Idioma:** Se mantendrá un idioma consistente (español) para nombrar variables y modelar el dominio del negocio (`materiales`, `catalogo`). Se prohíbe estrictamente el uso de "Spanglish" (ej. ❌ `def get_libro_by_id():`).

## 2. Programación Orientada a Objetos (POO)

Dado que Django está fundamentado en POO, se deben aplicar sus principios para estructurar y organizar la lógica del sistema.

* **Encapsulamiento (El Modelo es dueño de sus datos):** La lógica de negocio intrínseca a una entidad debe residir en su respectivo modelo, no en las vistas. Por ejemplo, los cálculos sobre el estado de un objeto deben implementarse como métodos en `models.py` (ej. `def esta_vencido(self):`), permitiendo su reutilización en cualquier capa del sistema.
* **Herencia y Reutilización:** Se empleará la herencia para evitar la duplicación de código. Entidades con atributos compartidos (ej. `Libro`, `Revista`) deben heredar de una clase base abstracta común (ej. `Documento`).

## 3. Principios SOLID

La arquitectura del proyecto se guiará por los principios SOLID para prevenir el acoplamiento y facilitar el crecimiento del sistema:

* **S - Responsabilidad Única (Single Responsibility):** Cada clase, función o módulo debe tener un único propósito. Las vistas complejas que realizan múltiples acciones (ej. guardar datos, enviar correos y generar reportes) deben refactorizarse en funciones o servicios especializados de un solo propósito.
* **O - Abierto/Cerrado (Open/Closed):** Las entidades de software deben estar abiertas para extensión, pero cerradas para modificación. Se debe facilitar la adición de nuevas funcionalidades sin alterar el código existente.
* **DRY (Don't Repeat Yourself):** Se evitará la redundancia en el código. Los bloques de código repetidos deben abstraerse en funciones, clases o utilidades reutilizables.

## 4. Regla del Buen Explorador (Boy Scout Rule)

El equipo adoptará la regla de "dejar el código más limpio de lo que se encontró". Se fomenta la refactorización continua de problemas menores (espacios, comentarios desactualizados, errores tipográficos) directamente durante el desarrollo habitual, sin necesidad de crear tareas independientes.

## 5. Documentación y Comentarios

El código debe ser autoexplicativo mediante el uso de nombres descriptivos. Los comentarios se reservarán exclusivamente para explicar el *porqué* (reglas de negocio complejas, decisiones de diseño o atajos no triviales), evitando documentar el *qué* (lo que ya es evidente en el código).

* ❌ **Comentario redundante:**
  ```python
  # Filtra los libros por autor
  libros = Libro.objects.filter(autor="Gabriel")
  ```

* ✅ **Comentario explicativo (Regla de negocio):**
  ```python
  # Se excluyen los libros inactivos ya que se encuentran en revisión por el decanato
  libros = Libro.objects.filter(autor="Gabriel", estado="activo")
  ```

## 6. Arquitectura: Modelos Robustos, Vistas Ligeras (Fat Models, Skinny Views)

Las vistas (`views.py`) deben mantenerse concisas. Sus responsabilidades se limitan estrictamente a:
1. Recibir y procesar la petición HTTP (Request).
2. Delegar la lógica a modelos o servicios.
3. Retornar una respuesta adecuada (Response o Template).

Toda lógica de negocio compleja, algoritmos avanzados y consultas exhaustivas a la base de datos deben ser abstraídos hacia los modelos o capas de servicio correspondientes.

Adicionalmente, se debe respetar estrictamente el **Patrón MVT (Model-View-Template)** de Django para aislar responsabilidades:
* **Enrutamiento (`urls.py`):** Define el punto de entrada y delega a la vista correspondiente.
* **Controlador (`views.py`):** Intermedia entre los datos y la presentación.
* **Presentación (`templates/`):** Archivos HTML aislados (siempre ubicados en `templates/nombre_app/`).

## 7. Pruebas y Comportamiento (BDD)

Las especificaciones Gherkin en el directorio `features/` actúan como documentación viva del sistema. Deben redactarse desde la perspectiva del usuario final, sin detalles técnicos ni de implementación.

* ❌ **Escenario Acoplado a Implementación:** "Dado que hago clic en el `div` con id `#btn-submit` y espero un código HTTP 200..."
* ✅ **Escenario Orientado a Negocio:** "Dado que el estudiante presiona el botón de guardar..."

El desarrollo debe seguir el **Ciclo BDD (Behavior-Driven Development)** estructurado en 3 pasos:
1. **Definir el Comportamiento (Gherkin):** Redactar el escenario funcional en lenguaje claro en la carpeta `features/`.
2. **Implementar los Steps:** Traducir los pasos a pruebas automatizadas en `features/steps/`. La prueba debe fallar inicialmente.
3. **Escribir la Lógica (Django):** Desarrollar el código de la aplicación hasta que la prueba automatizada sea exitosa.

## 8. Seguridad y Limpieza de Código

* **Gestión de Secretos:** Queda estrictamente prohibido incluir información sensible (contraseñas, tokens de API, credenciales de bases de datos) en el código fuente. Se debe utilizar el archivo `.env` o gestores de secretos.
* **Exclusión de Archivos Locales (.gitignore):** Nunca se deben subir repositorios de entornos virtuales (`venv/`, `env/`) ni bases de datos locales (ej. `db.sqlite3`). El archivo `.gitignore` debe configurarse adecuadamente desde el inicio del proyecto.
* **Limpieza Previa a Commit:** Todo código de depuración (ej. sentencias `print()`, `console.log()`) debe ser eliminado antes de registrar los cambios, para mantener limpios y útiles los registros (logs) en producción.

## 9. Modo de Escritura

Se requiere un tono estrictamente profesional en el código base. Queda prohibido el uso de emojis tanto en el código fuente, como en comentarios y en mensajes de *commit*.

## 10. Convenciones de Control de Versiones (Git)

Para mantener un historial de cambios legible y automatizar la gestión de tareas (tableros Kanban), el equipo debe adherirse a las siguientes normas:

### 10.1. Nomenclatura de Ramas (Branches)
Nunca se debe trabajar directamente sobre la rama `main`. Las nuevas características o correcciones se desarrollan en ramas aisladas, nombradas en minúsculas y separadas por guiones bajo la estructura `tipo/numero-tarea-descripcion`:
* **Nuevas funcionalidades:** `feature/numero-descripcion` (Ej. `feature/5-buscador-autores`)
* **Corrección de errores:** `fix/numero-descripcion` (Ej. `fix/12-color-boton`)

### 10.2. Mensajes de Commit
Se utilizará un estándar adaptado, integrando la palabra clave para el cierre automatizado de *Issues*. El formato obligatorio es:
`tipo: descripción breve. PalabraClave #NumeroTarea`

Tipos permitidos:
* `feat:` Para nuevas funcionalidades.
* `fix:` Para soluciones a errores.
* `docs:` Para cambios en documentación.
* `test:` Para adición o modificación de pruebas (BDD).

Palabras clave para integración con el tablero (deben ir al final del mensaje):
* `Closes #123`, `Fixes #123`, `Resolves #123`.

**Ejemplo correcto:**
`feat: agregar buscador de libros por autor. Closes #5`

## 11. Estructura del Proyecto

```text
BIBLIOTECA/
├── config/              # Configuraciones globales del proyecto
├── docs/                # Documentación del sistema
├── features/            # Pruebas BDD (Archivos Gherkin)
├── src/                 # Código fuente principal
│   └── modulo/          # Aplicaciones / Módulos de Django
│   └── templates/       # Plantillas HTML
│       ├── index.html
│       └── modulo/  
├── static/              # Archivos estáticos (CSS, JS, Imágenes)
├── media/               # Archivos subidos por los usuarios
├── .env                 # Variables de entorno locales
├── .gitignore           # Archivos y directorios ignorados por Git
├── requirements.txt     # Dependencias de Python
└── manage.py            # Utilidad de línea de comandos de Django
```
