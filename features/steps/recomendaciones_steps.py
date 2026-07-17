from behave import given, when, then
from django.contrib.auth import get_user_model
from django.utils import timezone

from src.login.models import PerfilUsuario
from src.feed.models import Publicacion, Categoria as FeedCategoria
from src.materiales.models import Libro, Categoria

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _crear_libro_publicado(autor, titulo, categorias=None, visualizaciones=0,
                           descargas=0, republicaciones=0):
    """Crea un Libro en estado publicado y su Publicacion espejo en el feed."""
    libro = Libro.objects.create(
        titulo=titulo,
        autor=autor,
        estado=Libro.PUBLICADO,
        contenido_texto='Contenido de prueba para el libro.',
        numero_paginas=10,
        visualizaciones=visualizaciones,
        descargas=descargas,
        republicaciones=republicaciones,
    )
    pub = Publicacion.objects.create(
        pk=libro.pk,
        autor=autor,
        titulo=titulo,
        tipo=Publicacion.LIBRO,
    )
    if categorias:
        for cat in categorias:
            feed_cat, _ = FeedCategoria.objects.get_or_create(nombre=cat.nombre)
            pub.categorias.add(feed_cat)
    return libro, pub


def _crear_coleccion_publicada(autor, titulo, categorias=None):
    """Crea una Publicacion de tipo coleccion en el feed."""
    pub = Publicacion.objects.create(
        autor=autor,
        titulo=titulo,
        tipo=Publicacion.COLECCION,
    )
    if categorias:
        for cat in categorias:
            feed_cat, _ = FeedCategoria.objects.get_or_create(nombre=cat.nombre)
            pub.categorias.add(feed_cat)
    return pub


# ---------------------------------------------------------------------------
# Escenario: Ver recomendaciones basadas en el historial de lectura
# (RN-REC-01, RN-REC-03)
# ---------------------------------------------------------------------------

@given('que el usuario tiene historial de lectura en una o más áreas temáticas')
def step_usuario_con_historial_lectura(context):
    """
    Crea categorias, libros ya leidos por el usuario y libros nuevos
    en las mismas areas para que el motor de recomendaciones los detecte.
    """
    from src.recomendaciones.models import HistorialLectura

    cat_ciencias = Categoria.objects.create(nombre='Ciencias')
    cat_historia = Categoria.objects.create(nombre='Historia')

    otro_autor = User.objects.create_user(
        username='autor_recomendaciones',
        email='autor_rec@ejemplo.com',
        password='password123',
        first_name='Autor Recomendaciones',
    )
    PerfilUsuario.objects.create(
        usuario=otro_autor,
        rol=PerfilUsuario.ESTUDIANTE,
    )

    # Libros ya leidos por el usuario (deben excluirse de las recomendaciones)
    libro_leido, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro ya leido de Ciencias',
        categorias=[cat_ciencias],
    )
    HistorialLectura.objects.create(
        usuario=context.usuario_principal,
        publicacion=Publicacion.objects.get(pk=libro_leido.pk),
    )
    context.libro_leido = libro_leido

    # Libros nuevos en la misma area tematica (deben aparecer como recomendacion)
    libro_nuevo_ciencias, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro nuevo de Ciencias',
        categorias=[cat_ciencias],
    )
    context.libro_nuevo_ciencias = libro_nuevo_ciencias

    # Libro de otra area que NO ha explorado (menor relevancia)
    libro_otra_area, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro de Arte',
        categorias=[Categoria.objects.create(nombre='Arte')],
    )
    context.libro_otra_area = libro_otra_area

    context.cat_ciencias = cat_ciencias


@when('el usuario accede a la sección de recomendaciones')
def step_accede_seccion_recomendaciones(context):
    """Solicita la vista de recomendaciones a traves del cliente de prueba."""
    from django.urls import reverse

    url = reverse('recomendaciones:recomendaciones')
    context.response = context.test.client.get(url)


