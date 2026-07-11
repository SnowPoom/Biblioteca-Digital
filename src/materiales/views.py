from django.shortcuts import render


def inicio(request):
    return render(request, 'inicio/inicio.html')


def vista_previa_material(request):
    return render(request, 'materiales/vista_previa_material.html', {
        'titulo': 'Nombre del Material',
        'autor': 'Autor',
        'descripcion': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since 1966.',
        'categorias': ['categoria', 'categoria'],
    })


def detalle_libro(request, pk):
    from src.feed.models import Publicacion
    from django.shortcuts import get_object_or_404
    libro = get_object_or_404(Publicacion, pk=pk)
    return render(request, 'materiales/vista_previa_material.html', {
        'libro': libro,
        'titulo': libro.titulo,
        'autor': libro.autor,
        'descripcion': libro.descripcion,
    })


def lectura_material(request):
    return render(request, 'materiales/lectura_material.html', {
        'titulo': 'Nombre del Material',
        'autor': 'Autor',
        'contenido': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since 1966.',
        'notas': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since 1966.',
    })


def creacion_material(request):
    return render(request, 'materiales/creacion_material.html', {
        'titulo': 'Nombre del Material',
    })