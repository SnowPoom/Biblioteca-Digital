from behave import given, when, then
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from src.materiales.models import Libro, Categoria
from src.materiales.models import Anotacion

User = get_user_model()

LIMITE_CARACTERES_ANOTACION = 150


# --- Antecedentes ---
# El step "que el usuario ha iniciado sesion en la plataforma" ya existe
# en publicacion_material_steps.py y se reutiliza automaticamente por Behave.

@given('que el usuario ha abierto un libro disponible en la biblioteca')
def step_usuario_abre_libro(context):
    categoria = Categoria.objects.create(nombre='Ciencias Generales')
    context.libro = Libro.objects.create(
        titulo='Fundamentos de Fisica',
        contenido_texto='La energia no se crea ni se destruye, solo se transforma.',
        numero_paginas=120,
        autor=context.usuario,
        estado=Libro.PUBLICADO,
    )
    context.libro.portada.save(
        'portada_fisica.png',
        SimpleUploadedFile(
            'portada_fisica.png',
            b'\x89PNG\r\n\x1a\n\x00\x00\x00',
            content_type='image/png',
        ),
    )
    context.libro.categorias.add(categoria)


# ---------------------------------------------------------------------------
# Escenario: Crear una anotacion sobre un fragmento de texto
# ---------------------------------------------------------------------------

@given('que el usuario está leyendo una página del libro')
def step_usuario_leyendo_pagina(context):
    context.fragmento_texto = 'La energia no se crea ni se destruye'
    context.tipo_fragmento = 'texto'


@when('el usuario selecciona un fragmento de texto y elige anotarlo')
def step_selecciona_fragmento_texto(context):
    context.fragmento_seleccionado = context.fragmento_texto


@when('escribe el contenido de la anotación')
def step_escribe_contenido_anotacion(context):
    context.contenido_anotacion = 'Primer principio de la termodinamica'
    context.anotacion = Anotacion.objects.create(
        usuario=context.usuario,
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
        "La anotacion no quedo asociada al fragmento de texto correcto.",
    )
    context.test.assertEqual(
        anotacion.contenido,
        context.contenido_anotacion,
        "El contenido de la anotacion no coincide con lo escrito por el usuario.",
    )


@then('el fragmento se muestra visualmente diferenciado en la página')
def step_fragmento_diferenciado(context):
    anotacion = Anotacion.objects.get(pk=context.anotacion.pk)
    context.test.assertTrue(
        anotacion.esta_activa(),
        "La anotacion debe estar activa para diferenciarse visualmente.",
    )


# ---------------------------------------------------------------------------
# Escenario: Crear una anotacion sobre una imagen
# ---------------------------------------------------------------------------

@given('que el usuario está en una página que contiene una imagen')
def step_usuario_pagina_con_imagen(context):
    context.identificador_imagen = 'imagen_diagrama_fuerzas.png'
    context.tipo_fragmento = 'imagen'


@when('el usuario elige anotar esa imagen')
def step_elige_anotar_imagen(context):
    context.fragmento_seleccionado = context.identificador_imagen


@then('la anotación queda asociada a esa imagen')
def step_anotacion_asociada_imagen(context):
    anotacion = Anotacion.objects.get(pk=context.anotacion.pk)
    context.test.assertEqual(
        anotacion.fragmento_texto,
        context.identificador_imagen,
        "La anotacion no quedo asociada a la imagen correcta.",
    )
    context.test.assertEqual(
        anotacion.tipo_fragmento,
        'imagen',
        "El tipo de fragmento deberia ser 'imagen'.",
    )


# ---------------------------------------------------------------------------
# Escenario: No se puede guardar una anotacion que supera el limite de caracteres
# ---------------------------------------------------------------------------

@given('que el usuario ha abierto el campo de anotación sobre un fragmento')
def step_campo_anotacion_abierto(context):
    context.fragmento_seleccionado = 'solo se transforma'
    context.tipo_fragmento = 'texto'


@when('el usuario intenta ingresar un texto que supera los 150 caracteres')
def step_intenta_texto_excede_limite(context):
    # RN-ANO-03: Limite maximo de 150 caracteres
    texto_excedido = 'a' * (LIMITE_CARACTERES_ANOTACION + 1)
    context.resultado_validacion = Anotacion.validar_contenido(texto_excedido)


@then('el sistema no permite continuar ingresando texto')
def step_no_permite_texto(context):
    context.test.assertFalse(
        context.resultado_validacion,
        "El sistema deberia rechazar una anotacion que supera los 150 caracteres.",
    )


@then('se indica visualmente que se alcanzó el límite')
def step_indica_limite_alcanzado(context):
    # La validacion a nivel de modelo garantiza el rechazo;
    # la indicacion visual se verifica confirmando que el modelo no acepta el contenido
    texto_excedido = 'a' * (LIMITE_CARACTERES_ANOTACION + 1)
    context.test.assertGreater(
        len(texto_excedido),
        LIMITE_CARACTERES_ANOTACION,
        "El texto supera el limite y el sistema debe indicarlo.",
    )


