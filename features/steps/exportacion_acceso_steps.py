from behave import given, when, then
from django.contrib.auth import get_user_model
from django.urls import reverse
from src.login.models import PerfilUsuario

User = get_user_model()

# El step 'que el usuario ha iniciado sesion en la plataforma' se define
# en feed_actividad_steps.py y es compartido por todos los features.

@given('que el usuario tiene una cuota de descarga mensual disponible')
def step_usuario_cuota_disponible(context):
    perfil = context.usuario_principal.perfil
    perfil.cuota_descarga = 500
    perfil.save()
    context.perfil = perfil

@given('la cantidad de páginas del libro no excede dicha cuota')
def step_paginas_no_excede(context):
    from src.materiales.models import Libro
    context.libro = Libro.objects.create(
        titulo='Libro Corto',
        numero_paginas=300,
        autor=context.usuario_principal,
    )

@when('el usuario solicita descargar un libro')
def step_usuario_solicita_descargar(context):
    url = reverse('materiales:confirmar_descarga', args=[context.libro.id, 'pdf'])
    context.response = context.test.client.get(url)

@then('el sistema le muestra una pantalla de confirmación con su cuota restante')
def step_muestra_pantalla_confirmacion(context):
    context.test.assertEqual(context.response.status_code, 200, "No se pudo cargar la pantalla de confirmacion")
    context.test.assertTemplateUsed(context.response, 'materiales/confirmar_descarga.html')
    # Verificamos que se paso la cuota restante al template
    context.test.assertIn('cuota_restante', context.response.context)
    context.test.assertTrue(context.response.context['puede_descargar'])

@then('al confirmar la descarga, el libro queda disponible para acceso sin conexión')
def step_confirma_descarga_disponible(context):
    url = reverse('materiales:descargar_libro', args=[context.libro.id, 'pdf'])
    context.response = context.test.client.get(url)
    context.test.assertEqual(context.response.status_code, 200, "La descarga fallo.")
    context.test.assertEqual(context.response['Content-Type'], 'application/pdf')

@then('la cuota del usuario se reduce según el número de páginas descargadas')
def step_cuota_se_reduce(context):
    context.perfil.refresh_from_db()
    # 500 - 300 = 200
    context.test.assertEqual(context.perfil.cuota_descarga, 200, "La cuota no se redujo correctamente.")

@given('la cantidad de páginas del libro excede su cuota restante')
def step_paginas_excede_cuota(context):
    from src.materiales.models import Libro
    context.libro = Libro.objects.create(
        titulo='Libro Largo',
        numero_paginas=800,
        autor=context.usuario_principal,
    )

@then('el sistema bloquea la acción y le muestra un mensaje indicando que su cuota es insuficiente y la fecha de su próxima renovación')
def step_muestra_bloqueo_con_fecha_renovacion(context):
    context.test.assertEqual(context.response.status_code, 200)
    context.test.assertTemplateUsed(context.response, 'materiales/confirmar_descarga.html')
    context.test.assertFalse(context.response.context['puede_descargar'])
    context.test.assertContains(context.response, "Cuota Insuficiente")
    # RN-EXP-02: El mensaje debe indicar la fecha de renovacion
    context.test.assertIn('fecha_renovacion', context.response.context)

@given('que el usuario descarga un libro publicado por otro usuario en formato PDF o EPUB')
def step_descarga_libro_otro_usuario_formato(context):
    from src.materiales.models import Libro
    autor_otro = User.objects.create_user(username='autor2', password='123')
    context.libro = Libro.objects.create(
        titulo='Libro de Autor',
        numero_paginas=100,
        autor=autor_otro,
        contenido_texto='<p>Contenido del libro de prueba.</p>',
    )
    perfil = context.usuario_principal.perfil
    perfil.cuota_descarga = 500
    perfil.save()
    context.perfil = perfil
    url = reverse('materiales:descargar_libro', args=[context.libro.id, 'pdf'])
    context.response = context.test.client.get(url)

@when('el usuario abre el archivo descargado')
def step_usuario_abre_archivo(context):
    context.test.assertEqual(context.response.status_code, 200)
    context.archivo_contenido = context.response.content.decode('latin-1')

@then('el archivo incluye de forma mandatoria el nombre del autor original y la fuente de la publicación')
def step_archivo_incluye_metadatos(context):
    context.test.assertIn("Autor original: autor2", context.archivo_contenido)
    context.test.assertIn("Fuente: Biblioteca Digital", context.archivo_contenido)

# --- Steps para US-20: Gestion y Renovacion de Cuota de Descarga ---

# Escenario: Renovacion automatica de la cuota de descarga cada 30 dias

@given('que un usuario ha consumido parte o la totalidad de su cuota de descarga')
def step_usuario_consumio_cuota(context):
    perfil = context.usuario_principal.perfil
    # Simulamos que el usuario consumio parte de su cuota
    perfil.cuota_descarga = 100
    perfil.save()
    context.perfil = perfil
    context.cuota_antes_de_renovacion = perfil.cuota_descarga

@when('transcurren 30 días desde la última renovación')
def step_transcurren_30_dias(context):
    from datetime import timedelta
    from django.utils import timezone
    perfil = context.perfil
    # RN-EXP-02: Simulamos que la ultima renovacion fue hace 30 dias
    perfil.fecha_ultima_renovacion = timezone.now() - timedelta(days=30)
    perfil.save()
    # Invocar el metodo de renovacion que debe existir en el modelo
    perfil.renovar_cuota_si_corresponde()