@then('el sistema recomienda hasta 10 libros y hasta 10 colecciones relacionados con las áreas que más ha explorado')
def step_presenta_contenido_areas_exploradas(context):
    """
    Verifica que las recomendaciones devueltas esten relacionadas con las
    categorias que el usuario ha explorado en su historial de lectura,
    y que haya un maximo de 10 libros y 10 colecciones.
    RN-REC-01: Historial de lectura y areas tematicas como senales primarias.
    """
    context.test.assertEqual(
        context.response.status_code,
        200,
        'La seccion de recomendaciones no respondio con HTTP 200.',
    )

    recomendaciones = list(context.response.context['recomendaciones'])
    context.test.assertGreater(
        len(recomendaciones),
        0,
        'No se generaron recomendaciones cuando el usuario tiene historial.',
    )

    # Validar el limite maximo de 10 libros y 10 colecciones
    libros_recomendados = [pub for pub in recomendaciones if pub.tipo == Publicacion.LIBRO]
    colecciones_recomendadas = [pub for pub in recomendaciones if pub.tipo == Publicacion.COLECCION]

    context.test.assertLessEqual(
        len(libros_recomendados),
        10,
        f'Se recomendaron {len(libros_recomendados)} libros, superando el limite de 10.'
    )
    context.test.assertLessEqual(
        len(colecciones_recomendadas),
        10,
        f'Se recomendaron {len(colecciones_recomendadas)} colecciones, superando el limite de 10.'
    )

    # Al menos una recomendacion debe pertenecer a la categoria explorada
    categorias_recomendadas = set()
    for pub in recomendaciones:
        for cat in pub.categorias.all():
            categorias_recomendadas.add(cat.nombre)

    context.test.assertIn(
        context.cat_ciencias.nombre,
        categorias_recomendadas,
        'Las recomendaciones no incluyen la categoria mas explorada por el usuario.',
    )


@then('no aparece contenido que el usuario ya haya consumido')
def step_no_aparece_contenido_consumido(context):
    """
    Verifica que el contenido ya leido por el usuario no aparece en las
    recomendaciones. RN-REC-03.
    """
    recomendaciones = list(context.response.context['recomendaciones'])
    ids_recomendados = [pub.pk for pub in recomendaciones]

    context.test.assertNotIn(
        context.libro_leido.pk,
        ids_recomendados,
        'Un libro ya consumido aparece entre las recomendaciones.',
    )


# ---------------------------------------------------------------------------
# Escenario: Las recomendaciones consideran metricas colectivas de actividad
# (RN-REC-02)
# ---------------------------------------------------------------------------

@given('que el usuario ha explorado contenido en la plataforma')
def step_usuario_ha_explorado_contenido(context):
    """
    Crea un historial minimo para que el usuario no caiga en arranque en frio
    y crea publicaciones con metricas distintas para verificar que las de
    mayor actividad colectiva se prioricen.
    """
    from src.recomendaciones.models import HistorialLectura

    cat_tecnologia = Categoria.objects.create(nombre='Tecnologia')

    otro_autor = User.objects.create_user(
        username='autor_metricas',
        email='autor_metricas@ejemplo.com',
        password='password123',
        first_name='Autor Metricas',
    )
    PerfilUsuario.objects.create(
        usuario=otro_autor,
        rol=PerfilUsuario.PROFESOR,
    )

    # Libro con historial para que no sea arranque en frio
    libro_base, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro base explorado',
        categorias=[cat_tecnologia],
    )
    HistorialLectura.objects.create(
        usuario=context.usuario_principal,
        publicacion=Publicacion.objects.get(pk=libro_base.pk),
    )

    # Libro con metricas altas (debe priorizarse)
    libro_popular, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro muy popular',
        categorias=[cat_tecnologia],
        visualizaciones=500,
        descargas=200,
        republicaciones=50,
    )
    context.libro_popular = libro_popular

    # Libro con metricas bajas
    libro_poco_popular, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro poco popular',
        categorias=[cat_tecnologia],
        visualizaciones=1,
        descargas=0,
        republicaciones=0,
    )
    context.libro_poco_popular = libro_poco_popular


