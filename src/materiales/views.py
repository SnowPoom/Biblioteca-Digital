from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST

from .forms import PublicacionLibroFormulario
from .models import Anotacion, Libro, LIMITE_CARACTERES_ANOTACION


def inicio(request):
    libros = Libro.objects.all()
    return render(request, 'inicio/inicio.html', {'libros': libros})


def vista_previa_material(request):
    return render(request, 'materiales/vista_previa_material.html', {
        'titulo': 'Nombre del Material',
        'autor': 'Autor',
        'descripcion': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.',
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


def lectura_material(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    anotaciones = []

    if request.user.is_authenticated:
        anotaciones = [
            anotacion.serializar_para_lectura()
            for anotacion in Anotacion.objects.filter(
                usuario=request.user,
                libro=libro,
            ).order_by('creado')
        ]

    return render(request, 'materiales/lectura_material.html', {
        'libro': libro,
        'anotaciones': anotaciones,
        'limite_caracteres_anotacion': LIMITE_CARACTERES_ANOTACION,
    })


@login_required(login_url='/auth/')
@require_POST
def editar_anotacion(request, anotacion_id):
    anotacion = get_object_or_404(
        Anotacion,
        pk=anotacion_id,
        usuario=request.user,
    )
    nuevo_contenido = request.POST.get('contenido', '').strip()

    if nuevo_contenido and Anotacion.validar_contenido(nuevo_contenido):
        anotacion.actualizar_contenido(nuevo_contenido)

    return redirect('materiales:lectura_material', libro_id=anotacion.libro_id)


@login_required(login_url='/auth/')
@require_POST
def eliminar_anotacion(request, anotacion_id):
    anotacion = get_object_or_404(
        Anotacion,
        pk=anotacion_id,
        usuario=request.user,
    )
    libro_id = anotacion.libro_id
    anotacion.delete()
    return redirect('materiales:lectura_material', libro_id=libro_id)


@login_required(login_url='/auth/')
def creacion_material(request):
    """Vista para la publicacion de un libro original, usando el template como editor Word."""
    formulario = PublicacionLibroFormulario(
        request.POST or None,
        request.FILES or None,
    )
    mensaje_exito = ''
    mensaje_error = ''

    if request.method == 'POST':
        if formulario.is_valid():
            libro = formulario.save(commit=False)
            libro.autor = request.user
            libro.save()
            formulario.save_m2m()

            resultado = libro.publicar()

            if resultado:
                mensaje_exito = (
                    f'El libro "{libro.titulo}" ha sido enviado a revision. '
                    f'Estado actual: {libro.get_estado_display()}.'
                )
            else:
                mensaje_error = 'No se pudo publicar el libro. Verifica que cumpla todos los requisitos.'
        else:
            mensaje_error = 'Corrige los errores indicados en el formulario.'

    return render(request, 'materiales/creacion_material.html', {
        'titulo': 'Creación del material',
        'formulario': formulario,
        'mensaje_exito': mensaje_exito,
        'mensaje_error': mensaje_error,
    })