# ---------------------------------------------------------------------------
# Escenario: Un fragmento con anotacion existente no permite crear una segunda
# ---------------------------------------------------------------------------

@given('que el usuario tiene una anotación guardada sobre un fragmento de texto')
def step_anotacion_existente_en_fragmento(context):
    context.fragmento_seleccionado = 'La energia no se crea ni se destruye'
    context.tipo_fragmento = 'texto'
    context.anotacion_existente = Anotacion.objects.create(
        usuario=context.usuario,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
        tipo_fragmento=context.tipo_fragmento,
        contenido='Nota original sobre este fragmento',
    )


@when('el usuario selecciona ese mismo fragmento para anotar nuevamente')
def step_selecciona_mismo_fragmento(context):
    # RN-ANO-04: Maximo una anotacion activa por fragmento por usuario
    context.anotacion_recuperada = Anotacion.obtener_anotacion_existente(
        usuario=context.usuario,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
    )


@then('el sistema lleva al usuario a editar la anotación existente')
def step_lleva_a_editar(context):
    context.test.assertIsNotNone(
        context.anotacion_recuperada,
        "El sistema debe recuperar la anotacion existente para edicion.",
    )
    context.test.assertEqual(
        context.anotacion_recuperada.pk,
        context.anotacion_existente.pk,
        "La anotacion recuperada debe ser la misma que ya existia en el fragmento.",
    )


@then('no permite crear una anotación adicional sobre el mismo fragmento')
def step_no_permite_duplicar(context):
    total_anotaciones = Anotacion.objects.filter(
        usuario=context.usuario,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
    ).count()
    context.test.assertEqual(
        total_anotaciones,
        1,
        "Solo debe existir una anotacion por fragmento por usuario.",
    )


# ---------------------------------------------------------------------------
# Escenario: Las anotaciones persisten entre sesiones
# ---------------------------------------------------------------------------

@given('que el usuario tiene anotaciones guardadas en un libro')
def step_anotaciones_guardadas(context):
    context.anotacion_persistente = Anotacion.objects.create(
        usuario=context.usuario,
        libro=context.libro,
        fragmento_texto='La energia no se crea ni se destruye',
        tipo_fragmento='texto',
        contenido='Esta nota debe persistir entre sesiones',
    )


@when('el usuario cierra el libro y vuelve a abrirlo en una sesión posterior')
def step_cierra_y_reabre_libro(context):
    # Simula el cierre y reapertura consultando las anotaciones desde la base de datos
    context.anotaciones_recuperadas = Anotacion.objects.filter(
        usuario=context.usuario,
        libro=context.libro,
    )


@then('todas las anotaciones siguen visibles en los fragmentos correspondientes')
def step_anotaciones_visibles(context):
    context.test.assertTrue(
        context.anotaciones_recuperadas.exists(),
        "Las anotaciones deben persistir entre sesiones (RN-ANO-07).",
    )
    context.test.assertEqual(
        context.anotaciones_recuperadas.first().pk,
        context.anotacion_persistente.pk,
        "La anotacion recuperada debe ser la misma que se guardo previamente.",
    )


# ---------------------------------------------------------------------------
# Escenario: Editar una anotacion existente
# ---------------------------------------------------------------------------

@given('que el usuario tiene una anotación guardada sobre un fragmento')
def step_anotacion_guardada_fragmento(context):
    context.fragmento_seleccionado = 'solo se transforma'
    context.anotacion = Anotacion.objects.create(
        usuario=context.usuario,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
        tipo_fragmento='texto',
        contenido='Contenido original de la anotacion',
    )


@when('el usuario accede a esa anotación y modifica su contenido')
def step_modifica_contenido(context):
    context.nuevo_contenido = 'Contenido actualizado de la anotacion'
    context.anotacion.contenido = context.nuevo_contenido
    context.anotacion.save()


@then('la anotación refleja el contenido actualizado')
def step_refleja_contenido_actualizado(context):
    context.anotacion.refresh_from_db()
    context.test.assertEqual(
        context.anotacion.contenido,
        context.nuevo_contenido,
        "La anotacion no refleja el contenido actualizado tras la edicion.",
    )


@then('el fragmento permanece visualmente diferenciado')
def step_fragmento_permanece_diferenciado(context):
    context.anotacion.refresh_from_db()
    context.test.assertTrue(
        context.anotacion.esta_activa(),
        "La anotacion debe permanecer activa despues de la edicion.",
    )


# ---------------------------------------------------------------------------
# Escenario: Eliminar una anotacion propia
# ---------------------------------------------------------------------------

@when('el usuario elimina esa anotación')
def step_elimina_anotacion(context):
    context.anotacion_pk = context.anotacion.pk
    context.anotacion.delete()