@then('el sistema incluye publicaciones con alto número de visualizaciones, republicaciones y descargas como señal de relevancia')
def step_incluye_publicaciones_alta_actividad(context):
    """
    Verifica que las publicaciones con mayor actividad colectiva aparecen
    en las recomendaciones con mayor prioridad. RN-REC-02.
    """
    context.test.assertEqual(
        context.response.status_code,
        200,
        'La seccion de recomendaciones no respondio con HTTP 200.',
    )

    recomendaciones = list(context.response.context['recomendaciones'])
    ids_recomendados = [pub.pk for pub in recomendaciones]

    context.test.assertIn(
        context.libro_popular.pk,
        ids_recomendados,
        'El libro con alta actividad colectiva no aparece en las recomendaciones.',
    )

    # El libro popular debe aparecer antes que el poco popular
    context.test.assertIn(
        context.libro_poco_popular.pk,
        ids_recomendados,
        'El libro poco popular no aparece en las recomendaciones para ser comparado.',
    )
    indice_popular = ids_recomendados.index(context.libro_popular.pk)
    indice_poco_popular = ids_recomendados.index(context.libro_poco_popular.pk)
    context.test.assertLess(
        indice_popular,
        indice_poco_popular,
        'El libro popular no tiene mayor prioridad que el poco popular en las recomendaciones.',
    )


# ---------------------------------------------------------------------------
# Escenario: Usuario sin actividad suficiente recibe recomendaciones generales
# (RN-REC-05 — US-27 Arranque en frio)
# ---------------------------------------------------------------------------

@given('que el usuario no tiene historial de actividad suficiente en la plataforma')
def step_usuario_sin_historial(context):
    """
    Verifica que el usuario principal no tiene historial de lectura y
    crea contenido con distintas metricas de consumo para validar que
    el sistema recomiende el contenido mas popular de la plataforma.
    RN-REC-05: Arranque en frio.
    """
    from src.recomendaciones.models import HistorialLectura

    # Asegurar que el usuario no tiene historial de lectura
    HistorialLectura.objects.filter(usuario=context.usuario_principal).delete()

    otro_autor = User.objects.create_user(
        username='autor_arranque_frio',
        email='autor_frio@ejemplo.com',
        password='password123',
        first_name='Autor Arranque Frio',
    )
    PerfilUsuario.objects.create(
        usuario=otro_autor,
        rol=PerfilUsuario.ESTUDIANTE,
    )

    cat_general = Categoria.objects.create(nombre='General')

    # Libro con alto consumo (debe aparecer primero)
    libro_alto_consumo, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro de alto consumo general',
        categorias=[cat_general],
        visualizaciones=1000,
        descargas=500,
        republicaciones=100,
    )
    context.libro_alto_consumo = libro_alto_consumo

    # Libro con bajo consumo (debe aparecer despues)
    libro_bajo_consumo, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro de bajo consumo general',
        categorias=[cat_general],
        visualizaciones=5,
        descargas=1,
        republicaciones=0,
    )
    context.libro_bajo_consumo = libro_bajo_consumo

    # Coleccion publicada para verificar que tambien se incluyen colecciones
    coleccion_popular = _crear_coleccion_publicada(
        autor=otro_autor,
        titulo='Coleccion popular general',
        categorias=[cat_general],
    )
    context.coleccion_popular = coleccion_popular


