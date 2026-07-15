from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notificacion, Publicacion, Republicacion, Seguimiento

User = get_user_model()


@login_required
def feed(request):
    """
    Retorna las publicaciones y republicaciones de los usuarios seguidos
    ordenadas cronológicamente de la más reciente a la más antigua.
    """
    from itertools import chain

    ids_seguidos = Seguimiento.objects.filter(
        seguidor=request.user
    ).values_list('seguido_id', flat=True)

    publicaciones = Publicacion.objects.filter(
        autor_id__in=ids_seguidos
    ).select_related('autor')

    republicaciones = Republicacion.objects.filter(
        republicado_por_id__in=ids_seguidos
    ).select_related('republicado_por', 'publicacion__autor')

    # Separar colecciones
    colecciones = publicaciones.filter(tipo=Publicacion.COLECCION).order_by('-creado')

    # Combinar libros y republicaciones estrictamente por fecha
    libros = publicaciones.filter(tipo=Publicacion.LIBRO)
    material_feed = sorted(
        chain(libros, republicaciones),
        key=lambda obj: obj.creado,
        reverse=True
    )

    if not material_feed and not colecciones:
        return redirect('materiales:inicio')

    contexto = {
        'material_feed': material_feed,
        'colecciones': colecciones,
    }
    return render(request, 'feed/feed.html', contexto)


@login_required
@require_POST
def seguir_usuario(request, usuario_id):
    """
    Crea una relación de seguimiento entre el usuario autenticado y
    el usuario objetivo. No requiere aprobación (RN-FED-05).
    Redirige al perfil público del usuario seguido.
    """
    usuario_objetivo = get_object_or_404(User, pk=usuario_id)

    # Un usuario no puede seguirse a sí mismo
    if usuario_objetivo == request.user:
        return redirect('feed:perfil_publico', username=request.user.username)

    Seguimiento.objects.get_or_create(
        seguidor=request.user,
        seguido=usuario_objetivo,
    )
    return redirect('feed:perfil_publico', username=usuario_objetivo.username)


@login_required
@require_POST
def dejar_de_seguir(request, usuario_id):
    """
    Elimina la relación de seguimiento. El contenido del usuario
    dejado de seguir desaparece del feed de forma inmediata (RN-FED-06).
    """
    usuario_objetivo = get_object_or_404(User, pk=usuario_id)

    Seguimiento.objects.filter(
        seguidor=request.user,
        seguido=usuario_objetivo,
    ).delete()

    return redirect('feed:perfil_publico', username=usuario_objetivo.username)


@login_required
def perfil_publico(request, username):
    """
    Muestra el perfil público de un usuario con sus publicaciones
    recientes y el botón de seguir o dejar de seguir.
    """
    usuario_perfil = get_object_or_404(User, username=username)

    ya_sigue = Seguimiento.objects.filter(
        seguidor=request.user,
        seguido=usuario_perfil,
    ).exists()

    cantidad_seguidores = Seguimiento.objects.filter(
        seguido=usuario_perfil,
    ).count()

    cantidad_seguidos = Seguimiento.objects.filter(
        seguidor=usuario_perfil,
    ).count()

    publicaciones = Publicacion.objects.filter(
        autor=usuario_perfil,
    ).select_related('autor').order_by('-creado')

    es_propio = request.user == usuario_perfil

    contexto = {
        'usuario_perfil': usuario_perfil,
        'ya_sigue': ya_sigue,
        'cantidad_seguidores': cantidad_seguidores,
        'cantidad_seguidos': cantidad_seguidos,
        'publicaciones': publicaciones,
        'es_propio': es_propio,
    }
    return render(request, 'perfil/perfil_publico.html', contexto)


@login_required
def notificaciones(request):
    """
    Muestra todas las notificaciones del usuario autenticado,
    ordenadas de la más reciente a la más antigua.
    Al acceder a esta vista, las notificaciones se marcan como leídas.
    """
    lista_notificaciones = Notificacion.objects.filter(
        usuario=request.user,
    ).order_by('-creado')

    # Marcar como leídas todas las no leídas
    lista_notificaciones.filter(leida=False).update(leida=True)

    contexto = {
        'notificaciones': lista_notificaciones,
    }
    return render(request, 'feed/notificaciones.html', contexto)
