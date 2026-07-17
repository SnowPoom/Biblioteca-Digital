from behave import given, when, then
from django.contrib.auth import get_user_model
from src.materiales.models import Coleccion, Libro, Categoria, ParticipacionColeccion

User = get_user_model()

@given('que el usuario es participante de una colección colaborativa')
def step_impl(context):
    if not hasattr(context, 'coleccion'):
        context.coleccion = Coleccion.objects.create(
            nombre='Colección Antecedente',
            creador=context.usuario_principal
        )

# ==============================================================================
# ESCENARIO 1: Dejar un comentario de retroalimentación sobre un libro de la colección
# ==============================================================================

@given('que el usuario accede a un libro dentro de la colección')
def step_impl(context):
    # Setup del libro y colección si no existe
    if not hasattr(context, 'coleccion'):
        context.coleccion = Coleccion.objects.create(
            nombre='Colección de prueba',
            creador=context.usuario_principal
        )
    if not hasattr(context, 'libro'):
        cat = Categoria.objects.create(nombre="Tecnología")
        context.libro = Libro.objects.create(
            titulo='Libro de prueba',
            autor=context.usuario_principal
        )
        context.libro.categorias.add(cat)
        context.coleccion.agregar_libro(context.usuario_principal, context.libro)

@when('el usuario deja un comentario de retroalimentación sobre ese libro')
def step_impl(context):
    from src.materiales.models import ComentarioRetroalimentacion
    try:
        context.comentario = ComentarioRetroalimentacion.crear_comentario(
            coleccion=context.coleccion,
            libro=context.libro,
            usuario=context.usuario_principal,
            texto="Este es un comentario de sugerencia"
        )
    except Exception as e:
        context.exception = e

@then('el comentario queda guardado')
def step_impl(context):
    context.test.assertIsNotNone(context.comentario)
    context.test.assertTrue(context.comentario.id)

@then('todos los participantes de la colección pueden verlo')
def step_impl(context):
    # Simular la visibilidad verificando que los participantes puedan acceder
    for participacion in context.coleccion.participantes_activos():
        visible = context.comentario.es_visible_para(participacion.usuario)
        context.test.assertTrue(visible)


# ==============================================================================
# ESCENARIO 2: Los comentarios de retroalimentación no son visibles fuera de la colección
# ==============================================================================

@given('que una colección tiene comentarios de retroalimentación registrados')
def step_impl(context):
    if not hasattr(context, 'usuario_principal'):
        context.usuario_principal = User.objects.create_user(username='usuario_principal_2', password='pwd')
    if not hasattr(context, 'coleccion'):
        context.coleccion = Coleccion.objects.create(nombre='Coleccion con comentarios', creador=context.usuario_principal)
    if not hasattr(context, 'libro'):
        cat, _ = Categoria.objects.get_or_create(nombre='Matematicas')
        context.libro = Libro.objects.create(titulo='Libro Comentable 2', autor=context.usuario_principal)
        context.libro.categorias.add(cat)
        context.coleccion.agregar_libro(context.usuario_principal, context.libro)
    from src.materiales.models import ComentarioRetroalimentacion
    context.comentario = ComentarioRetroalimentacion.crear_comentario(
        coleccion=context.coleccion, libro=context.libro, usuario=context.usuario_principal, texto="Un comentario"
    )

@when('un usuario que no es miembro de la colección accede a ella')
def step_impl(context):
    context.usuario_externo = User.objects.create_user(username='externo', password='pwd')
    # Accede simulando un request a la vista o invocando el modelo

@then('ese usuario no puede ver los comentarios internos')
def step_impl(context):
    visible = context.comentario.es_visible_para(context.usuario_externo)
    context.test.assertFalse(visible)





# ==============================================================================
# ESCENARIO 7: Un comentario con contenido inapropiado es rechazado por el sistema
# ==============================================================================

@given('que el usuario intenta dejar un comentario de retroalimentación con contenido inapropiado')
def step_impl(context):
    if not hasattr(context, 'coleccion'):
        context.coleccion = Coleccion.objects.create(
            nombre='Colección para comentario',
            creador=context.usuario_principal
        )
    if not hasattr(context, 'libro'):
        cat, _ = Categoria.objects.get_or_create(nombre="Sociales")
        context.libro = Libro.objects.create(titulo='Libro Comentable', autor=context.usuario_principal)
        context.libro.categorias.add(cat)
        context.coleccion.agregar_libro(context.usuario_principal, context.libro)
        
    context.texto_inapropiado = "Este libro es una mierda"

@when('el usuario envía el comentario')
def step_impl(context):
    from src.materiales.models import ComentarioRetroalimentacion
    from django.core.exceptions import ValidationError
    try:
        context.comentario = ComentarioRetroalimentacion.crear_comentario(
            coleccion=context.coleccion,
            libro=context.libro,
            usuario=context.usuario_principal,
            texto=context.texto_inapropiado
        )
        context.excepcion_comentario = None
    except ValidationError as e:
        context.excepcion_comentario = e

@then('el sistema detecta el contenido y rechaza la operación')
def step_impl(context):
    context.test.assertIsNotNone(context.excepcion_comentario)
    context.test.assertIn("inapropiado", str(context.excepcion_comentario).lower())

@then('el comentario no queda registrado en la colección')
def step_impl(context):
    from src.materiales.models import ComentarioRetroalimentacion
    existe = ComentarioRetroalimentacion.objects.filter(texto=context.texto_inapropiado).exists()
    context.test.assertFalse(existe)


# ==============================================================================
# ESCENARIO 8: El historial de comentarios de retroalimentación no puede ser eliminado
# ==============================================================================

@given('que existen comentarios de retroalimentación registrados en la colección')
def step_impl(context):
    if not hasattr(context, 'usuario_principal'):
        context.usuario_principal = User.objects.create_user(username='usuario_principal_3', password='pwd')
    if not hasattr(context, 'coleccion'):
        context.coleccion = Coleccion.objects.create(nombre='Coleccion para borrar comentario', creador=context.usuario_principal)
    if not hasattr(context, 'libro'):
        cat, _ = Categoria.objects.get_or_create(nombre='Historia')
        context.libro = Libro.objects.create(titulo='Libro Comentable 3', autor=context.usuario_principal)
        context.libro.categorias.add(cat)
        context.coleccion.agregar_libro(context.usuario_principal, context.libro)
    from src.materiales.models import ComentarioRetroalimentacion
    context.comentario = ComentarioRetroalimentacion.crear_comentario(
        coleccion=context.coleccion, libro=context.libro, usuario=context.usuario_principal, texto="Otro comentario"
    )

@when('un participante intenta eliminar un comentario de retroalimentación')
def step_impl(context):
    try:
        context.comentario.eliminar()
        context.excepcion_eliminacion = None
    except Exception as e:
        context.excepcion_eliminacion = e

@then('el sistema rechaza la operación de eliminación')
def step_impl(context):
    context.test.assertIsNotNone(getattr(context, 'excepcion_eliminacion', None))

@then('el comentario permanece en el historial')
def step_impl(context):
    from src.materiales.models import ComentarioRetroalimentacion
    existe = ComentarioRetroalimentacion.objects.filter(id=context.comentario.id).exists()
    context.test.assertTrue(existe)
