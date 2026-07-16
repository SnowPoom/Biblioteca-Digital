from behave import given, when, then
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from src.materiales.models import Libro, Categoria, Anotacion
from src.login.models import PerfilUsuario

User = get_user_model()

LIMITE_CARACTERES_ANOTACION = 150


# ---------------------------------------------------------------------------
# Antecedentes
# ---------------------------------------------------------------------------
# El step "que el usuario ha iniciado sesion en la plataforma" ya esta
# definido en feed_actividad_steps.py y behave lo reutiliza automaticamente.

@given('que el usuario ha abierto un libro disponible en la biblioteca')
def step_usuario_abre_libro(context):
    """Crea un libro publicado y lo almacena en el contexto como libro abierto."""
    categoria = Categoria.objects.create(nombre='Ciencias Generales')
    context.libro = Libro.objects.create(
        titulo='Fundamentos de Ciencia',
        contenido_texto=(
            'La ciencia es el conjunto de conocimientos sistematizados '
            'sobre la naturaleza, la sociedad y el pensamiento acumulados '
            'en el curso de la historia.'
        ),
        numero_paginas=120,
        autor=context.usuario_principal,
        estado=Libro.PUBLICADO,
    )
    context.libro.portada.save(
        'portada_ciencias.png',
        SimpleUploadedFile(
            'portada_ciencias.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
    )
    context.libro.categorias.add(categoria)


# ---------------------------------------------------------------------------
# Escenario: Crear una anotacion sobre un fragmento de texto
# RN-ANO-02: Una anotacion se crea seleccionando un fragmento de texto
# ---------------------------------------------------------------------------

@given('que el usuario está leyendo una página del libro')
def step_usuario_leyendo_pagina(context):
    context.fragmento_texto = 'conocimientos sistematizados'


@when('el usuario selecciona un fragmento de texto y elige anotarlo')
def step_selecciona_fragmento_texto(context):
    context.fragmento_seleccionado = context.fragmento_texto
    context.tipo_fragmento = Anotacion.TEXTO


@when('escribe el contenido de la anotación')
def step_escribe_contenido_anotacion(context):
    context.contenido_anotacion = 'Importante para el examen parcial'
    context.anotacion = Anotacion.objects.create(
        usuario=context.usuario_principal,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
        tipo_fragmento=context.tipo_fragmento,
        contenido=context.contenido_anotacion,
    )


@then('la anotación queda asociada a ese fragmento')
def step_anotacion_asociada_fragmento(context):
    anotacion = Anotacion.objects.get(pk=context.anotacion.pk)
    context.test.assertEqual(
        anotacion.fragmento_texto,
        context.fragmento_seleccionado,
        "La anotacion debe estar asociada al fragmento seleccionado.",
    )
    context.test.assertEqual(
        anotacion.libro,
        context.libro,
        "La anotacion debe pertenecer al libro que se esta leyendo.",
    )


@then('el fragmento se muestra visualmente diferenciado en la página')
def step_fragmento_visualmente_diferenciado(context):
    # RN-ANO-05: Los fragmentos anotados deben mostrarse visualmente diferenciados
    anotacion = Anotacion.objects.get(pk=context.anotacion.pk)
    context.test.assertTrue(
        anotacion.esta_activa(),
        "La anotacion activa indica que el fragmento debe resaltarse visualmente.",
    )


# ---------------------------------------------------------------------------
# Escenario: Crear una anotacion sobre una imagen
# RN-ANO-02: En el caso de imagenes, se puede anotar la imagen completa
# ---------------------------------------------------------------------------

@given('que el usuario está en una página que contiene una imagen')
def step_usuario_pagina_con_imagen(context):
    context.identificador_imagen = 'figura_1_celula'


@when('el usuario elige anotar esa imagen')
def step_elige_anotar_imagen(context):
    context.fragmento_seleccionado = context.identificador_imagen
    context.tipo_fragmento = Anotacion.IMAGEN


@then('la anotación queda asociada a esa imagen')
def step_anotacion_asociada_imagen(context):
    anotacion = Anotacion.objects.get(pk=context.anotacion.pk)
    context.test.assertEqual(
        anotacion.fragmento_texto,
        context.identificador_imagen,
        "La anotacion debe estar asociada al identificador de la imagen.",
    )
    context.test.assertEqual(
        anotacion.tipo_fragmento,
        Anotacion.IMAGEN,
        "El tipo de fragmento debe ser 'imagen'.",
    )


# ---------------------------------------------------------------------------
# Escenario: No se puede guardar una anotacion que supera el limite
# RN-ANO-03: Limite maximo de 150 caracteres
# ---------------------------------------------------------------------------

@given('que el usuario ha abierto el campo de anotación sobre un fragmento')
def step_campo_anotacion_abierto(context):
    context.fragmento_seleccionado = 'naturaleza'
    context.tipo_fragmento = Anotacion.TEXTO


@when('el usuario intenta ingresar un texto que supera los 150 caracteres')
def step_intenta_texto_supera_limite(context):
    texto_excesivo = 'A' * (LIMITE_CARACTERES_ANOTACION + 1)
    try:
        anotacion = Anotacion(
            usuario=context.usuario_principal,
            libro=context.libro,
            fragmento_texto=context.fragmento_seleccionado,
            tipo_fragmento=context.tipo_fragmento,
            contenido=texto_excesivo,
        )
        anotacion.full_clean()
        anotacion.save()
        context.resultado_limite = False
    except Exception:
        context.resultado_limite = True


@then('el sistema no permite continuar ingresando texto')
def step_sistema_no_permite_texto(context):
    context.test.assertTrue(
        context.resultado_limite,
        "El sistema debe rechazar anotaciones que superen los 150 caracteres.",
    )


@then('se indica visualmente que se alcanzó el límite')
def step_indicacion_limite_alcanzado(context):
    # Se verifica que no exista la anotacion con contenido excesivo en la BD
    total = Anotacion.objects.filter(
        usuario=context.usuario_principal,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
    ).count()
    context.test.assertEqual(
        total,
        0,
        "No debe existir ninguna anotacion con contenido que supere el limite.",
    )


# ---------------------------------------------------------------------------
# Escenario: Un fragmento con anotacion existente no permite crear una segunda
# RN-ANO-04: Un fragmento puede tener como maximo una anotacion activa
# ---------------------------------------------------------------------------

@given('que el usuario tiene una anotación guardada sobre un fragmento de texto')
def step_anotacion_existente_fragmento_texto(context):
    context.fragmento_seleccionado = 'conocimientos sistematizados'
    context.anotacion = Anotacion.objects.create(
        usuario=context.usuario_principal,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
        tipo_fragmento=Anotacion.TEXTO,
        contenido='Primera anotacion sobre el fragmento',
    )


@when('el usuario selecciona ese mismo fragmento para anotar nuevamente')
def step_selecciona_mismo_fragmento(context):
    try:
        segunda_anotacion = Anotacion(
            usuario=context.usuario_principal,
            libro=context.libro,
            fragmento_texto=context.fragmento_seleccionado,
            tipo_fragmento=Anotacion.TEXTO,
            contenido='Intento de segunda anotacion',
        )
        segunda_anotacion.full_clean()
        segunda_anotacion.save()
        context.anotacion_duplicada_creada = True
    except Exception:
        context.anotacion_duplicada_creada = False

    # Se recupera la anotacion existente para posible edicion
    context.anotacion_existente = Anotacion.objects.get(
        usuario=context.usuario_principal,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
    )


@then('el sistema lleva al usuario a editar la anotación existente')
def step_lleva_a_editar_existente(context):
    context.test.assertIsNotNone(
        context.anotacion_existente,
        "Debe existir la anotacion original para ser editada.",
    )
    context.test.assertEqual(
        context.anotacion_existente.pk,
        context.anotacion.pk,
        "Se debe redirigir a la misma anotacion existente, no a una nueva.",
    )


@then('no permite crear una anotación adicional sobre el mismo fragmento')
def step_no_permite_anotacion_adicional(context):
    context.test.assertFalse(
        context.anotacion_duplicada_creada,
        "No se debe permitir crear una segunda anotacion sobre el mismo fragmento.",
    )
    total = Anotacion.objects.filter(
        usuario=context.usuario_principal,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
    ).count()
    context.test.assertEqual(
        total,
        1,
        "Debe existir exactamente una anotacion por fragmento y usuario.",
    )


# ---------------------------------------------------------------------------
# Escenario: Las anotaciones persisten entre sesiones
# RN-ANO-07: Las anotaciones persisten entre sesiones
# ---------------------------------------------------------------------------

@given('que el usuario tiene anotaciones guardadas en un libro')
def step_usuario_con_anotaciones_en_libro(context):
    context.anotacion_persistente = Anotacion.objects.create(
        usuario=context.usuario_principal,
        libro=context.libro,
        fragmento_texto='sociedad y el pensamiento',
        tipo_fragmento=Anotacion.TEXTO,
        contenido='Revisar para el examen final',
    )


@when('el usuario cierra el libro y vuelve a abrirlo en una sesión posterior')
def step_cierra_y_reabre_libro(context):
    # Simula el cierre y reapertura del libro reconsultando las anotaciones
    context.anotaciones_recuperadas = Anotacion.objects.filter(
        usuario=context.usuario_principal,
        libro=context.libro,
    )


@then('todas las anotaciones siguen visibles en los fragmentos correspondientes')
def step_anotaciones_visibles_tras_sesion(context):
    context.test.assertTrue(
        context.anotaciones_recuperadas.exists(),
        "Las anotaciones deben persistir entre sesiones.",
    )
    context.test.assertIn(
        context.anotacion_persistente,
        context.anotaciones_recuperadas,
        "La anotacion guardada previamente debe estar disponible tras reabrir el libro.",
    )


# ---------------------------------------------------------------------------
# Escenario: Editar una anotacion existente
# RN-ANO-06: El usuario puede editar cualquiera de sus propias anotaciones
# ---------------------------------------------------------------------------

@given('que el usuario tiene una anotación guardada sobre un fragmento')
def step_anotacion_existente_sobre_fragmento(context):
    context.fragmento_seleccionado = 'naturaleza'
    context.anotacion = Anotacion.objects.create(
        usuario=context.usuario_principal,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
        tipo_fragmento=Anotacion.TEXTO,
        contenido='Contenido original de la anotacion',
    )


@when('el usuario accede a esa anotación y modifica su contenido')
def step_modifica_contenido_anotacion(context):
    context.nuevo_contenido = 'Contenido actualizado de la anotacion'
    context.anotacion.editar(context.nuevo_contenido)


@then('la anotación refleja el contenido actualizado')
def step_anotacion_contenido_actualizado(context):
    context.anotacion.refresh_from_db()
    context.test.assertEqual(
        context.anotacion.contenido,
        context.nuevo_contenido,
        "El contenido de la anotacion debe reflejar la modificacion realizada.",
    )


@then('el fragmento permanece visualmente diferenciado')
def step_fragmento_permanece_diferenciado(context):
    context.anotacion.refresh_from_db()
    context.test.assertTrue(
        context.anotacion.esta_activa(),
        "La anotacion debe seguir activa tras la edicion para mantener el resaltado visual.",
    )


# ---------------------------------------------------------------------------
# Escenario: Eliminar una anotacion propia
# RN-ANO-06: El usuario puede eliminar cualquiera de sus propias anotaciones
# ---------------------------------------------------------------------------

@when('el usuario elimina esa anotación')
def step_elimina_anotacion(context):
    context.anotacion_pk = context.anotacion.pk
    context.fragmento_eliminado = context.anotacion.fragmento_texto
    context.anotacion.eliminar()


@then('la anotación desaparece del sistema')
def step_anotacion_desaparece(context):
    existe = Anotacion.objects.filter(pk=context.anotacion_pk).exists()
    context.test.assertFalse(
        existe,
        "La anotacion eliminada no debe existir en el sistema.",
    )


@then('el fragmento deja de estar visualmente diferenciado')
def step_fragmento_sin_diferenciacion(context):
    anotaciones_fragmento = Anotacion.objects.filter(
        usuario=context.usuario_principal,
        libro=context.libro,
        fragmento_texto=context.fragmento_eliminado,
    )
    context.test.assertFalse(
        anotaciones_fragmento.exists(),
        "No deben quedar anotaciones activas en el fragmento eliminado.",
    )


# ---------------------------------------------------------------------------
# Escenario: Las anotaciones de un usuario no son visibles para otros
# RN-ANO-01: Las anotaciones son personales e intransferibles
# ---------------------------------------------------------------------------

@when('otro usuario accede al mismo libro')
def step_otro_usuario_accede_libro(context):
    context.otro_usuario = User.objects.create_user(
        username='otro_lector',
        email='otro@ejemplo.com',
        password='password123',
        first_name='Otro Lector',
    )
    PerfilUsuario.objects.create(
        usuario=context.otro_usuario,
        rol=PerfilUsuario.ESTUDIANTE,
    )
    # Consulta las anotaciones que veria el otro usuario sobre el mismo libro
    context.anotaciones_otro_usuario = Anotacion.objects.filter(
        usuario=context.otro_usuario,
        libro=context.libro,
    )


@then('ese usuario no puede ver las anotaciones del primero')
def step_no_ve_anotaciones_ajenas(context):
    context.test.assertFalse(
        context.anotaciones_otro_usuario.exists(),
        "El otro usuario no debe ver anotaciones que no le pertenecen.",
    )
    # Doble verificacion: las anotaciones del usuario original siguen existiendo
    anotaciones_propias = Anotacion.objects.filter(
        usuario=context.usuario_principal,
        libro=context.libro,
    )
    context.test.assertTrue(
        anotaciones_propias.exists(),
        "Las anotaciones del usuario original deben seguir en el sistema.",
    )


# ---------------------------------------------------------------------------
# Escenario: Las anotaciones se eliminan cuando el libro es retirado
# RN-ANO-08: Si un libro es eliminado, las anotaciones se eliminan tambien
# ---------------------------------------------------------------------------

@given('que el usuario tiene anotaciones en un libro')
def step_usuario_con_anotaciones(context):
    context.anotacion_retiro = Anotacion.objects.create(
        usuario=context.usuario_principal,
        libro=context.libro,
        fragmento_texto='historia',
        tipo_fragmento=Anotacion.TEXTO,
        contenido='Nota sobre la historia de la ciencia',
    )
    context.libro_id = context.libro.pk


@when('ese libro es retirado de la plataforma por su autor')
def step_libro_retirado_por_autor(context):
    context.libro.retirar()


@then('las anotaciones asociadas a ese libro son eliminadas del sistema')
def step_anotaciones_eliminadas_con_libro(context):
    anotaciones_restantes = Anotacion.objects.filter(libro_id=context.libro_id)
    context.test.assertFalse(
        anotaciones_restantes.exists(),
        "Todas las anotaciones del libro retirado deben ser eliminadas del sistema.",
    )


# ---------------------------------------------------------------------------
# Esquema del escenario: Crear anotaciones en distintos libros y fragmentos
# Se usa el matcher 're' para evitar ambiguedad con steps de otros features
# que contienen la frase 'visualizando un libro publicado por otro usuario'
# ---------------------------------------------------------------------------

from behave import use_step_matcher

use_step_matcher('re')


@given('que el usuario está visualizando (?P<nombre_libro>(?!un libro publicado por otro usuario).+)')
def step_usuario_visualizando_libro(context, nombre_libro):
    categoria = Categoria.objects.create(
        nombre=f'Categoria de {nombre_libro}',
    )
    context.libro_actual = Libro.objects.create(
        titulo=nombre_libro,
        contenido_texto=f'Contenido academico del libro {nombre_libro}.',
        numero_paginas=100,
        autor=context.usuario_principal,
        estado=Libro.PUBLICADO,
    )
    context.libro_actual.portada.save(
        'portada.png',
        SimpleUploadedFile(
            'portada.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
    )
    context.libro_actual.categorias.add(categoria)


@when('el usuario selecciona (?P<fragmento_texto>.+) y escribe la anotación (?P<contenido_anotacion>.+)')
def step_selecciona_fragmento_y_escribe(context, fragmento_texto, contenido_anotacion):
    context.anotacion_esquema = Anotacion.objects.create(
        usuario=context.usuario_principal,
        libro=context.libro_actual,
        fragmento_texto=fragmento_texto,
        tipo_fragmento=Anotacion.TEXTO,
        contenido=contenido_anotacion,
    )


@then('la anotación queda asociada a (?P<fragmento_texto>.+) en (?P<nombre_libro>.+)')
def step_anotacion_asociada_libro_fragmento(context, fragmento_texto, nombre_libro):
    anotacion = Anotacion.objects.get(pk=context.anotacion_esquema.pk)
    context.test.assertEqual(
        anotacion.fragmento_texto,
        fragmento_texto,
        f"La anotacion debe estar asociada al fragmento '{fragmento_texto}'.",
    )
    context.test.assertEqual(
        anotacion.libro.titulo,
        nombre_libro,
        f"La anotacion debe pertenecer al libro '{nombre_libro}'.",
    )
    context.test.assertEqual(
        anotacion.usuario,
        context.usuario_principal,
        "La anotacion debe pertenecer al usuario autenticado.",
    )


use_step_matcher('parse')