@then('el sistema presenta el contenido de mayor consumo general de la plataforma')
def step_presenta_contenido_mayor_consumo(context):
    """
    Verifica que el feed de recomendaciones muestra contenido basado en el
    mayor consumo general (visualizaciones y descargas) cuando el usuario
    no tiene historial suficiente. RN-REC-05.
    """
    context.test.assertEqual(
        context.response.status_code,
        200,
        'La seccion de recomendaciones no respondio con HTTP 200.',
    )

    recomendaciones = list(context.response.context['recomendaciones'])
    context.test.assertGreater(
        len(recomendaciones),
        0,
        'No se generaron recomendaciones generales para un usuario sin historial.',
    )

    ids_recomendados = [pub.pk for pub in recomendaciones]

    # El contenido de alto consumo debe estar presente
    context.test.assertIn(
        context.libro_alto_consumo.pk,
        ids_recomendados,
        'El libro de alto consumo general no aparece en las recomendaciones de arranque en frio.',
    )

    # El contenido de alto consumo debe aparecer antes que el de bajo consumo
    context.test.assertIn(
        context.libro_bajo_consumo.pk,
        ids_recomendados,
        'El contenido de bajo consumo no aparece en las recomendaciones de arranque en frio.',
    )
    indice_alto = ids_recomendados.index(context.libro_alto_consumo.pk)
    indice_bajo = ids_recomendados.index(context.libro_bajo_consumo.pk)
    context.test.assertLess(
        indice_alto,
        indice_bajo,
        'El contenido de mayor consumo no tiene prioridad sobre el de menor consumo en arranque en frio.',
    )


# ---------------------------------------------------------------------------
# Escenario: El contenido ya consumido no aparece entre las recomendaciones
# (RN-REC-03 - escenario especifico)
# ---------------------------------------------------------------------------

@given('que el usuario ha leído un libro previamente')
def step_usuario_leyo_libro(context):
    """Crea un libro que ya fue leido y otro no leido en la misma categoria."""
    from src.recomendaciones.models import HistorialLectura

    cat_literatura = Categoria.objects.create(nombre='Literatura')

    otro_autor = User.objects.create_user(
        username='autor_consumido',
        email='autor_consumido@ejemplo.com',
        password='password123',
        first_name='Autor Consumido',
    )
    PerfilUsuario.objects.create(
        usuario=otro_autor,
        rol=PerfilUsuario.ESTUDIANTE,
    )

    libro_ya_leido, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro ya leido previamente',
        categorias=[cat_literatura],
    )
    HistorialLectura.objects.create(
        usuario=context.usuario_principal,
        publicacion=Publicacion.objects.get(pk=libro_ya_leido.pk),
    )
    context.libro_ya_leido = libro_ya_leido

    # Libro no leido para que existan recomendaciones
    libro_no_leido, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro no leido de Literatura',
        categorias=[cat_literatura],
    )
    context.libro_no_leido = libro_no_leido


@then('ese libro no aparece entre las sugerencias')
def step_libro_no_aparece_en_sugerencias(context):
    """Verifica que el libro previamente leido no esta en las recomendaciones."""
    context.test.assertEqual(
        context.response.status_code,
        200,
        'La seccion de recomendaciones no respondio con HTTP 200.',
    )

    recomendaciones = list(context.response.context['recomendaciones'])
    ids_recomendados = [pub.pk for pub in recomendaciones]

    context.test.assertNotIn(
        context.libro_ya_leido.pk,
        ids_recomendados,
        'El libro ya leido aparece entre las sugerencias cuando deberia estar excluido.',
    )


# ---------------------------------------------------------------------------
# Escenario: Descartar una recomendacion la excluye de sugerencias futuras
# (RN-REC-04 — US-28)
# ---------------------------------------------------------------------------

