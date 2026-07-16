from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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