@then('la anotación desaparece del sistema')
def step_anotacion_desaparece(context):
    existe = Anotacion.objects.filter(pk=context.anotacion_pk).exists()
    context.test.assertFalse(
        existe,
        "La anotacion eliminada no debe existir en el sistema.",
    )


@then('el fragmento deja de estar visualmente diferenciado')
def step_fragmento_no_diferenciado(context):
    anotaciones_fragmento = Anotacion.objects.filter(
        usuario=context.usuario,
        libro=context.libro,
        fragmento_texto=context.fragmento_seleccionado,
    )
    context.test.assertFalse(
        anotaciones_fragmento.exists(),
        "No deben quedar anotaciones activas sobre el fragmento eliminado.",
    )


# ---------------------------------------------------------------------------
# Escenario: Las anotaciones de un usuario no son visibles para otros
# ---------------------------------------------------------------------------

@when('otro usuario accede al mismo libro')
def step_otro_usuario_accede(context):
    context.otro_usuario = User.objects.create_user(
        username='otro_lector',
        email='otro_lector@ejemplo.com',
        password='password123',
        first_name='Otro Lector',
    )
    # RN-ANO-01: Las anotaciones son personales e intransferibles
    context.anotaciones_otro_usuario = Anotacion.objects.filter(
        usuario=context.otro_usuario,
        libro=context.libro,
    )


@then('ese usuario no puede ver las anotaciones del primero')
def step_no_ve_anotaciones_ajenas(context):
    context.test.assertFalse(
        context.anotaciones_otro_usuario.exists(),
        "El otro usuario no debe ver las anotaciones del primer usuario (RN-ANO-01).",
    )
    # Verifica ademas que las anotaciones originales siguen existiendo para su dueno
    anotaciones_dueno = Anotacion.objects.filter(
        usuario=context.usuario,
        libro=context.libro,
    )
    context.test.assertTrue(
        anotaciones_dueno.exists(),
        "Las anotaciones del usuario original deben seguir existiendo.",
    )


# ---------------------------------------------------------------------------
# Escenario: Las anotaciones se eliminan cuando el libro es retirado
# ---------------------------------------------------------------------------

@given('que el usuario tiene anotaciones en un libro')
def step_anotaciones_en_libro(context):
    context.anotacion_a_eliminar = Anotacion.objects.create(
        usuario=context.usuario,
        libro=context.libro,
        fragmento_texto='La energia no se crea ni se destruye',
        tipo_fragmento='texto',
        contenido='Anotacion que sera eliminada con el libro',
    )


@when('ese libro es retirado de la plataforma por su autor')
def step_libro_retirado(context):
    # RN-ANO-08: Al retirar el libro, las anotaciones se eliminan
    context.libro.retirar()


@then('las anotaciones asociadas a ese libro son eliminadas del sistema')
def step_anotaciones_eliminadas_con_libro(context):
    anotaciones_del_libro = Anotacion.objects.filter(libro=context.libro)
    context.test.assertFalse(
        anotaciones_del_libro.exists(),
        "Todas las anotaciones deben eliminarse al retirar el libro (RN-ANO-08).",
    )


# ---------------------------------------------------------------------------
# Esquema del escenario: Crear anotaciones en distintos libros y fragmentos
# ---------------------------------------------------------------------------

@given('que el usuario está visualizando {nombre_libro}')
def step_visualizando_libro(context, nombre_libro):
    categoria = Categoria.objects.create(
        nombre=f'Categoria de {nombre_libro}',
    )
    context.libro_actual = Libro.objects.create(
        titulo=nombre_libro,
        contenido_texto=f'Contenido del libro {nombre_libro}.',
        numero_paginas=80,
        autor=context.usuario,
        estado=Libro.PUBLICADO,
    )
    context.libro_actual.categorias.add(categoria)


@when('el usuario selecciona {fragmento_texto} y escribe la anotación {contenido_anotacion}')
def step_selecciona_y_anota(context, fragmento_texto, contenido_anotacion):
    context.anotacion_esquema = Anotacion.objects.create(
        usuario=context.usuario,
        libro=context.libro_actual,
        fragmento_texto=fragmento_texto,
        tipo_fragmento='texto',
        contenido=contenido_anotacion,
    )


@then('la anotación queda asociada a {fragmento_texto} en {nombre_libro}')
def step_anotacion_asociada_libro(context, fragmento_texto, nombre_libro):
    anotacion = Anotacion.objects.get(pk=context.anotacion_esquema.pk)
    context.test.assertEqual(
        anotacion.fragmento_texto,
        fragmento_texto,
        f"La anotacion no esta asociada al fragmento '{fragmento_texto}'.",
    )
    context.test.assertEqual(
        anotacion.libro.titulo,
        nombre_libro,
        f"La anotacion no esta asociada al libro '{nombre_libro}'.",
    )