@given('que el usuario visualiza una recomendación en su sección')
def step_usuario_visualiza_recomendacion(context):
    """Crea contenido recomendable y verifica que aparece en la seccion.

    Se genera historial de lectura para que el usuario no caiga en arranque
    en frio y se crea un libro candidato en la misma area tematica que debe
    aparecer como recomendacion antes de ser descartado.
    RN-REC-04: Prerequisito — el contenido debe ser visible inicialmente.
    """
    from src.recomendaciones.models import HistorialLectura

    cat_biologia = Categoria.objects.create(nombre='Biologia')

    otro_autor = User.objects.create_user(
        username='autor_descarte',
        email='autor_descarte@ejemplo.com',
        password='password123',
        first_name='Autor Descarte',
    )
    PerfilUsuario.objects.create(
        usuario=otro_autor,
        rol=PerfilUsuario.ESTUDIANTE,
    )

    # Lectura previa para generar historial (evitar arranque en frio)
    libro_historial, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro historial descarte',
        categorias=[cat_biologia],
    )
    HistorialLectura.objects.create(
        usuario=context.usuario_principal,
        publicacion=Publicacion.objects.get(pk=libro_historial.pk),
    )

    # Libro candidato que debe aparecer como recomendacion
    libro_candidato, pub_candidata = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro candidato a descartar',
        categorias=[cat_biologia],
    )
    context.libro_a_descartar = libro_candidato
    context.publicacion_a_descartar = pub_candidata

    # Verificar que el contenido aparece inicialmente en las recomendaciones
    from django.urls import reverse

    url = reverse('recomendaciones:recomendaciones')
    response = context.test.client.get(url)
    recomendaciones = list(response.context['recomendaciones'])
    ids_recomendados = [pub.pk for pub in recomendaciones]

    context.test.assertIn(
        pub_candidata.pk,
        ids_recomendados,
        'El contenido candidato no aparece en las recomendaciones iniciales; '
        'no se puede validar el descarte.',
    )


@when('el usuario descarta esa recomendación')
def step_usuario_descarta_recomendacion(context):
    """Realiza la accion de descarte sobre la recomendacion candidata.

    Envia una peticion POST al endpoint de descarte con el identificador
    de la publicacion. El sistema debe registrar un DescarteRecomendacion
    permanente asociado al usuario y la publicacion.
    RN-REC-04: El descarte queda registrado para ajustar recomendaciones futuras.
    US-28: El descarte se asocia a DescarteRecomendacion de forma permanente.
    """
    from django.urls import reverse

    url = reverse(
        'recomendaciones:descartar_recomendacion',
        kwargs={'publicacion_id': context.publicacion_a_descartar.pk},
    )
    context.response = context.test.client.post(url)


@then('ese contenido no vuelve a aparecer en recomendaciones futuras')
def step_contenido_no_aparece_en_futuras(context):
    """Verifica que el contenido descartado se excluye de recomendaciones.

    Se comprueban dos condiciones derivadas de los criterios de aceptacion:
    1. El contenido descartado ya no aparece en el feed de recomendaciones
       (US-28 CA-1).
    2. El descarte quedo registrado de forma permanente en el modelo
       DescarteRecomendacion (US-28 CA-2, RN-REC-04).
    """
    from src.recomendaciones.models import DescarteRecomendacion
    from django.urls import reverse

    # CA-2: El descarte se registro de forma permanente
    descarte_existe = DescarteRecomendacion.objects.filter(
        usuario=context.usuario_principal,
        publicacion=context.publicacion_a_descartar,
    ).exists()
    context.test.assertTrue(
        descarte_existe,
        'No se registro el descarte de forma permanente en DescarteRecomendacion.',
    )

    # CA-1: El contenido descartado ya no aparece en las recomendaciones
    url = reverse('recomendaciones:recomendaciones')
    response = context.test.client.get(url)

    context.test.assertEqual(
        response.status_code,
        200,
        'La seccion de recomendaciones no respondio con HTTP 200 tras el descarte.',
    )

    recomendaciones = list(response.context['recomendaciones'])
    ids_recomendados = [pub.pk for pub in recomendaciones]

    context.test.assertNotIn(
        context.publicacion_a_descartar.pk,
        ids_recomendados,
        'El contenido descartado sigue apareciendo en las recomendaciones '
        'cuando deberia estar excluido (RN-REC-04).',
    )


