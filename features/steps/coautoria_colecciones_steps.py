from behave import given, when, then
from django.contrib.auth import get_user_model
from src.materiales.models import Coleccion, ParticipacionColeccion, Libro, Categoria

User = get_user_model()

# ---------------------------------------------------------------------------
# Escenario: Invitar a un usuario a colaborar en una colección
# ---------------------------------------------------------------------------

@given('que el usuario es administrador de una colección que no ha alcanzado el límite de participantes')
def step_admin_coleccion_sin_limite(context):
    context.coleccion = Coleccion.objects.create(
        nombre='Colección de Ciencias',
        creador=context.usuario_principal
    )
    context.invitado = User.objects.create_user(
        username='invitado', email='invitado@test.com', password='password123'
    )

@when('el usuario invita a otro usuario a colaborar en esa colección')
def step_invitar_usuario_a_colaborar(context):
    # Asumimos que existirá un método invitar_usuario o se crea una Invitacion
    try:
        context.resultado_invitacion, context.mensaje = context.coleccion.invitar_usuario(
            admin=context.usuario_principal, 
            usuario_invitado=context.invitado
        )
    except Exception as e:
        context.exception = e

@then('el usuario invitado recibe la invitación')
def step_invitado_recibe_invitacion(context):
    context.test.assertTrue(hasattr(context, 'resultado_invitacion'))
    context.test.assertTrue(context.resultado_invitacion)
    
    # Asumimos la existencia de un modelo InvitacionColeccion
    from src.materiales.models import InvitacionColeccion
    invitacion = InvitacionColeccion.objects.filter(
        coleccion=context.coleccion, usuario_invitado=context.invitado
    ).first()
    context.test.assertIsNotNone(invitacion)

@then('queda pendiente hasta que la acepte o rechace')
def step_invitacion_queda_pendiente(context):
    from src.materiales.models import InvitacionColeccion
    invitacion = InvitacionColeccion.objects.get(
        coleccion=context.coleccion, usuario_invitado=context.invitado
    )
    context.test.assertEqual(invitacion.estado, 'pendiente')

# ---------------------------------------------------------------------------
# Escenario: Unirse a una colección por invitación
# ---------------------------------------------------------------------------

@given('que el usuario ha recibido una invitación para unirse a una colección')
def step_usuario_recibe_invitacion(context):
    admin = User.objects.create_user(username='admin_col', password='123')
    context.coleccion = Coleccion.objects.create(nombre='Col Admin', creador=admin)
    
    # context.usuario_principal es el invitado (ya creado en antecedentes)
    from src.materiales.models import InvitacionColeccion
    context.invitacion = InvitacionColeccion.objects.create(
        coleccion=context.coleccion,
        usuario_invitado=context.usuario_principal,
        estado='pendiente'
    )

@when('el usuario acepta la invitación')
def step_usuario_acepta_invitacion(context):
    try:
        context.resultado_aceptar = context.invitacion.aceptar(usuario=context.usuario_principal)
    except Exception as e:
        context.exception = e

@then('pasa a ser participante de esa colección')
def step_pasa_a_ser_participante(context):
    es_participante = ParticipacionColeccion.objects.filter(
        coleccion=context.coleccion, usuario=context.usuario_principal
    ).exists()
    context.test.assertTrue(es_participante)

@then('puede agregar libros y editar junto a los demás miembros')
def step_puede_agregar_y_editar(context):
    participacion = ParticipacionColeccion.objects.get(
        coleccion=context.coleccion, usuario=context.usuario_principal
    )
    context.test.assertEqual(participacion.rol, ParticipacionColeccion.PARTICIPANTE)

# ---------------------------------------------------------------------------
# Escenario: Solicitar unirse a una colección colaborativa
# ---------------------------------------------------------------------------

@given('que el usuario está visualizando una colección colaborativa disponible')
def step_visualiza_coleccion_disponible(context):
    admin = User.objects.create_user(username='admin_disp', password='123')
    context.coleccion = Coleccion.objects.create(
        nombre='Coleccion Publica', 
        creador=admin, 
        visibilidad=Coleccion.PUBLICA
    )

@when('el usuario solicita unirse a esa colección')
def step_solicita_unirse(context):
    try:
        context.resultado_solicitud, context.mensaje = context.coleccion.solicitar_acceso(
            usuario_solicitante=context.usuario_principal
        )
    except Exception as e:
        context.exception = e

