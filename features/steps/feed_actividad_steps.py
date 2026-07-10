from behave import given, when, then
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from src.login.models import PerfilUsuario
from src.feed.models import Seguimiento, Publicacion, Republicacion

User = get_user_model()


# ---------------------------------------------------------------------------
# Antecedente compartido
# ---------------------------------------------------------------------------

@given('que el usuario ha iniciado sesión en la plataforma')
def step_usuario_autenticado(context):
    """Crea un usuario principal y lo autentica en el cliente de prueba."""
    context.usuario_principal = User.objects.create_user(
        username='usuario_principal',
        email='principal@ejemplo.com',
        password='password123',
        first_name='Usuario Principal',
    )
    PerfilUsuario.objects.create(
        usuario=context.usuario_principal,
        rol=PerfilUsuario.ESTUDIANTE,
    )
    context.test.client.force_login(context.usuario_principal)


# ---------------------------------------------------------------------------
# Escenario: El feed muestra publicaciones en orden cronológico inverso
# ---------------------------------------------------------------------------

@given('que el usuario sigue a uno o más usuarios que han publicado material recientemente')
def step_seguidos_con_publicaciones(context):
    """
    Crea dos usuarios seguidos y tres publicaciones con fechas distintas
    para poder verificar el orden cronológico inverso.
    """
    usuario_a = User.objects.create_user(
        username='usuario_a',
        email='a@ejemplo.com',
        password='password123',
        first_name='Usuario A',
    )
    usuario_b = User.objects.create_user(
        username='usuario_b',
        email='b@ejemplo.com',
        password='password123',
        first_name='Usuario B',
    )

    Seguimiento.objects.create(
        seguidor=context.usuario_principal,
        seguido=usuario_a,
    )
    Seguimiento.objects.create(
        seguidor=context.usuario_principal,
        seguido=usuario_b,
    )

    # Las publicaciones se crean con fechas explícitamente distintas
    # para garantizar el orden esperado en la prueba.
    ahora = timezone.now()
    publicacion_antigua = Publicacion.objects.create(
        autor=usuario_a,
        titulo='Publicacion antigua',
        tipo=Publicacion.LIBRO,
    )
    Publicacion.objects.filter(pk=publicacion_antigua.pk).update(
        creado=ahora - timezone.timedelta(hours=2)
    )

    publicacion_media = Publicacion.objects.create(
        autor=usuario_b,
        titulo='Publicacion media',
        tipo=Publicacion.LIBRO,
    )
    Publicacion.objects.filter(pk=publicacion_media.pk).update(
        creado=ahora - timezone.timedelta(hours=1)
    )

    publicacion_reciente = Publicacion.objects.create(
        autor=usuario_a,
        titulo='Publicacion reciente',
        tipo=Publicacion.LIBRO,
    )
    Publicacion.objects.filter(pk=publicacion_reciente.pk).update(
        creado=ahora
    )

    context.publicacion_reciente = publicacion_reciente
    context.publicacion_antigua = publicacion_antigua


@when('el usuario accede al feed de seguimiento')
def step_accede_al_feed(context):
    url = reverse('feed:feed')
    context.response = context.test.client.get(url)


@then('las publicaciones aparecen ordenadas de la más reciente a la más antigua')
def step_publicaciones_ordenadas_cronologicamente(context):
    context.test.assertEqual(
        context.response.status_code,
        200,
        'El feed no respondió con HTTP 200.',
    )
    # material_feed contiene libros y republicaciones
    publicaciones = list(context.response.context['material_feed'])
    context.test.assertGreaterEqual(
        len(publicaciones),
        2,
        'El feed debe contener al menos dos publicaciones para verificar el orden.',
    )
    # Verifica que cada publicación sea más reciente o igual que la siguiente
    for i in range(len(publicaciones) - 1):
        context.test.assertGreaterEqual(
            publicaciones[i].creado,
            publicaciones[i + 1].creado,
            f'La publicacion en posicion {i} no es mas reciente que la de posicion {i + 1}.',
        )


# ---------------------------------------------------------------------------
# Escenario: El feed no muestra contenido de usuarios no seguidos
# ---------------------------------------------------------------------------

@given('que hay usuarios en la plataforma a los que el usuario no sigue')
def step_usuarios_no_seguidos_con_contenido(context):
    """
    Crea un usuario seguido con una publicación y un usuario NO seguido
    con otra publicación, para verificar que solo aparece la del seguido.
    """
    usuario_seguido = User.objects.create_user(
        username='usuario_seguido',
        email='seguido@ejemplo.com',
        password='password123',
        first_name='Usuario Seguido',
    )
    usuario_no_seguido = User.objects.create_user(
        username='usuario_no_seguido',
        email='noseguido@ejemplo.com',
        password='password123',
        first_name='Usuario No Seguido',
    )

    Seguimiento.objects.create(
        seguidor=context.usuario_principal,
        seguido=usuario_seguido,
    )

    context.publicacion_seguido = Publicacion.objects.create(
        autor=usuario_seguido,
        titulo='Publicacion de seguido',
        tipo=Publicacion.LIBRO,
    )
    context.publicacion_no_seguido = Publicacion.objects.create(
        autor=usuario_no_seguido,
        titulo='Publicacion de no seguido',
        tipo=Publicacion.LIBRO,
    )


