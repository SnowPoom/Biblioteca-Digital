
```
# 🚀 Guía de Instalación: Cómo preparar tu computadora para programar

¡Hola, equipo! Para empezar a trabajar en la Biblioteca Digital, necesitamos descargar el código y preparar nuestro entorno. Sigue estos pasos exactos y estarás listo para programar en un par de minutos.

## 0. ¿Qué necesitas tener instalado?
Antes de empezar, asegúrate de tener en tu computadora:
* **Python** (La base de todo).
* **Git** (Para descargar el código).
* **Visual Studio Code (VS Code)** (Nuestro editor de código).

---

## Paso 1: Descargar el proyecto (Clonar)
Vamos a traer el código de GitHub a tu computadora.

1. Crea una carpeta en tu computadora donde quieras guardar el proyecto.
2. Abre esa carpeta con **VS Code**.
3. Abre la terminal integrada de VS Code (`Ctrl + ñ` o `Terminal > Nuevo Terminal`).
4. Escribe el siguiente comando y presiona Enter (reemplaza el enlace por el link real de nuestro GitHub):
   ```bash
   git clone [https://github.com/nuestro-usuario/nuestro-repo.git](https://github.com/nuestro-usuario/nuestro-repo.git) .
```

*(Ojo: ¡No olvides el punto al final! Eso hace que el código se descargue justo en la carpeta donde estás y no cree una carpeta doble).*

## Paso 2: Crear nuestra burbuja de trabajo (Entorno Virtual)

Para no mezclar las herramientas de este proyecto con otras cosas de tu computadora, crearemos un espacio aislado llamado "entorno virtual".

En la misma terminal de VS Code, escribe:

**Bash**

```
python -m venv venv
```

**Ahora, ¡actívalo!** Dependiendo de la terminal que uses, el comando cambia un poco:

* Si usas **Git Bash** (la terminal con letras de colores): `source venv/Scripts/activate`
* Si usas  **Windows PowerShell** : `.\venv\Scripts\Activate.ps1`
* Si usas  **Mac/Linux** : `source venv/bin/activate`

Sabrás que funcionó si al inicio de tu línea en la terminal aparece un  **`(venv)`** . ¡Nunca programes si no ves ese `(venv)` activo!

## Paso 3: Instalar las herramientas mágicas

Con la burbuja activa, vamos a instalar Django (para la web) y Behave (para nuestras pruebas).

Escribe esto y deja que termine de cargar:

**Bash**

```
pip install django behave behave-django
```

## Paso 4: ¡Comprobar que todo funciona!

Vamos a asegurarnos de que la instalación fue un éxito y que tu compu ya habla con nuestro código.

**1. Revisa que las pruebas pasen:**

Escribe en la terminal:

**Bash**

```
python manage.py behave
```

Si ves texto verde diciendo que los escenarios pasaron, ¡vas por buen camino!

**2. Levanta la página web:**

Escribe en la terminal:

**Bash**

```
python manage.py runserver
```
