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
# Escenario: Seguir a otro usuario
# ---------------------------------------------------------------------------

@given('que el usuario está visitando el perfil público de otro usuario')
def step_visitando_perfil_publico(context):
    """
    Crea un usuario objetivo que ya tiene publicaciones y lo almacena
    en el contexto para que los pasos posteriores puedan operar sobre él.
    """
    context.usuario_objetivo = User.objects.create_user(
        username='usuario_objetivo',
        email='objetivo@ejemplo.com',
        password='password123',
        first_name='Usuario Objetivo',
    )
    PerfilUsuario.objects.create(
        usuario=context.usuario_objetivo,
        rol=PerfilUsuario.ESTUDIANTE,
    )
    # El usuario objetivo ya tiene contenido publicado
    context.publicacion_objetivo = Publicacion.objects.create(
        autor=context.usuario_objetivo,
        titulo='Libro del usuario objetivo',
        tipo=Publicacion.LIBRO,
    )


@when('el usuario decide seguir a ese perfil')
def step_usuario_decide_seguir(context):
    """
    Simula la acción de seguir al usuario objetivo a través de la vista real.
    """
    context.test.client.force_login(context.usuario_principal)
    url = reverse('feed:seguir_usuario', args=[context.usuario_objetivo.pk])
    response = context.test.client.post(url)
    
    context.test.assertEqual(response.status_code, 302, 'Expected redirect after following')
    
    # Verifica que la relación se ha creado
    relacion_existe = Seguimiento.objects.filter(
        seguidor=context.usuario_principal,
        seguido=context.usuario_objetivo
    ).exists()
    context.test.assertTrue(relacion_existe, "La relación de seguimiento no se creó.")


@then('el contenido que publique ese usuario comienza a aparecer en el feed de seguimiento')
def step_contenido_aparece_en_feed(context):
    """
    Verifica que tras seguir al usuario, su publicación ya aparece
    en el feed del usuario principal.
    """
    url = reverse('feed:feed')
    response = context.test.client.get(url)

    context.test.assertEqual(
        response.status_code,
        200,
        'El feed no respondió con HTTP 200.',
    )

    publicaciones = list(response.context['material_feed'])
    ids_en_feed = [p.pk for p in publicaciones]

    context.test.assertIn(
        context.publicacion_objetivo.pk,
        ids_en_feed,
        'La publicacion del usuario seguido no aparece en el feed despues de seguirlo.',
    )


# ---------------------------------------------------------------------------
# Escenario: Dejar de seguir a un usuario elimina su contenido del feed
# ---------------------------------------------------------------------------

@given('que el usuario sigue a otro usuario cuyo contenido aparece en su feed')
def step_usuario_sigue_a_otro_con_contenido(context):
    """
    Crea un usuario seguido con una publicación y establece el seguimiento.
    Verifica que el contenido efectivamente aparece en el feed antes
    de ejecutar la acción de dejar de seguir.
    """
    context.usuario_a_dejar = User.objects.create_user(
        username='usuario_a_dejar',
        email='adejar@ejemplo.com',
        password='password123',
        first_name='Usuario A Dejar',
    )
    PerfilUsuario.objects.create(
        usuario=context.usuario_a_dejar,
        rol=PerfilUsuario.ESTUDIANTE,
    )

    context.publicacion_a_desaparecer = Publicacion.objects.create(
        autor=context.usuario_a_dejar,
        titulo='Publicacion que debe desaparecer',
        tipo=Publicacion.LIBRO,
    )

    context.seguimiento_a_eliminar = Seguimiento.objects.create(
        seguidor=context.usuario_principal,
        seguido=context.usuario_a_dejar,
    )

    # Verificación previa: el contenido aparece en el feed antes de dejar de seguir
    url = reverse('feed:feed')
    response = context.test.client.get(url)
    publicaciones = list(response.context['material_feed'])
    ids_en_feed = [p.pk for p in publicaciones]
    context.test.assertIn(
        context.publicacion_a_desaparecer.pk,
        ids_en_feed,
        'La publicacion del seguido debe aparecer en el feed antes de dejar de seguirlo.',
    )


@when('el usuario deja de seguir a ese usuario')
def step_usuario_deja_de_seguir(context):
    """
    Elimina la relación de seguimiento usando la vista real.
    """
    context.test.client.force_login(context.usuario_principal)
    url = reverse('feed:dejar_de_seguir', args=[context.usuario_a_dejar.pk])
    response = context.test.client.post(url)
    
    context.test.assertEqual(response.status_code, 302, 'Expected redirect after unfollowing')
    
    # Verifica que la relación se ha eliminado
    relacion_existe = Seguimiento.objects.filter(
        seguidor=context.usuario_principal,
        seguido=context.usuario_a_dejar
    ).exists()
    context.test.assertFalse(relacion_existe, "La relación de seguimiento no se eliminó.")


@then('el contenido de ese usuario desaparece del feed de seguimiento de forma inmediata')
def step_contenido_desaparece_del_feed(context):
    """
    Verifica que tras eliminar el seguimiento, el contenido del
    usuario dejado de seguir ya no aparece en el feed.
    """
    url = reverse('feed:feed')
    response = context.test.client.get(url)

    if response.status_code == 302:
        # El feed quedó completamente vacío y redirigió a inicio
        context.test.assertRedirects(response, reverse('materiales:inicio'))
    else:
        context.test.assertEqual(
            response.status_code,
            200,
            'El feed no respondió con HTTP 200.',
        )
        publicaciones = list(response.context.get('material_feed', []))
        ids_en_feed = [p.pk for p in publicaciones]
    
        context.test.assertNotIn(
            context.publicacion_a_desaparecer.pk,
            ids_en_feed,
            'La publicacion del usuario dejado de seguir sigue apareciendo en el feed.',
        )


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


