from behave import given, when, then
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from src.materiales.models import Libro, Categoria

User = get_user_model()


# ---------------------------------------------------------------------------
# Escenario: Publicar un libro que supera la validacion automatica de contenido
# ---------------------------------------------------------------------------

@given('que el usuario ha preparado un libro con título, portada, contenido textual y categoría')
def step_libro_requisitos_completos(context):
    context.categoria = Categoria.objects.create(nombre='Matemáticas')
    context.datos_libro = {
        'titulo': 'Algebra Lineal Fundamental',
        'portada': SimpleUploadedFile(
            'portada_algebra.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
        'contenido_texto': (
            'El algebra lineal es una rama de las matematicas que estudia '
            'conceptos como vectores, matrices, sistemas de ecuaciones lineales '
            'y transformaciones lineales. Es fundamental en ingenieria, fisica '
            'y ciencias de la computacion. Los espacios vectoriales proporcionan '
            'la estructura algebraica necesaria para modelar problemas en '
            'multiples dimensiones.'
        ),
        'categorias': [context.categoria.id],
        'numero_paginas': 100,
    }


@given('el contenido es enriquecido, tiene sentido y guarda relación con la categoría')
def step_contenido_enriquecido_y_relacionado(context):
    # El contenido preparado en el paso anterior ya es academicamente valido
    # y guarda relacion con la categoria 'Matematicas'. Se verifica aca.
    context.test.assertIn(
        'Matemáticas',
        context.categoria.nombre,
        "La categoria debe ser relevante para el contenido del libro.",
    )
    context.test.assertTrue(
        len(context.datos_libro['contenido_texto']) > 50,
        "El contenido debe ser suficientemente extenso para ser enriquecido.",
    )


@given('las imágenes y la portada tienen relación con el contenido')
def step_imagenes_relacionadas_con_contenido(context):
    # La portada fue preparada con un nombre descriptivo acorde al contenido
    context.test.assertIsNotNone(
        context.datos_libro['portada'],
        "La portada debe estar presente para la validacion de imagenes.",
    )


@when('el usuario solicita publicar el libro')
def step_solicita_publicar(context):
    from unittest.mock import patch
    
    def mock_validar(self, libro):
        titulo = libro.titulo
        if 'Recetas de Cocina' in titulo:
            return {'aprobado': False, 'mensaje': 'El titulo y contenido del libro no guardan relacion con la categoria.'}
        if 'Introduccion a Python' in titulo:
            return {'aprobado': False, 'mensaje': 'Las imagenes no tienen relacion con el tema del libro.'}
        return {'aprobado': True, 'mensaje': ''}

    with patch('src.materiales.validacion_contenido.ValidadorContenido._validar_tematica_e_imagenes_ia', new=mock_validar):
        context.libro = Libro.objects.create(
            titulo=context.datos_libro['titulo'],
            contenido_texto=context.datos_libro['contenido_texto'],
            numero_paginas=context.datos_libro['numero_paginas'],
            autor=context.usuario_principal,
        )
        context.libro.portada.save(
            context.datos_libro['portada'].name,
            context.datos_libro['portada'],
        )
        context.libro.categorias.add(context.categoria)

        # Paso 1: Publicar el libro (valida requisitos y contenido)
        resultado_bool, mensaje = context.libro.publicar()
    context.resultado_publicacion = resultado_bool
    context.resultado = resultado_bool  # Necesario para steps compartidos
    context.resultado_validacion = {'aprobado': resultado_bool, 'mensaje': mensaje}


@then('el sistema valida el contenido automáticamente de forma exitosa')
def step_valida_contenido_exitosa(context):
    mensaje_error = context.resultado_validacion.get('mensaje', 'Sin mensaje de error') if not context.resultado_publicacion else ''
    context.test.assertTrue(
        context.resultado_publicacion,
        f"La validacion automatica deberia ser exitosa para contenido academico valido. Detalle: {mensaje_error}"
    )


@then('el libro pasa a estado "Publicado" visible para la comunidad académica')
def step_libro_publicado_visible(context):
    context.libro.refresh_from_db()
    context.test.assertEqual(
        context.libro.estado,
        Libro.PUBLICADO,
        "El libro debe estar en estado 'Publicado' tras superar la validacion.",
    )


# ---------------------------------------------------------------------------
# Escenario: Rechazo de publicacion por contenido sin sentido
# ---------------------------------------------------------------------------

@given('que el usuario ha preparado un libro cuyo texto carece de sentido o es texto de relleno')
def step_libro_contenido_sin_sentido(context):
    context.categoria = Categoria.objects.create(nombre='Ciencias')
    context.datos_libro = {
        'titulo': 'Libro de Ciencias Naturales',
        'portada': SimpleUploadedFile(
            'portada_ciencias.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
        'contenido_texto': (
            'asdf jkl qwerty zxcv lorem ipsum dolor sit amet bla bla bla '
            'xxx yyy zzz aaa bbb ccc ddd eee fff ggg hhh iii jjj kkk lll '
            'mnop qrst uvwx yzab cdef ghij klmn opqr stuv wxyz 1234 5678 '
            'texto sin sentido alguno para rellenar espacio sin significado.'
        ),
        'categorias': [context.categoria.id],
        'numero_paginas': 50,
    }


# ---------------------------------------------------------------------------
# Escenario: Rechazo de publicacion por falta de relacion tematica
# ---------------------------------------------------------------------------

@given('que el usuario ha preparado un libro donde el contenido no está apegado a la categoría o el título no tiene relación con el contenido')
def step_libro_sin_relacion_tematica(context):
    context.categoria = Categoria.objects.create(nombre='Matemáticas')
    context.datos_libro = {
        'titulo': 'Recetas de Cocina Italiana',
        'portada': SimpleUploadedFile(
            'portada_cocina.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
        'contenido_texto': (
            'La pasta carbonara es un plato tradicional de la cocina italiana '
            'que se prepara con guanciale, huevos, queso pecorino romano y '
            'pimienta negra. Se debe cocinar la pasta al dente y mezclar con '
            'la salsa fuera del fuego para evitar que los huevos se cuajen. '
            'El risotto milanés lleva azafran y se cocina lentamente.'
        ),
        'categorias': [context.categoria.id],
        'numero_paginas': 80,
    }


# ---------------------------------------------------------------------------
# Escenario: Rechazo de publicacion por imagenes no relacionadas al contenido
# ---------------------------------------------------------------------------

@given('que el usuario ha preparado un libro donde las imágenes o la portada no tienen relación con el contenido textual')
def step_libro_imagenes_no_relacionadas(context):
    context.categoria = Categoria.objects.create(nombre='Programación')
    context.datos_libro = {
        'titulo': 'Introduccion a Python',
        'portada': SimpleUploadedFile(
            'portada_paisaje_playa.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
        'contenido_texto': (
            'Python es un lenguaje de programacion interpretado de alto nivel '
            'con tipado dinamico. Se utiliza ampliamente en desarrollo web, '
            'ciencia de datos, inteligencia artificial y automatizacion. '
            'Las estructuras de datos fundamentales incluyen listas, '
            'diccionarios, tuplas y conjuntos.'
        ),
        'categorias': [context.categoria.id],
        'numero_paginas': 120,
        # El nombre de la portada indica un paisaje de playa, no tiene
        # relacion con un libro de programacion
        'descripcion_portada': 'Fotografia de una playa tropical con palmeras',
    }


# ---------------------------------------------------------------------------
# Steps compartidos para escenarios de rechazo de validacion automatica
# ---------------------------------------------------------------------------

@then('el sistema rechaza la validación automática')
def step_rechaza_validacion_automatica(context):
    context.test.assertFalse(
        context.resultado_publicacion,
        "La validacion automatica deberia rechazar el contenido.",
    )
    context.test.assertFalse(
        context.resultado_validacion['aprobado'],
        "El resultado del validador debe indicar rechazo.",
    )


@then('el libro no pasa a estado "Publicado"')
def step_libro_no_publicado_validacion(context):
    context.libro.refresh_from_db()
    context.test.assertNotEqual(
        context.libro.estado,
        Libro.PUBLICADO,
        "El libro NO debe estar en estado 'Publicado' tras fallar la validacion.",
    )
    context.test.assertEqual(
        context.libro.estado,
        Libro.BORRADOR,
        "El libro debe regresar a estado 'Borrador' tras fallar la validacion.",
    )


@then('se notifica al autor detallando que el contenido carece de sentido o no es enriquecido')
def step_notificacion_contenido_sin_sentido(context):
    from src.feed.models import Notificacion
    notificacion = Notificacion.objects.filter(
        usuario=context.usuario_principal,
    ).last()

    context.test.assertIsNotNone(
        notificacion,
        "Debe existir una notificacion para el autor sobre el rechazo.",
    )
    context.test.assertIn(
        'contenido',
        notificacion.mensaje.lower(),
        "La notificacion debe detallar que el problema es con el contenido.",
    )


@then('se notifica al autor detallando la falta de relación temática entre título, contenido y categoría')
def step_notificacion_falta_relacion_tematica(context):
    from src.feed.models import Notificacion
    notificacion = Notificacion.objects.filter(
        usuario=context.usuario_principal,
    ).last()

    context.test.assertIsNotNone(
        notificacion,
        "Debe existir una notificacion para el autor sobre el rechazo.",
    )
    mensaje = notificacion.mensaje.lower()
    palabras_clave = ['relación', 'relacion', 'temática', 'tematica', 'categoría', 'categoria', 'semántica', 'semantica', 'coherencia', 'matemáticas', 'recetas', 'cocina']
    context.test.assertTrue(
        any(p in mensaje for p in palabras_clave),
        f"La notificacion debe detallar la falta de relacion tematica. Mensaje recibido: {mensaje}"
    )


@then('se notifica al autor detallando que las imágenes no son coherentes con el contenido')
def step_notificacion_imagenes_no_coherentes(context):
    from src.feed.models import Notificacion
    notificacion = Notificacion.objects.filter(
        usuario=context.usuario_principal,
    ).last()

    context.test.assertIsNotNone(
        notificacion,
        "Debe existir una notificacion para el autor sobre el rechazo.",
    )
    mensaje = notificacion.mensaje.lower()
    palabras_clave = ['imagen', 'imágenes', 'portada', 'foto', 'fotografía', 'visual']
    context.test.assertTrue(
        any(p in mensaje for p in palabras_clave),
        f"La notificacion debe detallar que las imagenes no son coherentes. Mensaje recibido: {mensaje}"
    )


# ---------------------------------------------------------------------------
# Esquema del escenario: No se puede publicar un libro con requisitos incompletos
# ---------------------------------------------------------------------------

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
        autor=context.usuario_principal,
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
    resultado_bool, mensaje = libro.publicar()
    context.resultado = resultado_bool


@then('el libro no queda publicado')
def step_libro_no_publicado(context):
    context.libro.refresh_from_db()
    context.test.assertEqual(
        context.libro.estado,
        Libro.BORRADOR,
        "El libro debe permanecer en estado 'Borrador' al fallar la validacion.",
    )


# ---------------------------------------------------------------------------
# Escenario: No se puede publicar un libro compuesto unicamente por imagenes
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Escenario: No se puede publicar un libro que supera el limite de paginas
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Escenarios de edicion y publicacion
# ---------------------------------------------------------------------------

@given('que el usuario tiene un libro publicado en su perfil')
def step_usuario_libro_publicado(context):
    context.categoria = Categoria.objects.create(nombre='Física')
    context.libro = Libro.objects.create(
        titulo='Introducción a la Física',
        contenido_texto='Contenido de física enriquecido y relevante',
        numero_paginas=150,
        autor=context.usuario_principal,
        estado=Libro.PUBLICADO
    )
    context.libro.categorias.add(context.categoria)

    # Un libro publicado ya cuenta con su entrada en el feed, tal como la
    # crearia Libro.publicar(). Se replica aqui para no depender de ese metodo.
    from src.feed.models import Publicacion
    Publicacion.objects.get_or_create(libro=context.libro)


@when('el usuario modifica los metadatos del libro')
def step_usuario_modifica_metadatos(context):
    context.libro.titulo = 'Física Avanzada'
    context.libro.editar(usuario_editor=context.usuario_principal)


@then('el libro pasa a estado Borrador')
def step_libro_pasa_estado_revision(context):
    context.libro.refresh_from_db()
    context.test.assertEqual(
        context.libro.estado,
        Libro.BORRADOR,
        "El libro debe regresar a estado Borrador tras su edición."
    )


@then('deja de ser visible para otros usuarios hasta superar la validación automática')
def step_libro_no_visible(context):
    context.test.assertNotEqual(
        context.libro.estado,
        Libro.PUBLICADO,
        "El libro ya no debe ser visible públicamente."
    )


@when('el usuario modifica el contenido textual del libro')
def step_usuario_modifica_contenido(context):
    context.libro.contenido_texto = 'Nuevo contenido actualizado'
    context.libro.editar(usuario_editor=context.usuario_principal)


# ---------------------------------------------------------------------------
# Escenario: Retirar un libro publicado lo hace invisible para otros usuarios
# ---------------------------------------------------------------------------

@when('el usuario retira la publicación del libro')
def step_usuario_retira_publicacion(context):
    context.libro.retirar()


@then('el libro deja de estar disponible para el resto de la comunidad')
def step_libro_no_disponible_comunidad(context):
    context.libro.refresh_from_db()
    context.test.assertEqual(
        context.libro.estado,
        Libro.RETIRADO,
        "El libro debe quedar en estado 'Retirado' tras retirarlo.",
    )

    from django.urls import reverse
    response = context.test.client.get(reverse('materiales:inicio'))
    libros_visibles = list(response.context['libros'])
    context.test.assertNotIn(
        context.libro,
        libros_visibles,
        "El libro retirado no debe aparecer en la biblioteca general.",
    )


@then('el libro deja de aparecer en el feed de los usuarios que siguen al autor')
def step_libro_no_aparece_en_feed(context):
    from django.urls import reverse
    from src.feed.models import Publicacion, Seguimiento

    seguidor = User.objects.create_user(username='seguidor_del_autor', password='123')
    Seguimiento.objects.create(seguidor=seguidor, seguido=context.usuario_principal)

    context.test.assertFalse(
        Publicacion.objects.filter(libro=context.libro).exists(),
        "La publicación del libro retirado debe eliminarse para que no pueda mostrarse en ningún feed.",
    )

    context.test.client.force_login(seguidor)
    response = context.test.client.get(reverse('feed:feed'))

    if response.status_code == 200:
        material_feed = list(response.context.get('material_feed', []))
        ids_en_feed = [item.pk for item in material_feed if hasattr(item, 'titulo')]
        context.test.assertNotIn(
            context.libro.pk,
            ids_en_feed,
            "El libro retirado no debe aparecer en el feed de sus seguidores.",
        )

    context.test.client.force_login(context.usuario_principal)


@then('el usuario puede seguir accediendo a él desde su propio perfil')
def step_usuario_accede_propio_perfil(context):
    libro_accesible = Libro.objects.filter(
        pk=context.libro.pk,
        autor=context.usuario_principal,
    ).exists()
    context.test.assertTrue(
        libro_accesible,
        "El autor debe poder seguir accediendo a su libro retirado desde su perfil.",
    )


@given('que el usuario está visualizando un libro publicado por otro usuario')
def step_usuario_viendo_libro_ajeno(context):
    otro_usuario = User.objects.create_user(username='otro', password='123')
    context.libro_ajeno = Libro.objects.create(
        titulo='Libro Ajeno',
        contenido_texto='Texto del otro usuario',
        numero_paginas=100,
        autor=otro_usuario,
        estado=Libro.PUBLICADO
    )


@when('el usuario intenta modificar ese libro')
def step_usuario_intenta_modificar_libro_ajeno(context):
    try:
        context.libro_ajeno.editar(usuario_editor=context.usuario_principal)
        context.resultado = True
    except PermissionError:
        context.resultado = False




# ---------------------------------------------------------------------------
# Escenario: Republicar el material de otro usuario preserva la autoría original
# ---------------------------------------------------------------------------

@when('el usuario republica ese libro en su perfil')
def step_usuario_republica_libro(context):
    context.total_libros_antes = Libro.objects.count()
    context.republicaciones_iniciales = context.libro_ajeno.republicaciones
    
    context.republicacion, _ = context.libro_ajeno.republicar(usuario=context.usuario_principal)


@then('el libro aparece en el perfil del usuario como contenido republicado')
def step_libro_aparece_republicado(context):
    context.test.assertEqual(
        Libro.objects.count(),
        context.total_libros_antes,
        "No se debe crear un nuevo registro de Libro al republicar (evita duplicación)."
    )
    
    context.libro_ajeno.refresh_from_db()
    context.test.assertEqual(
        context.libro_ajeno.republicaciones,
        context.republicaciones_iniciales + 1,
        "El contador de republicaciones del libro original debe incrementar en 1."
    )
    
    context.test.assertEqual(
        context.republicacion.republicado_por,
        context.usuario_principal,
        "La republicación debe registrarse para el usuario que la realiza."
    )


@then('la autoría original del libro se conserva visible')
def step_autoria_conserva_visible(context):
    context.test.assertEqual(
        context.republicacion.publicacion.autor,
        context.libro_ajeno.autor,
        "La republicación debe mantener intacta la referencia al autor original."
    )


# ---------------------------------------------------------------------------
# Escenarios: Visualizacion de metricas de interaccion (US-08)
# ---------------------------------------------------------------------------

@given('que el usuario tiene al menos un libro publicado')
def step_usuario_tiene_al_menos_un_libro_publicado(context):
    # Reutiliza la preparacion del libro publicado ya definida para los
    # escenarios de edicion/retiro, evitando duplicar la creacion del libro.
    step_usuario_libro_publicado(context)


@when('el usuario accede al detalle de ese libro')
def step_usuario_accede_detalle_libro(context):
    from django.urls import reverse
    context.test.client.force_login(context.usuario_principal)
    context.response = context.test.client.get(
        reverse('materiales:detalle_libro', kwargs={'pk': context.libro.pk})
    )


@then('puede consultar el número de visualizaciones, republicaciones y descargas')
def step_puede_consultar_metricas(context):
    context.test.assertEqual(
        context.response.status_code,
        200,
        "El autor debe poder acceder al detalle de su propio libro.",
    )

    context.libro.refresh_from_db()
    metricas = context.response.context.get('metricas') if context.response.context else None
    context.test.assertIsNotNone(
        metricas,
        "El detalle del libro debe exponer las métricas de interacción al autor.",
    )
    context.test.assertEqual(
        metricas.get('visualizaciones'),
        context.libro.visualizaciones,
        "Las visualizaciones mostradas deben coincidir con el total acumulado del libro.",
    )
    context.test.assertEqual(
        metricas.get('republicaciones'),
        context.libro.republicaciones,
        "Las republicaciones mostradas deben coincidir con el total acumulado del libro.",
    )
    context.test.assertEqual(
        metricas.get('descargas'),
        context.libro.descargas,
        "Las descargas mostradas deben coincidir con el total acumulado del libro.",
    )


@when('otro usuario distinto al autor accede al detalle de ese libro')
def step_otro_usuario_accede_detalle_libro(context):
    from django.urls import reverse
    context.usuario_no_autor = User.objects.create_user(
        username='usuario_no_autor', password='password123',
    )
    context.test.client.force_login(context.usuario_no_autor)
    context.response = context.test.client.get(
        reverse('materiales:detalle_libro', kwargs={'pk': context.libro.pk})
    )


@then('no puede consultar las métricas de visualizaciones, republicaciones y descargas')
def step_no_puede_consultar_metricas(context):
    if context.response.status_code == 200:
        metricas = context.response.context.get('metricas') if context.response.context else None
        context.test.assertIsNone(
            metricas,
            "Un usuario distinto al autor no debe recibir las métricas del libro.",
        )
    else:
        context.test.assertIn(
            context.response.status_code,
            (403, 404),
            "El acceso de un usuario no autor a las métricas debe ser rechazado.",
        )

# ---------------------------------------------------------------------------
# Escenarios de creacion de colecciones
# ---------------------------------------------------------------------------

@given('que el usuario ha preparado una colección con nombre y al menos una categoría temática')
def step_prepara_coleccion_basica(context):
    from src.materiales.models import Categoria
    context.categoria_coleccion, _ = Categoria.objects.get_or_create(nombre='Tecnología')
    context.datos_coleccion = {
        'nombre': 'Colección de Prueba',
        'descripcion': 'Descripción de la colección',
        'categorias': [context.categoria_coleccion.id],
    }


@given('el usuario define la visibilidad de la colección como "{visibilidad}"')
def step_define_visibilidad_param(context, visibilidad):
    context.datos_coleccion['visibilidad'] = visibilidad


@given('el usuario establece un límite máximo de {limite} libros')
def step_define_limite_valido_param(context, limite):
    context.datos_coleccion['limite_libros'] = int(limite)


@when('el usuario crea la colección')
def step_usuario_crea_coleccion(context):
    context.test.client.force_login(context.usuario_principal)
    
    post_data = {
        'nombre': context.datos_coleccion.get('nombre', ''),
        'descripcion': context.datos_coleccion.get('descripcion', ''),
        'visibilidad': context.datos_coleccion.get('visibilidad', 'publica'),
        'limite_libros': context.datos_coleccion.get('limite_libros', 20),
        'categorias': context.datos_coleccion.get('categorias', []),
    }
    
    response = context.test.client.post('/colecciones/crear/', data=post_data)
    
    if response.status_code == 302:
        context.resultado = True
        context.error_creacion = None
        from src.materiales.models import Coleccion
        context.coleccion = Coleccion.objects.filter(creador=context.usuario_principal).last()
    else:
        context.resultado = False
        if hasattr(response, 'context') and response.context and 'form' in response.context and response.context['form'].errors:
            context.error_creacion = str(response.context['form'].errors)
        else:
            context.error_creacion = "Error desconocido o validación fallida"


@then('la colección se crea exitosamente')
def step_coleccion_creada_exitosamente(context):
    context.test.assertTrue(
        context.resultado,
        f"La colección debió crearse exitosamente. Error: {context.error_creacion}"
    )
    context.test.assertIsNotNone(context.coleccion.id)


@then('la colección queda disponible según su visibilidad definida')
def step_coleccion_visibilidad(context):
    context.coleccion.refresh_from_db()
    context.test.assertEqual(
        context.coleccion.visibilidad,
        context.datos_coleccion.get('visibilidad', 'publica'),
        "La visibilidad de la colección no coincide con la definida"
    )


@then('el usuario creador es asignado automáticamente como administrador inicial de la colección')
def step_creador_es_administrador(context):
    es_admin = context.coleccion.es_administrador(context.usuario_principal)
    context.test.assertTrue(
        es_admin,
        "El creador debe ser asignado como administrador inicial."
    )


@given('el usuario intenta establecer un límite máximo de {limite} libros')
def step_intenta_establecer_limite_invalido(context, limite):
    context.datos_coleccion['limite_libros'] = int(limite)


@when('el usuario intenta crear la colección')
def step_intenta_crear_coleccion(context):
    step_usuario_crea_coleccion(context)


@then('la colección no se crea')
def step_coleccion_no_creada(context):
    context.test.assertFalse(
        hasattr(context, 'coleccion') and context.coleccion.id is not None,
        "La colección no debió guardarse."
    )


@then('se notifica que el límite mínimo de libros es {limite}')
def step_notifica_limite_minimo(context, limite):
    context.test.assertIsNotNone(context.error_creacion, "Debe existir un mensaje de error.")
    context.test.assertIn(
        limite,
        context.error_creacion,
        f"El error debe mencionar el límite de {limite} libros."
    )

# ---------------------------------------------------------------------------
# Otros escenarios de colecciones (Categorías, Limites de agregación, Eliminación)
# ---------------------------------------------------------------------------

@given('que el usuario ha preparado una colección con nombre y libros pero sin categoría')
def step_coleccion_sin_categoria(context):
    context.datos_coleccion = {
        'nombre': 'Coleccion Incompleta',
        'categorias': [],
    }



@given('que una colección ha alcanzado su límite máximo de libros')
def step_coleccion_alcanza_limite(context):
    from src.materiales.models import Coleccion, Libro
    context.coleccion = Coleccion.objects.create(
        nombre='Coleccion Limitada',
        creador=context.usuario_principal,
        limite_libros=5
    )
    # Agregar 5 libros
    for i in range(5):
        libro = Libro.objects.create(
            titulo=f'Libro {i}',
            autor=context.usuario_principal
        )
        context.coleccion.libros.add(libro)

@when('el usuario intenta agregar un libro más a esa colección')
def step_agrega_libro_extra(context):
    from src.materiales.models import Libro
    from django.core.exceptions import ValidationError
    context.libro_nuevo = Libro.objects.create(
        titulo='Libro Extra',
        autor=context.usuario_principal
    )
    try:
        context.coleccion.agregar_libro(context.usuario_principal, context.libro_nuevo)
        context.resultado = True
    except ValidationError as e:
        context.resultado = False
        context.error_creacion = str(e)

@then('el libro no se agrega a la colección')
def step_libro_no_agregado(context):
    context.test.assertFalse(context.resultado, "La operación debió ser rechazada.")
    context.test.assertNotIn(
        context.libro_nuevo,
        context.coleccion.libros.all(),
        "El libro no debe estar en la colección."
    )


@given('que el usuario tiene una colección que contiene un libro')
def step_coleccion_contiene_libro(context):
    from src.materiales.models import Coleccion, Libro
    context.coleccion_eliminar = Coleccion.objects.create(
        nombre='Coleccion para eliminar libro',
        creador=context.usuario_principal
    )
    context.libro_a_eliminar = Libro.objects.create(
        titulo='Libro a Eliminar',
        autor=context.usuario_principal,
        estado=Libro.PUBLICADO
    )
    context.coleccion_eliminar.libros.add(context.libro_a_eliminar)

@when('el usuario elimina ese libro de la colección')
def step_elimina_libro_de_coleccion(context):
    try:
        context.coleccion_eliminar.eliminar_libro(context.usuario_principal, context.libro_a_eliminar)
        context.resultado = True
    except Exception as e:
        context.resultado = False
        context.error = e

@then('el libro desaparece de la colección')
def step_libro_desaparece_coleccion(context):
    context.test.assertNotIn(
        context.libro_a_eliminar,
        context.coleccion_eliminar.libros.all(),
        'El libro no debería estar en la colección'
    )

@then('el libro sigue disponible para cualquier usuario en la biblioteca general')
def step_libro_sigue_disponible(context):
    from src.materiales.models import Libro
    libro_en_bd = Libro.objects.filter(id=context.libro_a_eliminar.id).exists()
    context.test.assertTrue(
        libro_en_bd,
        'El libro debe seguir existiendo en la base de datos general'
    )
    context.libro_a_eliminar.refresh_from_db()
    context.test.assertEqual(
        context.libro_a_eliminar.estado,
        Libro.PUBLICADO,
        'El libro debe seguir publicado'
    )
