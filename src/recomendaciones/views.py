from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from src.feed.models import Publicacion
from .models import DescarteRecomendacion
from .motor import MotorRecomendaciones


@login_required
def recomendaciones(request):
    """Vista de recomendaciones contextuales personalizadas.

    Acepta el parametro GET 'tipo' para filtrar entre
    'libros' o 'colecciones' (RN-REC-07).
    """
    tipo_filtro = request.GET.get('tipo', None)

    motor = MotorRecomendaciones(request.user)
    lista_recomendaciones = motor.obtener_recomendaciones(tipo=tipo_filtro)

    contexto = {
        'recomendaciones': lista_recomendaciones,
        'tipo_filtro': tipo_filtro,
    }
    return render(request, 'inicio/inicio.html', contexto)


@login_required
@require_POST
def descartar_recomendacion(request, publicacion_id):
    """Registra el descarte permanente de una recomendacion.

    RN-REC-04: La senal negativa queda registrada para ajustar
    recomendaciones futuras. El contenido descartado no volvera
    a recomendarse gracias al filtrado en el motor de recomendaciones.
    """
    publicacion = get_object_or_404(Publicacion, pk=publicacion_id)

    DescarteRecomendacion.objects.get_or_create(
        usuario=request.user,
        publicacion=publicacion,
    )

    return JsonResponse({'descartado': True})