# ---------------------------------------------------------------------------
# Escenario: La actividad reciente tiene mayor peso en las recomendaciones
# (RN-REC-08)
# ---------------------------------------------------------------------------

@given('que el usuario tiene historial de lectura de períodos distintos')
def step_historial_periodos_distintos(context):
    """
    Crea lecturas en dos categorias distintas: una antigua y otra reciente.
    Las recomendaciones deben priorizar la categoria de la lectura reciente.
    """
    from src.recomendaciones.models import HistorialLectura

    cat_matematicas = Categoria.objects.create(nombre='Matematicas')
    cat_filosofia = Categoria.objects.create(nombre='Filosofia')

    otro_autor = User.objects.create_user(
        username='autor_periodos',
        email='autor_periodos@ejemplo.com',
        password='password123',
        first_name='Autor Periodos',
    )
    PerfilUsuario.objects.create(
        usuario=otro_autor,
        rol=PerfilUsuario.PROFESOR,
    )

    # Lectura antigua en Matematicas
    libro_antiguo, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro antiguo de Matematicas',
        categorias=[cat_matematicas],
    )
    historial_antiguo = HistorialLectura.objects.create(
        usuario=context.usuario_principal,
        publicacion=Publicacion.objects.get(pk=libro_antiguo.pk),
    )
    # Se fuerza la fecha antigua con update para no activar auto_now_add
    ahora = timezone.now()
    HistorialLectura.objects.filter(pk=historial_antiguo.pk).update(
        fecha=ahora - timezone.timedelta(days=90)
    )

    # Lectura reciente en Filosofia
    libro_reciente, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro reciente de Filosofia',
        categorias=[cat_filosofia],
    )
    HistorialLectura.objects.create(
        usuario=context.usuario_principal,
        publicacion=Publicacion.objects.get(pk=libro_reciente.pk),
    )

    # Libros candidatos a recomendacion en ambas categorias
    libro_candidato_mat, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Candidato de Matematicas',
        categorias=[cat_matematicas],
    )
    libro_candidato_fil, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Candidato de Filosofia',
        categorias=[cat_filosofia],
    )

    context.cat_matematicas = cat_matematicas
    context.cat_filosofia = cat_filosofia
    context.libro_candidato_mat = libro_candidato_mat
    context.libro_candidato_fil = libro_candidato_fil


@then('el sistema prioriza recomendaciones relacionadas con la actividad más reciente del usuario')
def step_prioriza_actividad_reciente(context):
    """
    Verifica que la categoria de la lectura reciente (Filosofia) tiene mayor
    peso que la categoria de la lectura antigua (Matematicas). RN-REC-08.
    """
    context.test.assertEqual(
        context.response.status_code,
        200,
        'La seccion de recomendaciones no respondio con HTTP 200.',
    )

    recomendaciones = list(context.response.context['recomendaciones'])
    ids_recomendados = [pub.pk for pub in recomendaciones]

    context.test.assertGreater(
        len(recomendaciones),
        0,
        'No se generaron recomendaciones para verificar la prioridad temporal.',
    )

    # El candidato de Filosofia (reciente) debe aparecer antes que el de Matematicas (antiguo)
    context.test.assertIn(
        context.libro_candidato_fil.pk,
        ids_recomendados,
        'El candidato de la categoria reciente (Filosofia) no aparece en las recomendaciones.',
    )
    context.test.assertIn(
        context.libro_candidato_mat.pk,
        ids_recomendados,
        'El candidato de la categoria antigua (Matematicas) no aparece en las recomendaciones.',
    )
    indice_filosofia = ids_recomendados.index(context.libro_candidato_fil.pk)
    indice_matematicas = ids_recomendados.index(context.libro_candidato_mat.pk)
    context.test.assertLess(
        indice_filosofia,
        indice_matematicas,
        'Las recomendaciones de la actividad reciente no tienen mayor prioridad que las antiguas.',
    )


