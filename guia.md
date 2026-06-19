# Guía de Trabajo Ágil - Plataforma Biblioteca Digital 📚

¡Bienvenidos al equipo! Para construir nuestra biblioteca digital de forma ordenada, rápida y sin pisarnos los talones, vamos a usar una metodología que conecta lo que el usuario necesita directamente con nuestro código.

Aquí está todo lo que necesitas saber para empezar a programar.

---

## 🛠️ 1. Nuestro Stack y Herramientas

* **Editor oficial:** Visual Studio Code (VS Code).
* **Lenguaje y Framework Web:** Python con Django.
* **Pruebas (BDD):** Behave + behave-django.
* **Control de versiones:** Git y GitHub.
* **Gestión de tareas:** GitHub Projects (Tablero Kanban).

### Extensiones obligatorias en VS Code:

1. **Python** (Microsoft)
2. **Cucumber (Gherkin) Full Support** (Para leer bien los escenarios BDD)

---

## 🚀 2. Nuestro Flujo de Trabajo (El Tablero Kanban)

No empezamos a programar a lo loco. Todo el trabajo sale de nuestro tablero en GitHub Projects.

1. **Tomar una tarea:** Ve a la columna `Backlog` o `Todo`, elige un *Issue* (ej. `#3 Búsqueda de libros`) y muévelo a la columna `In Progress`.
2. **Programar:** Haz tu magia en VS Code siguiendo el ciclo BDD (explicado abajo).
3. **Guardar y cerrar automáticamente:** Cuando termines y la prueba esté en verde, ve a la pestaña de Git en VS Code y escribe tu mensaje de commit usando la palabra mágica `Closes` más el número del Issue.
   * *Ejemplo:* `feat: crear buscador por autor. Closes #3`
4. **Subir (Push):** Al subirlo, GitHub cerrará el Issue por ti y moverá la tarjeta a `Done`.

---

## ⚙️ 3. ¿Cómo programamos aquí? (El Ciclo BDD)

Trabajamos de afuera hacia adentro. Primero definimos qué queremos que pase, luego hacemos la prueba, y al final escribimos el código web.

**Paso 1: Escribir el requerimiento (Gherkin)**
Vamos a la carpeta `features/` y escribimos el comportamiento en español plano y sencillo.

```gherkin
# language: es
Característica: Buscar libro
  Escenario: Búsqueda exitosa
    Dado que el estudiante está en el buscador
    Entonces debe ver el libro "Cálculo"
```


**Paso 2: Conectar con Python (Steps)**
En `features/steps/`, traducimos ese Gherkin a código de prueba usando palabras en inglés (`@given`, `@when`, `@then`). Ejecutamos `python manage.py behave` en la terminal. **La prueba fallará (rojo). Eso es bueno.**

**Paso 3: Escribir la lógica en Django**
Ahora sí vamos a nuestra app (ej. `materiales/`) y escribimos el código para que la prueba pase.

## 🏗️ 4. Arquitectura: Módulos y Páginas Nuevas

Para mantener el código ordenado, usamos la regla de la casa:

* El **Proyecto** (`biblioteca_digital`) es la casa completa. La carpeta `config/` es el pasillo principal.
* Las **Aplicaciones** (`materiales/`, `usuarios/`) son las habitaciones separadas. Si hacemos un sistema de foros nuevo, creamos una habitación nueva con `python manage.py startapp foros`.

### El ciclo de 3 pasos para crear una página nueva

Django usa el patrón MVT. Para que una página exista en el navegador, siempre necesitas estos 3 elementos (como en un restaurante):

1. **La Dirección (`urls.py`):** Le decimos al sistema qué ruta escribir (ej. `/catalogo`).
2. **El Cocinero (`views.py`):** Recibe la petición, busca los datos en la base de datos (Models) y decide qué mostrar.
3. **El Plato servido (`templates/`):** El archivo HTML final que ve el usuario. *(Nota: los archivos HTML siempre van dentro de una carpeta llamada `templates/nombre_de_la_app/`).*

## ⚠️ 5. Las Reglas de Oro del Equipo

1. **Lenguaje Simple:** Documentamos y escribimos los casos de uso para que los entienda cualquier persona. Evitemos términos hiper-técnicos o rebuscados en las descripciones del negocio.
2. **¡NO subas el entorno virtual!:** El archivo `.gitignore` es sagrado. Nunca debe subirse la carpeta `venv/`, ni la base de datos local `db.sqlite3`.
3. **La terminal integrada es tu amiga:** Usa `Ctrl + ñ` en VS Code para correr el servidor (`python manage.py runserver`) o las pruebas (`python manage.py behave`). Todo en una misma ventana.
4. **Si se rompe, pregunta:** Todos estamos aprendiendo. Si algo falla en el entorno virtual o Git, avisa al equipo antes de borrar cosas al azar. 

## 🤖 6. Guía de Commits y Magia en el Tablero (Automatización)

Para que nuestro tablero de GitHub se actualice solo (gracias a los *Workflows* automáticos) y no tengamos que arrastrar tarjetas a la columna de "Listo" manualmente, debemos escribir nuestros mensajes de guardado (*commits*) siguiendo una regla muy sencilla.

