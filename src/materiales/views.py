from django.contrib.auth.decorators import login_required
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
    anotaciones = []
    fragmentos_resaltados = []
    if request.user.is_authenticated:
        from .models import Anotacion
        anotaciones = Anotacion.objects.filter(
            usuario=request.user,
            libro=libro,
        )
        # RN-ANO-05: fragmentos que deben mostrarse destacados durante la lectura
        fragmentos_resaltados = libro.fragmentos_anotados_por(request.user)
    return render(request, 'materiales/lectura_material.html', {
        'libro': libro,
        'anotaciones': anotaciones,
        'fragmentos_resaltados': fragmentos_resaltados,
    })


@login_required(login_url='/auth/')
def crear_anotacion(request, libro_id):
    """Crea una anotacion via AJAX. Retorna JSON con los datos de la anotacion creada."""
    from django.http import JsonResponse
    from .models import Anotacion, LIMITE_CARACTERES_ANOTACION
    import json

    if request.method != 'POST':
        return JsonResponse({'error': 'Metodo no permitido'}, status=405)

    libro = get_object_or_404(Libro, id=libro_id)
    datos = json.loads(request.body)
    fragmento = datos.get('fragmento_texto', '').strip()
    contenido = datos.get('contenido', '').strip()
    tipo = datos.get('tipo_fragmento', Anotacion.TEXTO)

    if not fragmento or not contenido:
        return JsonResponse({'error': 'Fragmento y contenido son obligatorios'}, status=400)

    if len(contenido) > LIMITE_CARACTERES_ANOTACION:
        return JsonResponse({'error': f'Limite de {LIMITE_CARACTERES_ANOTACION} caracteres'}, status=400)

    # RN-ANO-04: Si ya existe una anotacion para este fragmento, redirigir a edicion
    existente = Anotacion.objects.filter(
        usuario=request.user, libro=libro, fragmento_texto=fragmento,
    ).first()

    if existente:
        return JsonResponse({
            'error': 'Ya existe una anotacion para este fragmento',
            'anotacion_id': existente.pk,
            'contenido': existente.contenido,
        }, status=409)

    anotacion = Anotacion.objects.create(
        usuario=request.user,
        libro=libro,
        fragmento_texto=fragmento,
        tipo_fragmento=tipo,
        contenido=contenido,
    )
    return JsonResponse({
        'id': anotacion.pk,
        'fragmento_texto': anotacion.fragmento_texto,
        'contenido': anotacion.contenido,
        'tipo_fragmento': anotacion.tipo_fragmento,
    }, status=201)


@login_required(login_url='/auth/')
def editar_anotacion(request, anotacion_id):
    """Edita una anotacion propia via AJAX."""
    from django.http import JsonResponse
    from .models import Anotacion, LIMITE_CARACTERES_ANOTACION
    import json

    if request.method != 'POST':
        return JsonResponse({'error': 'Metodo no permitido'}, status=405)

    anotacion = get_object_or_404(Anotacion, pk=anotacion_id, usuario=request.user)
    datos = json.loads(request.body)
    nuevo_contenido = datos.get('contenido', '').strip()

    if not nuevo_contenido:
        return JsonResponse({'error': 'El contenido no puede estar vacio'}, status=400)

    if len(nuevo_contenido) > LIMITE_CARACTERES_ANOTACION:
        return JsonResponse({'error': f'Limite de {LIMITE_CARACTERES_ANOTACION} caracteres'}, status=400)

    anotacion.editar(nuevo_contenido)
    return JsonResponse({
        'id': anotacion.pk,
        'contenido': anotacion.contenido,
    })


@login_required(login_url='/auth/')
def eliminar_anotacion(request, anotacion_id):
    """Elimina una anotacion propia via AJAX."""
    from django.http import JsonResponse
    from .models import Anotacion

    if request.method != 'POST':
        return JsonResponse({'error': 'Metodo no permitido'}, status=405)

    anotacion = get_object_or_404(Anotacion, pk=anotacion_id, usuario=request.user)
    anotacion.eliminar()
    return JsonResponse({'eliminado': True})



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