# Guía de Trabajo Ágil - Plataforma Biblioteca Digital 📚

¡Bienvenidos al equipo! Esta guía rápida está diseñada para ayudarte a configurar tu entorno y entender nuestro flujo de trabajo diario. 

> **Nota:** Para reglas técnicas detalladas sobre arquitectura, nomenclatura de ramas, formato de commits y metodologías, consulta nuestro archivo de [Estándares de Programación](docs/estandares_programacion.md).

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

## 🚀 2. El Flujo de Trabajo Diario (Tablero Kanban y Git)

Todo nuestro trabajo está impulsado por el tablero en GitHub Projects. Sigue siempre estos pasos:

### Paso 1: Tomar una Tarea
1. Ve a nuestro Tablero Kanban.
2. En la columna `Backlog` o `Todo`, elige un *Issue* (ej. `#3 Búsqueda de libros`).
3. Muévelo a la columna `In Progress`.

### Paso 2: Preparar tu Entorno (VS Code)
1. **Actualízate:** Asegúrate de estar en la rama `main` y sincroniza los cambios (`git pull`) para tener lo último del equipo.
2. **Crea tu Rama:** Crea una nueva rama para trabajar siguiendo el estándar de nomenclatura (`feature/numero-tarea` o `fix/numero-tarea`). *(Ver [Estándares de Programación](docs/estandares_programacion.md) para más detalles).*

### Paso 3: Programar
Utiliza la terminal integrada de VS Code (`Ctrl + ñ`):
* **(Opcional) Crear un nuevo módulo/app:** Si tu tarea requiere construir una sección completamente nueva desde cero, el primer paso antes de programar es generar la aplicación en Django ejecutando: `python manage.py startapp nombre_del_modulo`
* Arranca el servidor local: `python manage.py runserver`
* Ejecuta tus pruebas BDD: `python manage.py behave`

Programa siguiendo el ciclo **BDD (Behavior-Driven Development)** y respetando la arquitectura **MVT** de Django tal como se especifica en los estándares.

### Paso 4: Subir los Cambios (Commits Mágicos)
Aprovechamos la automatización de GitHub para que el tablero se actualice solo.
1. Al hacer tus *commits*, utiliza el formato obligatorio (ej. `feat: agregar buscador. Closes #3`).
2. Sube tu rama a GitHub (`Publish branch`).

### Paso 5: Revisión y Unión (Pull Requests)
Nunca unimos código a `main` directamente.
1. En GitHub, presiona el botón **Compare & pull request** para tu rama recién subida.
2. Un compañero revisará tu trabajo. Si todo está correcto, aprobará el *Pull Request*.
3. Al aprobarse, tu código se integrará y, gracias a la palabra clave de tu commit, la tarea se moverá automáticamente a `Done` en el tablero.

---

## 💡 3. Consejos de Oro

* **Comunicación Simple:** Describe tus escenarios funcionales y documentación para que los entienda cualquier persona, evitando hiper-tecnicismos si no son necesarios.
* **Si se rompe, pregunta:** Todos estamos aprendiendo. Si tienes un conflicto con Git o problemas con el entorno virtual, pregunta al equipo antes de borrar archivos al azar.