# ---------------------------------------------------------------------------
# Escenario: Cuando no hay seguidos ni publicaciones recientes se muestra el feed de recomendaciones
# ---------------------------------------------------------------------------

@given('que el usuario no sigue a nadie o sus seguidos no tienen publicaciones recientes')
def step_no_sigue_a_nadie_o_sin_publicaciones(context):
    """
    Asegura que el usuario no sigue a nadie y crea contenido popular
    en la plataforma para verificar que se muestran recomendaciones
    generales en la redireccion. RN-FED-07, US-27.
    """
    from src.materiales.models import Libro, Categoria
    from src.feed.models import Publicacion, Categoria as FeedCategoria

    # El usuario_principal creado en el antecedente no sigue a nadie
    Seguimiento.objects.filter(seguidor=context.usuario_principal).delete()

    otro_autor = User.objects.create_user(
        username='autor_contenido_feed_vacio',
        email='autor_feed_vacio@ejemplo.com',
        password='password123',
        first_name='Autor Feed Vacio',
    )
    PerfilUsuario.objects.create(
        usuario=otro_autor,
        rol=PerfilUsuario.ESTUDIANTE,
    )

    cat_general = Categoria.objects.create(nombre='General Feed')

    # Crear libro popular para que aparezca en recomendaciones de arranque en frio
    libro_popular = Libro.objects.create(
        titulo='Libro popular para feed vacio',
        autor=otro_autor,
        estado=Libro.PUBLICADO,
        contenido_texto='Contenido de prueba.',
        numero_paginas=10,
        visualizaciones=800,
        descargas=300,
    )
    pub = Publicacion.objects.create(
        pk=libro_popular.pk,
        autor=otro_autor,
        titulo=libro_popular.titulo,
        tipo=Publicacion.LIBRO,
    )
    feed_cat, _ = FeedCategoria.objects.get_or_create(nombre=cat_general.nombre)
    pub.categorias.add(feed_cat)

    context.libro_popular_feed_vacio = libro_popular


@then('el sistema muestra el feed de recomendaciones en su lugar')
def step_muestra_feed_recomendaciones(context):
    """
    Verifica que cuando el feed de seguimiento esta vacio, el sistema
    redirige a la pagina de inicio donde se muestra el contenido de
    mayor consumo general de la plataforma (recomendaciones de
    arranque en frio). RN-FED-07, RN-REC-05.
    """
    # El feed vacio debe redirigir a la pagina de inicio
    context.test.assertEqual(
        context.response.status_code,
        302,
        'El feed vacio no genero una redireccion.',
    )
    context.test.assertRedirects(context.response, reverse('materiales:inicio'))

    # Seguir la redireccion para verificar que la pagina de inicio
    # contiene recomendaciones basadas en el consumo general
    response_inicio = context.test.client.get(reverse('materiales:inicio'))
    context.test.assertEqual(
        response_inicio.status_code,
        200,
        'La pagina de inicio no respondio con HTTP 200.',
    )

    recomendaciones = list(response_inicio.context.get('recomendaciones', []))
    context.test.assertGreater(
        len(recomendaciones),
        0,
        'La pagina de inicio no muestra recomendaciones generales cuando el feed de seguimiento esta vacio.',
    )


# ---------------------------------------------------------------------------
# Escenario: Acceder al detalle de una publicación desde el feed
# ---------------------------------------------------------------------------

@given('que el usuario está revisando el feed de seguimiento')
def step_revisando_feed(context):
    step_seguidos_con_publicaciones(context)
    url = reverse('feed:feed')
    context.response = context.test.client.get(url)
    context.publicacion_a_seleccionar = context.publicacion_reciente

@when('el usuario selecciona una publicación')
def step_selecciona_publicacion(context):
    import re
    html = context.response.content.decode('utf-8')
    match = re.search(fr'href="([^"]+/{context.publicacion_a_seleccionar.pk}/?[^"]*)"', html)
    context.test.assertIsNotNone(match, "No se encontró el enlace a la publicación en el HTML")
    url = match.group(1)
    context.response_detalle = context.test.client.get(url)

@then('el sistema lo redirige al detalle completo de ese libro o colección')
def step_redirige_a_detalle(context):
    context.test.assertEqual(context.response_detalle.status_code, 200)
    context.test.assertEqual(
        context.response_detalle.context['libro'].pk,
        context.publicacion_a_seleccionar.pk
    )


# ---------------------------------------------------------------------------
# Escenario: Recibir notificación cuando alguien empieza a seguirte
# ---------------------------------------------------------------------------

@given('que el usuario tiene un perfil público en la plataforma')
def step_perfil_publico(context):
    # Ya está autenticado como usuario_principal
    pass

@when('otro usuario comienza a seguirlo')
def step_otro_comienza_a_seguir(context):
    context.otro_usuario = User.objects.create_user(
        username='otro_usuario',
        email='otro@ejemplo.com',
        password='password123',
    )
    Seguimiento.objects.create(
        seguidor=context.otro_usuario,
        seguido=context.usuario_principal,
    )

@then('el usuario recibe una notificación informando quién lo empezó a seguir')
def step_recibe_notificacion_seguimiento(context):
    # Verificamos que haya una notificación en la base de datos
    # Como la BD no tiene modelo Notificacion aun, esto fallara si no lo implementamos.
    # Pero usaremos una abstraccion.
    try:
        from src.feed.models import Notificacion
        notificaciones = Notificacion.objects.filter(usuario=context.usuario_principal)
        context.test.assertEqual(notificaciones.count(), 1)
        context.test.assertIn(context.otro_usuario.username, notificaciones.first().mensaje)
    except ImportError:
        context.test.fail("Modelo Notificacion no encontrado")
