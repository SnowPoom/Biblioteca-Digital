from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Libro


def inicio(request):
    return render(request, 'inicio/inicio.html')


def vista_previa_material(request):
    return render(request, 'materiales/vista_previa_material.html', {
        'titulo': 'Nombre del Material',
        'autor': 'Autor',
        'descripcion': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since 1966.',
        'categorias': ['categoria', 'categoria'],
    })


def lectura_material(request, libro_id):
    libro = get_object_or_404(Libro, pk=libro_id)
    nombre_autor = libro.autor.get_full_name() or libro.autor.username
    perfil = request.user.perfil if request.user.is_authenticated else None
    return render(request, 'materiales/lectura_material.html', {
        'titulo': libro.titulo,
        'autor': nombre_autor,
        'contenido': f'Contenido del libro: {libro.titulo}',
        'notas': '',
        'libro': libro,
        'perfil': perfil,
    })


def creacion_material(request):
    return render(request, 'materiales/creacion_material.html', {
        'titulo': 'Nombre del Material',
    })


@login_required(login_url='/')
def descargar_libro(request, libro_id):
    libro = get_object_or_404(Libro, pk=libro_id)
    perfil = request.user.perfil

    # RN-EXP-05: La descarga se registra como metrica sin importar si supera la cuota
    libro.registrar_descarga()

    # RN-EXP-01: Solo se permite la descarga si las paginas no exceden la cuota disponible
    if not perfil.puede_descargar(libro.paginas):
        return HttpResponse(
            "no tiene suficientes páginas en su cuota",
            status=403,
            content_type='text/plain',
        )

    perfil.reducir_cuota(libro.paginas)

    # RN-EXP-06: El archivo generado incluye metadatos del autor original y la fuente
    contenido = libro.generar_contenido_descarga()
    tipo_contenido = (
        'application/pdf' if libro.archivo_formato == 'PDF'
        else 'application/epub+zip'
    )

    respuesta = HttpResponse(contenido, content_type=tipo_contenido)
    respuesta['Content-Disposition'] = f'attachment; filename="{libro.titulo}.{libro.archivo_formato.lower()}"'
    return respuesta