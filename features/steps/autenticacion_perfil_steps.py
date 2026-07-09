from behave import given, when, then
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from src.login.models import PerfilUsuario, RecuperacionContrasena

User = get_user_model()

@given('que la plataforma de biblioteca digital está operativa')
def step_plataforma_operativa(context):
    # La base de datos y la app ya están listas para las pruebas.
    pass

@given('que un visitante proporciona sus datos de autenticación básicos')
def step_visitante_datos_basicos(context):
    context.form_data = {
        'correo': 'nuevo@ejemplo.com',
        'contrasena1': 'password123',
        'contrasena2': 'password123',
    }

@given('proporciona su nombre completo y un nickname')
def step_proporciona_nombre_nickname(context):
    context.form_data['nombre'] = 'Juan Perez'
    context.form_data['nickname'] = 'juanperez99'

@given('selecciona obligatoriamente un rol académico')
def step_visitante_rol_academico(context):
    context.form_data['rol'] = PerfilUsuario.ESTUDIANTE

@when('el visitante completa el registro')
def step_visitante_completa_registro(context):
    url = reverse('login:registro')
    context.response = context.test.client.post(url, context.form_data)

@then('el sistema crea su cuenta exitosamente')
def step_sistema_crea_cuenta(context):
    # Verificamos que el usuario se haya creado usando el correo
    user_exists = User.objects.filter(email='nuevo@ejemplo.com').exists()
    context.test.assertTrue(user_exists, "El usuario no fue creado en la base de datos.")

@then('asigna el rol seleccionado a su perfil de usuario')
def step_asigna_rol_perfil(context):
    user = User.objects.get(email='nuevo@ejemplo.com')
    context.test.assertTrue(hasattr(user, 'perfil'), "El usuario no tiene un perfil asociado.")
    context.test.assertEqual(user.perfil.rol, PerfilUsuario.ESTUDIANTE, "El rol asignado no coincide.")

@given('que un usuario académico está registrado en el sistema')
def step_usuario_registrado(context):
    user = User.objects.create_user(
        username='usuarioregistrado', 
        email='registrado@ejemplo.com', 
        password='password123',
        first_name='Usuario Registrado'
    )
    PerfilUsuario.objects.create(usuario=user, rol=PerfilUsuario.PROFESOR)
    context.user_data = {
        'correo': 'registrado@ejemplo.com',
        'contrasena': 'password123'
    }

@when('el usuario proporciona sus credenciales correctas')
def step_usuario_credenciales(context):
    url = reverse('login:inicio')
    context.response = context.test.client.post(url, context.user_data)

@then('el sistema le permite el acceso')
def step_sistema_permite_acceso(context):
    # Verificar si fue autenticado verificando la sesión u otras respuestas
    # Al ser un redirect post-login exitoso, el status es 302
    context.test.assertEqual(context.response.status_code, 302, "No se permitió el acceso o no redirigió correctamente.")

@then('lo redirige a su panel personal')
def step_redirige_panel_personal(context):
    context.test.assertRedirects(context.response, reverse('login:panel'))

@given('que un usuario registrado requiere recuperar su contraseña')
def step_usuario_requiere_recuperar(context):
    user = User.objects.create_user(
        username='usuariorecuperar', 
        email='olvido@ejemplo.com', 
        password='password123',
        first_name='Usuario Recuperar'
    )
    context.recuperar_data = {'correo': 'olvido@ejemplo.com'}

@when('el usuario solicita la recuperación de su cuenta')
def step_usuario_solicita_recuperacion(context):
    url = reverse('login:olvido_contrasena')
    context.response = context.test.client.post(url, context.recuperar_data)

@then('el sistema genera un código de recuperación único')
def step_sistema_genera_codigo(context):
    user = User.objects.get(email='olvido@ejemplo.com')
    recuperaciones = RecuperacionContrasena.objects.filter(usuario=user)
    context.test.assertTrue(recuperaciones.exists(), "No se generó el código de recuperación.")
    context.recuperacion = recuperaciones.first()

@then('envía el código al correo electrónico del usuario con una vigencia máxima de 24 horas')
def step_envia_codigo_vigencia(context):
    # Verificamos la vigencia a nivel de modelo
    context.test.assertTrue(context.recuperacion.esta_vigente(), "El código generado no está vigente.")
    # Verificamos que se haya enviado el correo con el código/enlace
    context.test.assertEqual(len(mail.outbox), 1, "No se envió el correo de recuperación.")
    correo = mail.outbox[0]
    context.test.assertEqual(correo.to, ['olvido@ejemplo.com'])
    context.test.assertIn(str(context.recuperacion.codigo), correo.body)

@given('que un usuario posee un código de recuperación')
def step_usuario_posee_codigo(context):
    user = User.objects.create_user(
        username='usuariocodigo', 
        email='concodigo@ejemplo.com', 
        password='password123',
        first_name='Usuario Codigo'
    )
    context.recuperacion = RecuperacionContrasena.objects.create(usuario=user)

@given('el código ha superado su vigencia máxima de 24 horas o ya fue utilizado')
def step_codigo_expirado_utilizado(context):
    # Simulamos que el código ya fue usado
    context.recuperacion.usado = True
    context.recuperacion.save()

@when('el usuario intenta utilizar el código')
def step_usuario_intenta_utilizar(context):
    url = reverse('login:reiniciar_contrasena', args=[context.recuperacion.codigo])
    context.response = context.test.client.get(url)

@then('el sistema rechaza la operación')
def step_sistema_rechaza_operacion(context):
    # El response debería ser un render con status 200 pero que contenga el mensaje de error
    context.test.assertEqual(context.response.status_code, 200)

@then('solicita que genere un nuevo código de recuperación')
def step_solicita_nuevo_codigo(context):
    mensaje_error = 'El enlace ha expirado o ya se utilizó. Solicita uno nuevo.'
    context.test.assertContains(context.response, mensaje_error)