### La Fórmula del Commit Perfecto

Cada vez que vayas a guardar cambios en VS Code, tu mensaje debe tener esta estructura:

`tipo: qué hiciste de forma breve. PalabraMágica #NúmeroDeTarea`

**1. El Tipo (¿Qué estamos subiendo?)**
Usa una de estas palabras cortas al inicio para que todos sepamos de qué trata el cambio sin tener que revisar el código:

* `feat:` (Característica nueva) $\rightarrow$ *Ej: feat: crear página de catálogo*
* `fix:` (Arreglo de error) $\rightarrow$ *Ej: fix: corregir texto superpuesto en inicio*
* `docs:` (Documentación) $\rightarrow$ *Ej: docs: actualizar la guía del equipo*
* `test:` (Pruebas BDD) $\rightarrow$ *Ej: test: agregar escenarios Gherkin para buscador*

**2. La Palabra Mágica (Para cerrar tareas automáticamente)**
Para que GitHub detecte tu código y mueva la tarjeta a la columna de finalizado, **debes** usar una de estas palabras al final de tu mensaje, seguida de un espacio y el número exacto de tu tarea (*Issue*):

* `Closes #1` (La más común, "Cierra el número 1")
* `Fixes #2` ("Arregla el número 2", ideal para errores)
* `Resolves #3` ("Resuelve el número 3")

### Ejemplos Reales:

✅ **¡Perfecto!**
`feat: agregar buscador de libros por autor. Closes #5`
*(Esto sube el código y el sistema mueve automáticamente la tarjeta #5 a "Done").*

✅ **¡Perfecto!**
`fix: ajustar color del título en la página principal. Fixes #12`

❌ **Mal (No hará magia en el tablero)**
`subiendo el buscador de libros`
*(Falta el tipo, la palabra mágica y el número. El sistema no sabrá de qué tarea hablas y tendrás que mover la tarjeta a mano).*

### El flujo con ramas y Pull Requests

Si en el futuro trabajamos uniendo código a través de *Pull Requests*, nuestros *Workflows* también están configurados para detectar estas palabras mágicas. En cuanto el código se apruebe y se una al proyecto principal, la tarea se cerrará sola de forma inmediata.

## 🌿 7. El Uso de Ramas (Branches) y Pull Requests

Para evitar que la plataforma se rompa y asegurar que el trabajo de uno no borre el del otro, la regla de oro es: **nunca trabajamos ni guardamos cambios directamente en la rama `main`**.

Cada vez que tomes una tarea nueva del tablero, vas a crear una "rama". Piensa en una rama como un borrador seguro o un espacio de trabajo aislado donde puedes experimentar sin afectar la versión oficial del proyecto.

### ¿Cómo nombrar tu rama?

El nombre de tu rama debe decirle a cualquier compañero qué estás haciendo y a qué tarea del tablero pertenece, con solo un vistazo. Usa siempre letras minúsculas, sin espacios (usa guiones) y sigue este formato: `tipo/numero-tarea-descripcion-corta`.

* **Para funcionalidades nuevas:** Usa el prefijo `feature/`
  * *Ejemplo:* `feature/5-buscador-autores` (Estás haciendo la tarea #5, que es el buscador).
* **Para arreglar errores:** Usa el prefijo `fix/`
  * *Ejemplo:* `fix/12-color-boton` (Estás arreglando el botón de la tarea #12).

### El flujo de trabajo paso a paso en VS Code:

1. **Actualízate primero:** Antes de empezar cualquier tarea, asegúrate de estar en la rama `main` y haz clic en el botón de **Sincronizar cambios** (o ejecuta `git pull`). Esto descarga lo último que haya subido el resto del equipo.
2. **Crea tu rama:** En la esquina inferior izquierda de VS Code, haz clic donde dice `main`. Se abrirá un menú en la parte superior; elige **"Crear nueva rama"** (Create new branch) y escribe el nombre (ej. `feature/3-catalogo`).
3. **Programa tranquilo:** Escribe tu código, corre tus pruebas de Behave y haz tus *commits* con las reglas que ya aprendimos (ej. `feat: crear catálogo. Closes #3`).
4. **Sube tu rama:** En la pestaña de Git de VS Code, haz clic en **Publicar rama** (Publish branch) para que se suba a GitHub.

### Uniendo tu trabajo al proyecto oficial (Pull Requests)

Una vez que tu rama está subida a GitHub, no la mezclas tú mismo con el `main`. Vamos a trabajar en equipo:

1. Ve a la página de nuestro repositorio en GitHub. Verás un botón verde grande que dice **"Compare & pull request"**. Haz clic ahí.
2. Esto crea un "Pull Request" (PR), que es básicamente decirle al equipo: *"Chicos, terminé la tarea del catálogo, ¿alguien puede revisar que todo funcione bien?"*.
3. Un compañero leerá tu código rápidamente. Si todo está en orden, él presionará el botón de **"Merge"** (Unir).
4. ¡Listo! Tu código se une a `main` y, como usaste la palabra mágica en tu commit, la tarea se moverá sola a la columna de "Listo" en nuestro tablero.
