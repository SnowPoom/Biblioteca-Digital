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

    from django.db.models import Q
    publicaciones = Publicacion.objects.filter(
        Q(libro__autor_id__in=ids_seguidos) | Q(coleccion__creador_id__in=ids_seguidos)
    ).select_related('libro__autor', 'coleccion__creador')

    republicaciones = Republicacion.objects.filter(
        republicado_por_id__in=ids_seguidos
    ).select_related('republicado_por', 'publicacion__libro__autor', 'publicacion__coleccion__creador')

    # Separar colecciones
    colecciones = publicaciones.filter(coleccion__isnull=False).order_by('-creado')

    # Combinar libros y republicaciones estrictamente por fecha
    libros = publicaciones.filter(libro__isnull=False)
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
        return redirect('perfil_publico_global', username=request.user.username)

    Seguimiento.objects.get_or_create(
        seguidor=request.user,
        seguido=usuario_objetivo,
    )
    return redirect('perfil_publico_global', username=usuario_objetivo.username)


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

    return redirect('perfil_publico_global', username=usuario_objetivo.username)


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

    from django.db.models import Q
    publicaciones_propias = Publicacion.objects.filter(
        Q(libro__autor=usuario_perfil) | Q(coleccion__creador=usuario_perfil)
    ).select_related('libro__autor', 'coleccion__creador')

    republicaciones_propias = Republicacion.objects.filter(
        republicado_por=usuario_perfil,
    ).select_related('republicado_por', 'publicacion__libro__autor', 'publicacion__coleccion__creador')

    from itertools import chain
    publicaciones = sorted(
        chain(publicaciones_propias, republicaciones_propias),
        key=lambda obj: obj.creado,
        reverse=True
    )

    es_propio = request.user == usuario_perfil
    
    borradores = []
    retirados = []
    if es_propio:
        from src.materiales.models import Libro
        borradores = Libro.objects.filter(
            autor=usuario_perfil,
            estado=Libro.BORRADOR,
        ).order_by('-creado')
        # RN-PUB-10: el autor conserva acceso privado a su material retirado.
        retirados = Libro.objects.filter(
            autor=usuario_perfil,
            estado=Libro.RETIRADO,
        ).order_by('-creado')

    from src.materiales.models import Coleccion
    from django.db.models import Q
    if es_propio:
        colecciones = Coleccion.objects.filter(
            Q(creador=usuario_perfil) | Q(participaciones__usuario=usuario_perfil)
        ).distinct().order_by('-creado')
    else:
        colecciones = Coleccion.objects.filter(
            Q(creador=usuario_perfil) | Q(participaciones__usuario=usuario_perfil),
            visibilidad=Coleccion.PUBLICA
        ).distinct().order_by('-creado')

    contexto = {
        'usuario_perfil': usuario_perfil,
        'ya_sigue': ya_sigue,
        'cantidad_seguidores': cantidad_seguidores,
        'cantidad_seguidos': cantidad_seguidos,
        'publicaciones': publicaciones,
        'borradores': borradores,
        'retirados': retirados,
        'colecciones': colecciones,
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