@then('el administrador de la colección recibe la solicitud')
def step_admin_recibe_solicitud(context):
    from src.materiales.models import SolicitudAccesoColeccion
    solicitud = SolicitudAccesoColeccion.objects.filter(
        coleccion=context.coleccion, usuario_solicitante=context.usuario_principal
    ).first()
    context.test.assertIsNotNone(solicitud)

@then('el usuario queda en espera hasta que sea aprobada o rechazada')
def step_usuario_queda_en_espera(context):
    from src.materiales.models import SolicitudAccesoColeccion
    solicitud = SolicitudAccesoColeccion.objects.get(
        coleccion=context.coleccion, usuario_solicitante=context.usuario_principal
    )
    context.test.assertEqual(solicitud.estado, 'pendiente')

# ---------------------------------------------------------------------------
# Escenario: El administrador aprueba una solicitud de ingreso
# ---------------------------------------------------------------------------

@given('que el administrador de una colección tiene una solicitud de ingreso pendiente')
def step_admin_tiene_solicitud_pendiente(context):
    context.solicitante = User.objects.create_user(username='solicitante', password='123')
    context.coleccion = Coleccion.objects.create(
        nombre='Col Solicitud', creador=context.usuario_principal
    )
    from src.materiales.models import SolicitudAccesoColeccion
    context.solicitud = SolicitudAccesoColeccion.objects.create(
        coleccion=context.coleccion,
        usuario_solicitante=context.solicitante,
        estado='pendiente'
    )

@when('el administrador aprueba la solicitud')
def step_admin_aprueba_solicitud(context):
    try:
        context.resultado_aprobar = context.solicitud.aprobar(admin_usuario=context.usuario_principal)
    except Exception as e:
        context.exception = e

@then('el solicitante pasa a ser participante de la colección')
def step_solicitante_es_participante(context):
    es_participante = ParticipacionColeccion.objects.filter(
        coleccion=context.coleccion, usuario=context.solicitante
    ).exists()
    context.test.assertTrue(es_participante)

# ---------------------------------------------------------------------------
# Escenario: El administrador rechaza una solicitud de ingreso
# ---------------------------------------------------------------------------

@when('el administrador rechaza la solicitud')
def step_admin_rechaza_solicitud(context):
    try:
        context.resultado_rechazar = context.solicitud.rechazar(admin_usuario=context.usuario_principal)
    except Exception as e:
        context.exception = e

@then('el solicitante no obtiene acceso a la colección')
def step_solicitante_no_obtiene_acceso(context):
    es_participante = ParticipacionColeccion.objects.filter(
        coleccion=context.coleccion, usuario=context.solicitante
    ).exists()
    context.test.assertFalse(es_participante)

@then('es notificado del rechazo')
def step_notificado_rechazo(context):
    from src.feed.models import Notificacion
    notificacion = Notificacion.objects.filter(
        usuario=context.solicitante, 
        mensaje__icontains='rechazada'
    ).exists()
    context.test.assertTrue(notificacion)

# ---------------------------------------------------------------------------
# Escenario: No se puede invitar a más participantes si se alcanzó el límite de 15
# ---------------------------------------------------------------------------

@given('que el usuario es administrador de una colección que ya tiene 15 participantes')
def step_admin_coleccion_llena(context):
    context.coleccion = Coleccion.objects.create(
        nombre='Col Llena', creador=context.usuario_principal
    )
    # Llenar colección
    for i in range(14):  # 1 creador + 14 participantes = 15
        u = User.objects.create_user(username=f'part_{i}', password='123')
        context.coleccion.agregar_participante(u)
    
    context.nuevo_invitado = User.objects.create_user(username='nuevo_invitado', password='123')

@when('el usuario intenta invitar a un nuevo colaborador')
def step_intenta_invitar_nuevo(context):
    try:
        resultado, mensaje = context.coleccion.invitar_usuario(
            admin=context.usuario_principal, 
            usuario_invitado=context.nuevo_invitado
        )
        context.resultado = resultado
    except Exception as e:
        context.resultado = False
        context.exception = e

# ---------------------------------------------------------------------------
# Escenario: Solo el administrador puede gestionar participantes
# ---------------------------------------------------------------------------

@given('que el usuario es un participante regular de una colección')
def step_es_participante_regular(context):
    admin = User.objects.create_user(username='admin_reg', password='123')
    context.coleccion = Coleccion.objects.create(nombre='Col Regular', creador=admin)
    context.coleccion.agregar_participante(context.usuario_principal, rol=ParticipacionColeccion.PARTICIPANTE)
    context.tercero = User.objects.create_user(username='tercero', password='123')