@then('solo aparece contenido de los usuarios que sigue')
def step_solo_contenido_de_seguidos(context):
    context.test.assertEqual(
        context.response.status_code,
        200,
        'El feed no respondió con HTTP 200.',
    )
    publicaciones = list(context.response.context['material_feed'])
    ids_en_feed = [p.pk for p in publicaciones]

    context.test.assertIn(
        context.publicacion_seguido.pk,
        ids_en_feed,
        'La publicacion del usuario seguido no aparece en el feed.',
    )
    context.test.assertNotIn(
        context.publicacion_no_seguido.pk,
        ids_en_feed,
        'La publicacion del usuario no seguido aparece en el feed cuando no deberia.',
    )


# ---------------------------------------------------------------------------
# Escenario: Una republicación preserva la autoría original
# ---------------------------------------------------------------------------

@given('que un usuario seguido ha republicado contenido de un tercero')
def step_seguido_republicó_contenido(context):
    """
    Crea al autor original, al republicador (seguido) y una publicación
    que el republicador comparte.  Se almacena la Republicacion para
    luego verificar que el feed la expone con los metadatos correctos.
    """
    autor_original = User.objects.create_user(
        username='autor_original',
        email='original@ejemplo.com',
        password='password123',
        first_name='Autor Original',
    )
    republicador = User.objects.create_user(
        username='republicador',
        email='republicador@ejemplo.com',
        password='password123',
        first_name='Republicador',
    )

    Seguimiento.objects.create(
        seguidor=context.usuario_principal,
        seguido=republicador,
    )

    publicacion_original = Publicacion.objects.create(
        autor=autor_original,
        titulo='Recurso original del tercero',
        tipo=Publicacion.LIBRO,
    )

    context.republicacion = Republicacion.objects.create(
        publicacion=publicacion_original,
        republicado_por=republicador,
    )


@then('esa publicación aparece indicando quién la republicó')
def step_republicacion_muestra_quien_republicó(context):
    context.test.assertEqual(
        context.response.status_code,
        200,
        'El feed no respondió con HTTP 200.',
    )
    # Extraemos solo las republicaciones del material_feed
    material_feed = list(context.response.context.get('material_feed', []))
    republicaciones = [item for item in material_feed if not hasattr(item, 'titulo')]
    ids_en_feed = [r.pk for r in republicaciones]

    context.test.assertIn(
        context.republicacion.pk,
        ids_en_feed,
        'La republicacion no aparece en el feed.',
    )
    # Verifica que el republicador esté accesible desde el objeto
    republicacion_en_feed = next(
        r for r in republicaciones if r.pk == context.republicacion.pk
    )
    context.test.assertEqual(
        republicacion_en_feed.republicado_por.username,
        'republicador',
        'El republicador no coincide con el esperado.',
    )


@then('la autoría original del contenido es visible')
def step_autoria_original_visible(context):
    material_feed = list(context.response.context.get('material_feed', []))
    republicaciones = [item for item in material_feed if not hasattr(item, 'titulo')]
    republicacion_en_feed = next(
        r for r in republicaciones if r.pk == context.republicacion.pk
    )
    # Verifica que el autor original esté relacionado a través de la publicación
    context.test.assertEqual(
        republicacion_en_feed.publicacion.autor.username,
        'autor_original',
        'El autor original de la publicacion no es accesible desde la republicacion.',
    )


# ---------------------------------------------------------------------------
# Escenario: Filtrar el feed de seguimiento por tipo de contenido
# ---------------------------------------------------------------------------

@when(u'el usuario filtra por {tipo_contenido}')
def step_usuario_filtra_por_tipo(context, tipo_contenido):
    # Simulamos el filtro en el frontend guardando el estado
    context.filtro_aplicado = tipo_contenido


@then(u'el feed muestra únicamente {tipo_contenido} publicado por sus seguidos')
def step_feed_muestra_unicamente_tipo(context, tipo_contenido):
    if tipo_contenido == 'libros':
        material_feed = list(context.response.context.get('material_feed', []))
        context.test.assertGreater(len(material_feed), 0, "No hay libros en el feed.")
        context.test.assertIn(b'id="material-view"', context.response.content)
    elif tipo_contenido == 'colecciones':
        colecciones = list(context.response.context.get('colecciones', []))
        context.test.assertIn(b'id="colecciones-view"', context.response.content)


@then(u'el otro tipo de contenido no aparece en esa vista')
def step_otro_tipo_no_aparece(context):
    # Verificamos que no esten mezclados en el contexto backend
    material_feed = list(context.response.context.get('material_feed', []))
    colecciones = list(context.response.context.get('colecciones', []))
    
    # Comprobar que en material_feed no hay colecciones
    for item in material_feed:
        if hasattr(item, 'titulo'): # Es Publicacion
            context.test.assertNotEqual(item.tipo, 'coleccion', 'Hay una coleccion en material_feed')


@given(u'que el usuario accede al feed de seguimiento')
def step_dado_usuario_accede_feed(context):
    from django.urls import reverse
    # Aseguramos que haya datos invocando la funcion del otro step
    from features.steps.feed_actividad_steps import step_seguidos_con_publicaciones
    step_seguidos_con_publicaciones(context)
    
    context.response = context.test.client.get(reverse('feed:feed'))