# ---------------------------------------------------------------------------
# Esquema del escenario: Explorar recomendaciones filtrando por tipo de contenido
# (RN-REC-07)
# ---------------------------------------------------------------------------

@given('que el usuario se encuentra en la sección de recomendaciones')
def step_usuario_en_seccion_recomendaciones(context):
    """
    Prepara datos con libros y colecciones para que el filtrado tenga
    contenido sobre el cual operar.
    """
    from src.recomendaciones.models import HistorialLectura

    cat_ingenieria = Categoria.objects.create(nombre='Ingenieria')

    otro_autor = User.objects.create_user(
        username='autor_filtros',
        email='autor_filtros@ejemplo.com',
        password='password123',
        first_name='Autor Filtros',
    )
    PerfilUsuario.objects.create(
        usuario=otro_autor,
        rol=PerfilUsuario.ESTUDIANTE,
    )

    # Crear historial para que no sea arranque en frio
    libro_historial, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro historial filtros',
        categorias=[cat_ingenieria],
    )
    HistorialLectura.objects.create(
        usuario=context.usuario_principal,
        publicacion=Publicacion.objects.get(pk=libro_historial.pk),
    )

    # Libro candidato a recomendacion
    libro_rec, _ = _crear_libro_publicado(
        autor=otro_autor,
        titulo='Libro recomendable de Ingenieria',
        categorias=[cat_ingenieria],
    )
    context.libro_recomendable = libro_rec

    # Coleccion candidata a recomendacion
    coleccion_rec = _crear_coleccion_publicada(
        autor=otro_autor,
        titulo='Coleccion recomendable de Ingenieria',
        categorias=[cat_ingenieria],
    )
    context.coleccion_recomendable = coleccion_rec

    # Acceder a la seccion para tener la respuesta base
    from django.urls import reverse
    url = reverse('recomendaciones:recomendaciones')
    context.response = context.test.client.get(url)


@then('el sistema muestra únicamente sugerencias de {tipo_contenido}')
def step_muestra_unicamente_tipo(context, tipo_contenido):
    """
    Verifica que al filtrar, el sistema solo devuelve contenido del tipo
    solicitado. RN-REC-07.
    """
    from django.urls import reverse

    url = reverse('recomendaciones:recomendaciones')
    context.response = context.test.client.get(url, {'tipo': tipo_contenido})

    context.test.assertEqual(
        context.response.status_code,
        200,
        'La seccion de recomendaciones filtrada no respondio con HTTP 200.',
    )

    recomendaciones = list(context.response.context['recomendaciones'])
    ids_recomendados = [pub.pk for pub in recomendaciones]

    tipo_esperado = Publicacion.LIBRO if tipo_contenido == 'libros' else Publicacion.COLECCION
    
    # Primero verificar que el elemento esperado por el filtro esta presente
    if tipo_esperado == Publicacion.LIBRO:
        context.test.assertIn(context.libro_recomendable.pk, ids_recomendados)
    else:
        context.test.assertIn(context.coleccion_recomendable.pk, ids_recomendados)

    for pub in recomendaciones:
        context.test.assertEqual(
            pub.tipo,
            tipo_esperado,
            f'Se encontro contenido de tipo "{pub.tipo}" cuando se filtro por "{tipo_contenido}".',
        )


@then('no aparece el otro tipo de contenido en esa vista')
def step_no_aparece_otro_tipo(context):
    """
    Verifica que el tipo de contenido opuesto al filtro aplicado no esta
    presente en las recomendaciones.
    """
    recomendaciones = list(context.response.context['recomendaciones'])
    tipos_presentes = set(pub.tipo for pub in recomendaciones)

    # No deben coexistir ambos tipos en la misma vista filtrada
    context.test.assertLessEqual(
        len(tipos_presentes),
        1,
        'Se encontraron ambos tipos de contenido (libro y coleccion) en una vista filtrada.',
    )
