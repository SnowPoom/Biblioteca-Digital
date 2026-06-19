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
