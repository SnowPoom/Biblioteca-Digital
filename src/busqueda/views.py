from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from src.login.models import PerfilUsuario
from src.materiales.models import Categoria, Coleccion, Libro


@login_required
def busqueda(request):
    query = request.GET.get('q', '').strip()
    rol_filtro = request.GET.get('rol', '').strip()

    libros = Libro.objects.none()
    colecciones = Coleccion.objects.none()

    if query:
        libros = Libro.objects.filter(
            estado=Libro.PUBLICADO,
        ).filter(
            Q(titulo__icontains=query)
            | Q(categorias__nombre__icontains=query)
        ).select_related('autor').distinct()

        colecciones = Coleccion.objects.filter(
            visibilidad=Coleccion.PUBLICA,
        ).filter(
            Q(nombre__icontains=query)
            | Q(categorias__nombre__icontains=query)
        ).distinct()

        if rol_filtro in (PerfilUsuario.ESTUDIANTE, PerfilUsuario.PROFESOR):
            libros = libros.filter(autor__perfil__rol=rol_filtro)

    contexto = {
        'libros': libros,
        'colecciones': colecciones,
        'query': query,
        'rol_filtro': rol_filtro,
        'hay_resultados': libros.exists() or colecciones.exists(),
        'busqueda_realizada': bool(query),
    }
    return render(request, 'busqueda/busqueda.html', contexto)