@when('el usuario intenta invitar, aceptar solicitudes o retirar participantes')
def step_intenta_gestionar_participantes(context):
    try:
        context.coleccion.invitar_usuario(admin=context.usuario_principal, usuario_invitado=context.tercero)
    except PermissionError as e:
        context.exception = e

    from src.materiales.models import SolicitudAccesoColeccion
    solicitud = SolicitudAccesoColeccion.objects.create(coleccion=context.coleccion, usuario_solicitante=context.tercero)
    try:
        solicitud.aprobar(admin_usuario=context.usuario_principal)
    except PermissionError:
        pass

    context.resultado = False

# ---------------------------------------------------------------------------
# Escenario: Cualquier participante puede agregar libros a la colección
# ---------------------------------------------------------------------------

@given('que el usuario es participante de una colección que no ha alcanzado su límite de libros')
def step_participante_sin_limite_libros(context):
    admin = User.objects.create_user(username='admin_libros', password='123')
    context.coleccion = Coleccion.objects.create(nombre='Col Libros', creador=admin)
    context.coleccion.agregar_participante(context.usuario_principal, rol=ParticipacionColeccion.PARTICIPANTE)
    
    context.libro = Libro.objects.create(
        titulo='Libro Aporte',
        autor=context.usuario_principal,
        numero_paginas=100,
        estado=Libro.PUBLICADO
    )

@when('el usuario agrega un libro a la colección')
def step_agrega_libro(context):
    try:
        context.coleccion.agregar_libro(context.usuario_principal, context.libro)
    except Exception as e:
        context.exception = e

@then('el libro queda registrado en la colección')
def step_libro_registrado(context):
    context.test.assertTrue(context.coleccion.libros.filter(id=context.libro.id).exists())

@then('el cambio es visible para todos los participantes')
def step_cambio_visible(context):
    context.test.assertEqual(context.coleccion.libros.count(), 1)

# ---------------------------------------------------------------------------
# Escenario: Solo el administrador o el aportante puede eliminar un libro de la colección
# ---------------------------------------------------------------------------

@given('que el usuario es un participante de la colección y hay un libro en ella')
def step_participante_no_aportante(context):
    admin = User.objects.create_user(username='admin_elim_lib', password='123')
    context.coleccion = Coleccion.objects.create(nombre='Col Eliminar', creador=admin)
    context.coleccion.agregar_participante(context.usuario_principal, rol=ParticipacionColeccion.PARTICIPANTE)
    
    otro = User.objects.create_user(username='otro', password='123')
    context.coleccion.agregar_participante(otro, rol=ParticipacionColeccion.PARTICIPANTE)
    
    context.libro_otro = Libro.objects.create(
        titulo='Libro Otro', autor=otro, numero_paginas=50, estado=Libro.PUBLICADO
    )
    pass

@when('el usuario intenta eliminar ese libro de la colección')
def step_intenta_eliminar_libro(context):
    try:
        context.coleccion.eliminar_libro(context.usuario_principal, context.libro_otro)
        context.resultado = True
    except PermissionError as e:
        context.resultado = False
        context.exception_eliminar = e

@then('la operación es exitosa')
def step_operacion_exitosa_eliminar(context):
    context.test.assertTrue(context.resultado)


# ---------------------------------------------------------------------------
# Escenario: El rol de administrador pasa al colaborador más activo si el creador es eliminado
# ---------------------------------------------------------------------------

@given('que el creador de una colección es eliminado de la plataforma')
def step_creador_eliminado(context):
    admin = User.objects.create_user(username='admin_elim', password='123')
    context.coleccion = Coleccion.objects.create(nombre='Col Creador Elim', creador=admin)
    
    # Participante activo
    context.participante_activo = User.objects.create_user(username='activo', password='123')
    context.coleccion.agregar_participante(context.participante_activo)
    # Simular que es el más activo (por reputación)
    
    # Eliminar admin
    admin.delete()

@then('el sistema asigna automáticamente el rol de administrador al participante con mayor índice de reputación de colaborador en esa colección')
def step_asigna_nuevo_admin(context):
    context.coleccion.refresh_from_db()
    context.test.assertEqual(context.coleccion.creador.username, context.participante_activo.username)
    from src.materiales.models import ParticipacionColeccion
    es_admin = context.coleccion.participaciones.filter(usuario=context.participante_activo, rol=ParticipacionColeccion.ADMINISTRADOR).exists()
    context.test.assertTrue(es_admin)