@then('su cuota de descarga mensual se restablece automáticamente a su cupo base')
def step_cuota_restablecida(context):
    from src.login.models import PerfilUsuario
    context.perfil.refresh_from_db()
    cuota_base = PerfilUsuario.CUOTA_BASE
    # RN-EXP-03: La cuota base puede estar incrementada por libros publicados
    from src.materiales.models import Libro
    libros_publicados = Libro.objects.filter(
        autor=context.usuario_principal,
        estado=Libro.PUBLICADO,
    ).count()
    cuota_esperada = cuota_base + (libros_publicados * 100)
    context.test.assertEqual(
        context.perfil.cuota_descarga,
        cuota_esperada,
        "La cuota no se restablecio correctamente al cupo base."
    )

# Escenario: Publicar un libro incrementa la cuota de descarga mensual

@given('que el usuario tiene una cuota de descarga mensual establecida')
def step_usuario_cuota_establecida(context):
    perfil = context.usuario_principal.perfil
    perfil.cuota_descarga = PerfilUsuario.CUOTA_BASE
    perfil.save()
    context.perfil = perfil
    context.cuota_antes = perfil.cuota_descarga

@when('el usuario publica un libro exitosamente en la plataforma')
def step_usuario_publica_libro(context):
    from src.materiales.models import Libro, Categoria
    from django.core.files.uploadedfile import SimpleUploadedFile
    categoria = Categoria.objects.create(nombre='Matematicas')
    imagen_portada = SimpleUploadedFile(
        'portada.jpg', b'\xff\xd8\xff\xe0', content_type='image/jpeg'
    )
    libro = Libro.objects.create(
        titulo='Algebra Lineal para Matematicas',
        numero_paginas=50,
        autor=context.usuario_principal,
        contenido_texto=(
            '<p>El algebra lineal es una rama de las matematicas que estudia '
            'conceptos como vectores, matrices, sistemas de ecuaciones lineales '
            'y transformaciones lineales. Es fundamental en ingenieria, fisica '
            'y ciencias de la computacion.</p>'
        ),
        portada=imagen_portada,
    )
    libro.categorias.add(categoria)
    exito, mensaje = libro.publicar()
    context.test.assertTrue(exito, f"La publicacion debio ser exitosa: {mensaje}")
    context.libro_publicado = libro

@then('la cuota de descarga mensual del usuario aumenta en 100 páginas adicionales')
def step_cuota_aumenta_100_paginas(context):
    context.perfil.refresh_from_db()
    cuota_esperada = context.cuota_antes + 100
    context.test.assertEqual(
        context.perfil.cuota_descarga,
        cuota_esperada,
        "La cuota no aumento en 100 paginas tras la publicacion."
    )


# --- Steps para US-21: Descarga de Paginas o Libros Completos ---
# RN-EXP-04: Un usuario puede solicitar imprimir un libro completo,
# un rango de paginas o unicamente la pagina que esta visualizando.


@given('que el usuario tiene abierto un libro para descargarlo')
def step_usuario_visualizando_libro(context):
    from src.materiales.models import Libro, Categoria
    from django.core.files.uploadedfile import SimpleUploadedFile

    categoria = Categoria.objects.create(nombre='Ciencias')
    imagen_portada = SimpleUploadedFile(
        'portada.jpg', b'\xff\xd8\xff\xe0', content_type='image/jpeg'
    )
    libro = Libro.objects.create(
        titulo='Libro de Prueba Paginado',
        numero_paginas=50,
        autor=context.usuario_principal,
        contenido_texto=(
            '<p>Contenido de la pagina uno del libro de prueba.</p>'
            '<div class="page-gap"></div>'
            '<p>Contenido de la pagina dos del libro de prueba.</p>'
            '<div class="page-gap"></div>'
            '<p>Contenido de la pagina tres del libro de prueba.</p>'
        ),
        portada=imagen_portada,
    )
    libro.categorias.add(categoria)
    libro.estado = Libro.PUBLICADO
    libro.save()
    context.libro = libro
    # La pagina actual simulada por defecto es la pagina 1
    context.pagina_actual = 1
    # Configurar cuota suficiente para la descarga
    perfil = context.usuario_principal.perfil
    perfil.cuota_descarga = 500
    perfil.save()
    context.perfil = perfil


@when('el usuario solicita descargar {porcion}')
def step_usuario_solicita_descargar_porcion(context, porcion):
    if porcion == 'la página actual':
        url = reverse(
            'materiales:descargar_pagina',
            args=[context.libro.id, context.pagina_actual, 'pdf'],
        )
        context.response = context.test.client.get(url)

    elif porcion == 'un rango de páginas':
        url = reverse(
            'materiales:descargar_rango',
            args=[context.libro.id, 1, 3, 'pdf'],
        )
        context.response = context.test.client.get(url)

    elif porcion == 'el libro completo':
        url = reverse(
            'materiales:descargar_libro',
            args=[context.libro.id, 'pdf'],
        )
        context.response = context.test.client.get(url)


@then('el sistema genera el documento correspondiente a {porcion} listo para impresión')
def step_sistema_genera_documento_impresion(context, porcion):
    context.test.assertEqual(
        context.response.status_code, 200,
        f"La descarga de '{porcion}' no fue exitosa (status {context.response.status_code}).",
    )
    context.test.assertEqual(
        context.response['Content-Type'], 'application/pdf',
        f"El tipo de contenido no es PDF para '{porcion}'.",
    )
    # Verificar que el archivo descargado tiene contenido
    context.test.assertTrue(
        len(context.response.content) > 0,
        f"El archivo generado para '{porcion}' esta vacio.",
    )
    # RN-EXP-06: El archivo debe incluir metadatos de autoria
    contenido = context.response.content.decode('latin-1')
    context.test.assertIn(
        'Autor original',
        contenido,
        f"El archivo para '{porcion}' no incluye los metadatos del autor original.",
    )
