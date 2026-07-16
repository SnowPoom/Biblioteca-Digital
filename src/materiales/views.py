from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .forms import PublicacionLibroFormulario
from .models import Libro


def inicio(request):
    libros = Libro.objects.filter(estado=Libro.PUBLICADO)
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
    return render(request, 'materiales/lectura_material.html', {
        'libro': libro,
        'notas': 'Sección de notas...',
    })


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

            resultado, mensaje = libro.publicar()

            if resultado:
                from django.contrib import messages
                messages.success(request, f'El libro "{libro.titulo}" ha sido publicado con éxito.')
                return redirect('feed:perfil_publico', username=request.user.username)
            else:
                return redirect('feed:perfil_publico', username=request.user.username)
        else:
            mensaje_error = 'Corrige los errores indicados en el formulario.'

    return render(request, 'materiales/creacion_material.html', {
        'titulo': 'Creación del material',
        'formulario': formulario,
        'mensaje_exito': mensaje_exito,
        'mensaje_error': mensaje_error,
    })


@login_required(login_url='/auth/')
def edicion_material(request, pk):
    """Vista para editar un libro existente (borrador) y volver a intentar publicarlo."""
    libro = get_object_or_404(Libro, pk=pk, autor=request.user)
    formulario = PublicacionLibroFormulario(
        request.POST or None,
        request.FILES or None,
        instance=libro
    )
    mensaje_exito = ''
    mensaje_error = ''

    if request.method == 'POST':
        if formulario.is_valid():
            libro = formulario.save(commit=False)
            libro.save()
            formulario.save_m2m()

            resultado, mensaje = libro.publicar()

            if resultado:
                from django.contrib import messages
                messages.success(request, f'El libro "{libro.titulo}" ha sido publicado con éxito.')
                return redirect('feed:perfil_publico', username=request.user.username)
            else:
                return redirect('feed:perfil_publico', username=request.user.username)
        else:
            mensaje_error = 'Corrige los errores indicados en el formulario.'

    return render(request, 'materiales/creacion_material.html', {
        'titulo': 'Edición del material',
        'formulario': formulario,
        'mensaje_exito': mensaje_exito,
        'mensaje_error': mensaje_error,
        'es_edicion': True,
        'libro': libro,
    })

@login_required(login_url='/auth/')
def autoguardar_borrador(request, pk=None):
    from django.http import JsonResponse
    from .models import Libro
    from django.core.files.uploadedfile import UploadedFile

    if request.method == 'POST':
        if pk:
            try:
                libro = Libro.objects.get(pk=pk, autor=request.user)
            except Libro.DoesNotExist:
                return JsonResponse({'error': 'Libro no encontrado o sin permisos'}, status=403)
        else:
            libro = Libro(autor=request.user, estado=Libro.BORRADOR)

        titulo = request.POST.get('titulo', '').strip()
        contenido_texto = request.POST.get('contenido_texto', '')
        
        if not titulo and not pk:
            libro.titulo = '(Sin título)'
        elif titulo:
            libro.titulo = titulo
            
        if contenido_texto:
            libro.contenido_texto = contenido_texto

        if 'portada' in request.FILES:
            libro.portada = request.FILES['portada']

        if pk:
            libro.editar(usuario_editor=request.user)
        else:
            libro.save()

        # Manejo de categorias
        categorias_str = request.POST.get('categorias', '')
        if categorias_str:
            import json
            try:
                if categorias_str.startswith('['):
                    cat_ids = json.loads(categorias_str)
                else:
                    cat_ids = request.POST.getlist('categorias')
                libro.categorias.set(cat_ids)
            except Exception:
                pass
            
        return JsonResponse({'success': True, 'libro_id': libro.pk})
        
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required(login_url='/auth/')
def republicar_libro(request, pk):
    from django.contrib import messages
    from django.http import HttpResponseRedirect
    
    if request.method == 'POST':
        libro = get_object_or_404(Libro, pk=pk, estado=Libro.PUBLICADO)
        if libro.autor != request.user:
            republicacion, created = libro.republicar(usuario=request.user)
            if created:
                messages.success(request, f'Has republicado "{libro.titulo}" en tu perfil.')
        else:
            messages.error(request, 'No puedes republicar tu propio material.')
            
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
    return redirect('materiales:inicio')


@login_required(login_url='/auth/')
def descargar_libro(request, libro_id, formato='pdf'):
    libro = get_object_or_404(Libro, pk=libro_id)
    perfil = request.user.perfil

    formato = formato.lower()
    if formato not in ('pdf', 'epub'):
        formato = 'pdf'

    # RN-EXP-05: La descarga se registra como metrica sin importar si supera la cuota
    libro.registrar_descarga()

    # RN-EXP-01: Solo se permite la descarga si las paginas no exceden la cuota disponible
    if not perfil.puede_descargar(libro.numero_paginas):
        return HttpResponse(
            "no tiene suficientes páginas en su cuota",
            status=403,
            content_type='text/plain',
        )

    perfil.reducir_cuota(libro.numero_paginas)

    # RN-EXP-06: El archivo generado incluye metadatos del autor original y la fuente
    contenido = libro.generar_contenido_descarga(formato)

    if formato == 'epub':
        tipo_contenido = 'application/epub+zip'
        extension = 'epub'
    else:
        tipo_contenido = 'application/pdf'
        extension = 'pdf'

    respuesta = HttpResponse(contenido, content_type=tipo_contenido)
    respuesta['Content-Disposition'] = f'attachment; filename="{libro.titulo}.{extension}"'
    return respuesta