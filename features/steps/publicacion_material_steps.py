from behave import given, when, then
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from src.materiales.models import Libro, Categoria

User = get_user_model()

# --- Antecedentes ---
# El step "que el usuario ha iniciado sesion en la plataforma" se define
# en feed_actividad_steps.py y Behave lo comparte con todos los features.


# --- Escenario: Publicar un libro con todos los requisitos completos ---

@given('que el usuario ha preparado un libro con título, portada, contenido textual y categoría')
def step_libro_requisitos_completos(context):
    context.categoria = Categoria.objects.create(nombre='Matemáticas')
    context.datos_libro = {
        'titulo': 'Algebra Lineal Fundamental',
        'portada': SimpleUploadedFile(
            'portada.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
        'contenido_texto': 'Este es el contenido textual del libro de prueba.',
        'categorias': [context.categoria.id],
        'numero_paginas': 100,
    }


@when('el usuario solicita publicar el libro')
def step_solicita_publicar(context):
    context.libro = Libro.objects.create(
        titulo=context.datos_libro['titulo'],
        contenido_texto=context.datos_libro['contenido_texto'],
        numero_paginas=context.datos_libro['numero_paginas'],
        autor=context.usuario,
    )
    context.libro.portada.save(
        'portada.png',
        context.datos_libro['portada'],
    )
    context.libro.categorias.add(context.categoria)
    context.resultado = context.libro.publicar()


@then('el sistema valida el contenido automáticamente')
def step_valida_contenido(context):
    context.test.assertTrue(
        context.resultado,
        "La publicacion deberia ser exitosa con todos los requisitos completos.",
    )
    context.libro.refresh_from_db()
    context.test.assertEqual(
        context.libro.estado,
        Libro.EN_REVISION,
        "El estado inicial del libro al publicarse debe ser 'En Revision'.",
    )


@then('el libro queda visible para la comunidad académica')
def step_libro_visible(context):
    # RN-PUB-02: El libro queda en revision; sera visible tras pasar la validacion
    context.test.assertEqual(
        context.libro.estado,
        Libro.EN_REVISION,
        "El libro debe estar en estado 'En Revision' para validacion automatizada.",
    )


# --- Esquema del escenario: No se puede publicar un libro con requisitos incompletos ---

@given('que el usuario está creando un libro sin {requisito_faltante}')
def step_libro_sin_requisito(context, requisito_faltante):
    context.categoria = Categoria.objects.create(nombre='Ciencias')
    portada = SimpleUploadedFile(
        'portada.png',
        b'\x89PNG\r\n\x1a\n\x00\x00\x00',
        content_type='image/png',
    )

    context.datos_libro = {
        'titulo': 'Libro Incompleto',
        'portada': portada,
        'contenido_texto': 'Contenido textual valido para el libro.',
        'categorias': [context.categoria.id],
        'numero_paginas': 50,
    }

    if requisito_faltante == 'portada':
        context.datos_libro['portada'] = None
    elif requisito_faltante == 'contenido textual':
        context.datos_libro['contenido_texto'] = ''
    elif requisito_faltante == 'categoría':
        context.datos_libro['categorias'] = []


@when('el usuario intenta publicar el libro')
def step_intenta_publicar(context):
    libro = Libro(
        titulo=context.datos_libro['titulo'],
        contenido_texto=context.datos_libro.get('contenido_texto', ''),
        numero_paginas=context.datos_libro.get('numero_paginas', 50),
        autor=context.usuario,
    )

    if context.datos_libro.get('portada'):
        libro.portada.save(
            'portada.png',
            context.datos_libro['portada'],
            save=False,
        )

    libro.save()

    categorias = context.datos_libro.get('categorias', [])
    for categoria_id in categorias:
        libro.categorias.add(categoria_id)

    context.libro = libro
    context.resultado = libro.publicar()


@then('el libro no queda publicado')
def step_libro_no_publicado(context):
    context.libro.refresh_from_db()
    context.test.assertEqual(
        context.libro.estado,
        Libro.BORRADOR,
        "El libro debe permanecer en estado 'Borrador' al fallar la validacion.",
    )


# --- Escenario: No se puede publicar un libro compuesto unicamente por imagenes ---

@given('que el usuario ha preparado un libro cuyo contenido consiste solo en imágenes sin texto')
def step_libro_solo_imagenes(context):
    context.categoria = Categoria.objects.create(nombre='Arte')
    context.datos_libro = {
        'titulo': 'Libro Solo Imagenes',
        'portada': SimpleUploadedFile(
            'portada.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
        'contenido_texto': '',
        'categorias': [context.categoria.id],
        'numero_paginas': 30,
    }


# --- Escenario: No se puede publicar un libro que supera el limite de paginas ---

@given('que el usuario ha preparado un libro que excede las 500 páginas')
def step_libro_excede_paginas(context):
    context.categoria = Categoria.objects.create(nombre='Historia')
    context.datos_libro = {
        'titulo': 'Enciclopedia Extensa',
        'portada': SimpleUploadedFile(
            'portada.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
        'contenido_texto': 'Contenido textual valido para el libro extenso.',
        'categorias': [context.categoria.id],
        'numero_paginas': 501,
    }


@then('el libro no queda publicado hasta que el contenido sea reducido')
def step_libro_no_publicado_paginas(context):
    context.libro.refresh_from_db()
    context.test.assertEqual(
        context.libro.estado,
        Libro.BORRADOR,
        "El libro debe permanecer en 'Borrador' hasta reducir el numero de paginas.",
    )
