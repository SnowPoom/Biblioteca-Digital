from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Publicacion, Republicacion, Seguimiento


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

    contexto = {
        'material_feed': material_feed,
        'colecciones': colecciones,
    }
    return render(request, 'feed/feed.html', contexto)
