from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (
    InicioSesionFormulario,
    OlvidoContrasenaFormulario,
    RegistroFormulario,
    ReinicioContrasenaFormulario,
)
from .models import RecuperacionContrasena


def inicio(request):
    formulario = InicioSesionFormulario(request.POST or None, request=request)

    if request.method == 'POST' and formulario.is_valid():
        login(request, formulario.usuario)
        return redirect('materiales:inicio')

    return render(request, 'login/login.html', {'formulario': formulario})


def registro(request):
    formulario = RegistroFormulario(request.POST or None)
    mensaje_exito = ''

    if request.method == 'POST' and formulario.is_valid():
        formulario.save()
        mensaje_exito = 'Registro completado. Ya puedes iniciar sesion.'
        formulario = RegistroFormulario()

    from .forms import AVATARES_DISPONIBLES
    return render(
        request,
        'login/registro.html',
        {
            'formulario': formulario,
            'mensaje_exito': mensaje_exito,
            'avatares': AVATARES_DISPONIBLES,
        },
    )


def olvido_contrasena(request):
    formulario = OlvidoContrasenaFormulario(request.POST or None)
    enlace_reinicio = ''
    mensaje_exito = ''

    if request.method == 'POST' and formulario.is_valid():
        usuario = formulario.obtener_usuario()
        if usuario is not None:
            recuperacion = RecuperacionContrasena.objects.create(usuario=usuario)
            enlace_reinicio = request.build_absolute_uri(
                reverse('login:reiniciar_contrasena', args=[recuperacion.codigo])
            )
            # Enviar el correo electrónico
            send_mail(
                'Recuperación de contraseña',
                f'Utiliza este enlace para reiniciar tu contraseña: {enlace_reinicio}',
                'noreply@biblioteca.com',
                [usuario.email],
                fail_silently=False,
            )
        mensaje_exito = (
            'Si el correo existe en nuestro sistema, recibirás instrucciones para reiniciar tu contraseña.'
        )

    return render(
        request,
        'login/olvido.html',
        {
            'formulario': formulario,
            'mensaje_exito': mensaje_exito,
            'enlace_reinicio': enlace_reinicio,
        },
    )


def reiniciar_contrasena(request, codigo):
    recuperacion = get_object_or_404(RecuperacionContrasena, codigo=codigo)
    if not recuperacion.esta_vigente():
        return render(
            request,
            'login/reiniciar.html',
            {
                'formulario': None,
                'error': 'El enlace ha expirado o ya se utilizó. Solicita uno nuevo.',
            },
        )

    formulario = ReinicioContrasenaFormulario(request.POST or None)
    mensaje_exito = ''

    if request.method == 'POST' and formulario.is_valid():
        usuario = recuperacion.usuario
        usuario.set_password(formulario.cleaned_data['contrasena1'])
        usuario.save()
        recuperacion.usado = True
        recuperacion.save()
        messages.success(request, 'Contraseña actualizada correctamente. Puedes iniciar sesión ahora.')
        return redirect('login:inicio')

    return render(
        request,
        'login/reiniciar.html',
        {
            'formulario': formulario,
            'error': '',
        },
    )


@login_required(login_url='/')
def panel(request):
    return render(request, 'login/panel.html', {'usuario': request.user})


def cerrar_sesion(request):
    # Consumir y limpiar todos los mensajes pendientes para evitar que aparezcan en el login
    from django.contrib import messages
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    logout(request)
    return redirect('login:inicio')
