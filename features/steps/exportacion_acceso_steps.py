from behave import given, when, then
from django.contrib.auth import get_user_model
from django.urls import reverse
from src.login.models import PerfilUsuario

User = get_user_model()

@given('que el usuario ha iniciado sesión en la plataforma')
def step_usuario_iniciado_sesion(context):
    user = User.objects.create_user(
        username='lector',
        email='lector@ejemplo.com',
        password='password123',
        first_name='Lector'
    )
    # Suponiendo que el modelo PerfilUsuario tendrá cuota, la inicializamos
    perfil = PerfilUsuario.objects.create(usuario=user, rol=PerfilUsuario.ESTUDIANTE)
    context.user = user
    context.perfil = perfil
    context.test.client.login(username='lector', password='password123')

@given('que el usuario tiene una cuota de descarga mensual disponible')
def step_usuario_cuota_disponible(context):
    # Definimos que el usuario tiene 500 páginas de cuota
    context.perfil.cuota_descarga = 500
    context.perfil.save()

@given('la cantidad de páginas del libro no excede dicha cuota')
def step_paginas_no_excede(context):
    from src.materiales.models import Libro
    # Crear un libro de 300 páginas
    context.libro = Libro.objects.create(
        titulo='Libro Corto',
        paginas=300,
        autor=context.user,
        archivo_formato='PDF'
    )

@when('el usuario descarga un libro')
def step_usuario_descarga_libro_cuando(context):
    url = reverse('materiales:descargar_libro', args=[context.libro.id])
    context.response = context.test.client.get(url)

@when('el usuario intenta descargar un libro')
def step_usuario_intenta_descargar(context):
    url = reverse('materiales:descargar_libro', args=[context.libro.id])
    context.response = context.test.client.get(url)

@then('el libro queda disponible para acceso sin conexión')
def step_libro_disponible_offline(context):
    context.test.assertEqual(context.response.status_code, 200, "La descarga falló.")
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
        paginas=800, # Excede los 500
        autor=context.user,
        archivo_formato='PDF'
    )

@then('el sistema le informa que no tiene suficientes páginas en su cuota')
def step_informa_no_suficientes_paginas(context):
    context.test.assertContains(
        context.response,
        "no tiene suficientes páginas en su cuota",
        status_code=context.response.status_code
    )

@given('que el usuario descarga un libro publicado por otro usuario en formato PDF o EPUB')
def step_descarga_libro_otro_usuario_formato(context):
    from src.materiales.models import Libro
    autor_otro = User.objects.create_user(username='autor2', password='123')
    context.libro = Libro.objects.create(
        titulo='Libro de Autor',
        paginas=100,
        autor=autor_otro,
        archivo_formato='PDF'
    )
    context.perfil.cuota_descarga = 500
    context.perfil.save()
    url = reverse('materiales:descargar_libro', args=[context.libro.id])
    context.response = context.test.client.get(url)

@when('el usuario abre el archivo descargado')
def step_usuario_abre_archivo(context):
    context.test.assertEqual(context.response.status_code, 200)
    context.archivo_contenido = context.response.content.decode('latin-1')

@then('el archivo incluye de forma mandatoria el nombre del autor original y la fuente de la publicación')
def step_archivo_incluye_metadatos(context):
    context.test.assertIn("Autor original: autor2", context.archivo_contenido)
    context.test.assertIn("Fuente: Biblioteca Digital", context.archivo_contenido)

# --- Stubs para los otros escenarios de exportacion_acceso.feature ---

@given('que el usuario publica un libro exitosamente en la plataforma')
def step_usuario_publica_libro(context):
    pass

@then('la cuota de descarga mensual del usuario aumenta en 100 páginas adicionales')
def step_cuota_aumenta_100_paginas(context):
    pass

@given('que el usuario está visualizando un libro')
def step_usuario_visualiza_libro(context):
    pass

@when('el usuario solicita imprimir {porcion}')
def step_usuario_solicita_imprimir(context, porcion):
    pass

@then('el sistema genera el documento correspondiente a {porcion} listo para impresión')
def step_sistema_genera_documento_impresion(context, porcion):
    pass
