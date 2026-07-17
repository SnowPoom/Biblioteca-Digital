from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from django.core.exceptions import ValidationError
from .forms import PublicacionLibroFormulario
from .models import Libro


def inicio(request):

    if request.user.is_authenticated:
        from src.recomendaciones.motor import MotorRecomendaciones
        motor = MotorRecomendaciones(request.user)
        recomendaciones = motor.obtener_recomendaciones()
    else:
        recomendaciones = []
    from src.materiales.models import Coleccion
    colecciones = Coleccion.objects.filter(visibilidad=Coleccion.PUBLICA).order_by('-creado')
    libros = Libro.objects.filter(estado=Libro.PUBLICADO)

    return render(request, 'inicio/inicio.html', {
        'libros': libros,
        'recomendaciones': recomendaciones,
        'colecciones': colecciones,
    })


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
    from .models import Coleccion
    libro = get_object_or_404(Publicacion, pk=pk)

    # RN-PUB-13: Las métricas del material solo se exponen al autor.
    material = Libro.objects.filter(pk=pk).first()
    metricas = material.metricas_para(request.user) if material else None
    colecciones_usuario = Coleccion.objects.filter(participaciones__usuario=request.user) if request.user.is_authenticated else []

    return render(request, 'materiales/vista_previa_material.html', {
        'colecciones_usuario': colecciones_usuario,
        'libro': libro,
        'titulo': libro.titulo,
        'autor': libro.autor,
        'descripcion': libro.descripcion,
        'metricas': metricas,
    })


def lectura_material(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    anotaciones = []
    fragmentos_resaltados = []
    from .models import Coleccion
    colecciones_usuario = Coleccion.objects.filter(participaciones__usuario=request.user) if request.user.is_authenticated else []
    
    if request.user.is_authenticated:
        from .models import Anotacion
        from src.recomendaciones.models import HistorialLectura
        from src.feed.models import Publicacion
        from django.utils import timezone

        anotaciones = Anotacion.objects.filter(
            usuario=request.user,
            libro=libro,
        )
        # RN-ANO-05: fragmentos que deben mostrarse destacados durante la lectura
        fragmentos_resaltados = libro.fragmentos_anotados_por(request.user)

        # Registrar la lectura para alimentar el motor de recomendaciones (RN-REC-01, RN-REC-03)
        pub = Publicacion.objects.filter(pk=libro.pk).first()
        if pub:
            historial, created = HistorialLectura.objects.get_or_create(
                usuario=request.user,
                publicacion=pub,
            )
            if not created:
                # Si ya lo habia leido, actualizamos la fecha para dar mas peso (RN-REC-08)
                historial.fecha = timezone.now()
                historial.save(update_fields=['fecha'])

    return render(request, 'materiales/lectura_material.html', {
        'libro': libro,
        'anotaciones': anotaciones,
        'fragmentos_resaltados': fragmentos_resaltados,
        'colecciones_usuario': colecciones_usuario,
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
        categorias_str = request.POST.get('categorias', '').strip()
        
        # Validación para evitar guardar borradores en blanco
        es_categorias_vacio = not categorias_str or categorias_str == '[]'
        if not pk and not titulo and not contenido_texto.strip() and not 'portada' in request.FILES and es_categorias_vacio:
            return JsonResponse({'success': False, 'msg': 'Borrador vacío, no se guardará.'})
        
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
def confirmar_descarga(request, libro_id, formato='pdf'):
    libro = get_object_or_404(Libro, pk=libro_id)
    perfil = request.user.perfil

    formato = formato.lower()
    if formato not in ('pdf', 'epub'):
        formato = 'pdf'

    # RN-EXP-02: Renovar la cuota si han pasado 30 dias antes de validarla
    perfil.renovar_cuota_si_corresponde()

    cuota_actual = perfil.cuota_descarga
    paginas_libro = libro.numero_paginas
    cuota_restante = cuota_actual - paginas_libro
    puede_descargar = perfil.puede_descargar(paginas_libro)

    # RN-EXP-02: Calcular la fecha de proxima renovacion para informar al usuario
    fecha_renovacion = perfil.fecha_proxima_renovacion()

    return render(request, 'materiales/confirmar_descarga.html', {
        'libro': libro,
        'formato': formato,
        'cuota_actual': cuota_actual,
        'paginas_libro': paginas_libro,
        'cuota_restante': cuota_restante,
        'puede_descargar': puede_descargar,
        'fecha_renovacion': fecha_renovacion,
    })


@login_required(login_url='/auth/')
def descargar_libro(request, libro_id, formato='pdf'):
    libro = get_object_or_404(Libro, pk=libro_id)
    perfil = request.user.perfil

    formato = formato.lower()
    if formato not in ('pdf', 'epub'):
        formato = 'pdf'

    # RN-EXP-05: La descarga se registra como metrica sin importar si supera la cuota
    libro.registrar_descarga()

    # RN-EXP-02: Renovar la cuota si han pasado 30 dias antes de intentar usarla
    perfil.renovar_cuota_si_corresponde()

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

@login_required(login_url='/auth/')
def descargar_pagina(request, libro_id, pagina, formato='pdf'):
    return descargar_rango(request, libro_id, pagina, pagina, formato)

@login_required(login_url='/auth/')
def descargar_rango(request, libro_id, inicio, fin, formato='pdf'):
    libro = get_object_or_404(Libro, pk=libro_id)
    perfil = request.user.perfil

    formato = formato.lower()
    if formato not in ('pdf', 'epub'):
        formato = 'pdf'

    paginas_a_descargar = fin - inicio + 1
    if paginas_a_descargar <= 0:
        return HttpResponse("Rango de páginas inválido", status=400)

    # RN-EXP-05: La descarga se registra como metrica sin importar si supera la cuota
    libro.registrar_descarga()

    # RN-EXP-02: Renovar la cuota si han pasado 30 dias antes de intentar usarla
    perfil.renovar_cuota_si_corresponde()

    # RN-EXP-01: Solo se permite la descarga si las paginas no exceden la cuota disponible
    if not perfil.puede_descargar(paginas_a_descargar):
        return HttpResponse(
            "no tiene suficientes páginas en su cuota",
            status=403,
            content_type='text/plain',
        )

    perfil.reducir_cuota(paginas_a_descargar)

    # RN-EXP-06: El archivo generado incluye metadatos del autor original y la fuente
    contenido = libro.generar_contenido_descarga(formato, inicio, fin)

    if formato == 'epub':
        tipo_contenido = 'application/epub+zip'
        extension = 'epub'
    else:
        tipo_contenido = 'application/pdf'
        extension = 'pdf'

    respuesta = HttpResponse(contenido, content_type=tipo_contenido)
    rango_str = f"_paginas_{inicio}_a_{fin}" if inicio != fin else f"_pagina_{inicio}"
    respuesta['Content-Disposition'] = f'attachment; filename="{libro.titulo}{rango_str}.{extension}"'
    return respuesta

# -----------------------------------------------------------------------------
# VISTAS DE COLECCIONES
# -----------------------------------------------------------------------------
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Coleccion, ParticipacionColeccion, InvitacionColeccion, SolicitudAccesoColeccion

User = get_user_model()

@login_required
def detalle_coleccion(request, coleccion_id):
    coleccion = get_object_or_404(Coleccion, id=coleccion_id)
    participaciones = coleccion.participantes_activos().select_related('usuario')
    es_miembro = participaciones.filter(usuario=request.user).exists()
    es_admin = participaciones.filter(usuario=request.user, rol=ParticipacionColeccion.ADMINISTRADOR).exists()
    
    # Si la coleccion es privada y no es miembro, denegar acceso
    if coleccion.visibilidad == Coleccion.PRIVADA and not es_miembro:
        return HttpResponse("Acceso denegado.", status=403)
        
    solicitudes = []
    invitaciones = []
    if es_admin:
        solicitudes = coleccion.solicitudes.filter(estado=SolicitudAccesoColeccion.PENDIENTE)
        invitaciones = coleccion.invitaciones.filter(estado=InvitacionColeccion.PENDIENTE)
        
    libros_disponibles = Libro.objects.filter(estado=Libro.PUBLICADO).exclude(id__in=coleccion.libros.all()) if es_miembro else []
    libros_coleccion = coleccion.librocoleccion_set.select_related('libro', 'agregado_por').all()
    
    bitacora = coleccion.bitacora.all() if es_miembro else []
    
    context = {
        'coleccion': coleccion,
        'participaciones': participaciones,
        'es_miembro': es_miembro,
        'es_admin': es_admin,
        'solicitudes': solicitudes,
        'invitaciones': invitaciones,
        'libros_disponibles': libros_disponibles,
        'libros_coleccion': libros_coleccion,
        'bitacora': bitacora,
    }
    return render(request, 'colecciones/detalle_coleccion.html', context)

@login_required
def agregar_libro_coleccion(request, coleccion_id):
    if request.method == 'POST':
        coleccion = get_object_or_404(Coleccion, id=coleccion_id)
        if not coleccion.participaciones.filter(usuario=request.user).exists():
            messages.error(request, "No eres participante de esta colección.")
            return redirect('materiales:detalle_coleccion', coleccion_id=coleccion.id)
            
        libro_id = request.POST.get('libro_id')
        if libro_id:
            try:
                libro = get_object_or_404(Libro, id=libro_id, estado=Libro.PUBLICADO)
                coleccion.agregar_libro(request.user, libro)
                messages.success(request, f"Libro '{libro.titulo}' agregado a la colección.")
            except ValidationError as e:
                messages.error(request, str(e.message) if hasattr(e, 'message') else str(e))
            return redirect('materiales:detalle_coleccion', coleccion_id=coleccion.id)
    return redirect('materiales:inicio')

@login_required
def eliminar_libro_coleccion(request, coleccion_id, libro_id):
    if request.method == 'POST':
        coleccion = get_object_or_404(Coleccion, id=coleccion_id)
        libro = get_object_or_404(Libro, id=libro_id)
        try:
            coleccion.eliminar_libro(request.user, libro)
            messages.success(request, f"Libro '{libro.titulo}' eliminado de la colección.")
        except PermissionError as e:
            messages.error(request, str(e))
        return redirect('materiales:detalle_coleccion', coleccion_id=coleccion.id)
    return redirect('materiales:inicio')

@login_required
def invitar_a_coleccion(request, coleccion_id):
    if request.method == 'POST':
        coleccion = get_object_or_404(Coleccion, id=coleccion_id)
        username = request.POST.get('username')
        if username:
            try:
                usuario_invitado = User.objects.get(username=username)
                exito, msg = coleccion.invitar_usuario(request.user, usuario_invitado)
                if exito:
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
            except User.DoesNotExist:
                messages.error(request, "El usuario especificado no existe.")
            except PermissionError as e:
                messages.error(request, str(e))
    return redirect('materiales:detalle_coleccion', coleccion_id=coleccion_id)

@login_required
def solicitar_acceso_coleccion(request, coleccion_id):
    if request.method == 'POST':
        coleccion = get_object_or_404(Coleccion, id=coleccion_id)
        try:
            exito, msg = coleccion.solicitar_acceso(request.user)
            if exito:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        except (PermissionError, ValueError) as e:
            messages.error(request, str(e))
    return redirect('materiales:detalle_coleccion', coleccion_id=coleccion_id)

@login_required
@login_required
@login_required
def procesar_invitacion(request, invitacion_id, accion):
    if request.method != 'POST':
        return redirect('feed:notificaciones')
        
    invitacion = get_object_or_404(InvitacionColeccion, id=invitacion_id, estado=InvitacionColeccion.PENDIENTE)
    try:
        if accion == 'aceptar':
            exito, msg = invitacion.aceptar(request.user)
            if exito:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        elif accion == 'rechazar':
            exito, msg = invitacion.rechazar(request.user)
            if exito:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
    except PermissionError as e:
        messages.error(request, str(e))
        
    from django.utils.http import url_has_allowed_host_and_scheme
    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('feed:notificaciones')

@login_required
def procesar_solicitud(request, solicitud_id, accion):
    if request.method != 'POST':
        return redirect('materiales:inicio')
        
    solicitud = get_object_or_404(SolicitudAccesoColeccion, id=solicitud_id, estado=SolicitudAccesoColeccion.PENDIENTE)
    try:
        if accion == 'aprobar':
            if solicitud.aprobar(request.user):
                messages.success(request, "Solicitud aprobada.")
            else:
                messages.error(request, "No se pudo aprobar (límite de participantes).")
        elif accion == 'rechazar':
            if solicitud.rechazar(request.user):
                messages.success(request, "Solicitud rechazada.")
    except PermissionError as e:
        messages.error(request, str(e))
        
    from django.utils.http import url_has_allowed_host_and_scheme
    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('materiales:detalle_coleccion', coleccion_id=solicitud.coleccion.id)

@login_required
def api_buscar_usuarios(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        from django.http import JsonResponse
        return JsonResponse({'users': []})

    from django.db.models import Q
    from django.contrib.auth.models import User
    from django.http import JsonResponse

    usuarios = User.objects.filter(
        Q(username__icontains=q) |
        Q(first_name__icontains=q) |
        Q(last_name__icontains=q)
    ).exclude(id=request.user.id)[:10]

    data = []
    for u in usuarios:
        data.append({
            'username': u.username,
            'full_name': u.get_full_name()
        })
    return JsonResponse({'users': data})

from django.http import JsonResponse
@login_required
def api_buscar_libros(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'libros': []})
    libros = Libro.objects.filter(estado=Libro.PUBLICADO, titulo__icontains=q)[:10]
    results = [{'id': libro.id, 'titulo': libro.titulo, 'autor': libro.autor.username} for libro in libros]
    return JsonResponse({'libros': results})

def ajustar_limite(request, coleccion_id):
    if request.method == 'POST':
        coleccion = get_object_or_404(Coleccion, id=coleccion_id)
        if not coleccion.es_administrador(request.user):
            messages.error(request, "Solo los administradores pueden ajustar el límite.")
            return redirect('materiales:detalle_coleccion', coleccion_id=coleccion_id)
        
        try:
            nuevo_limite = int(request.POST.get('limite_libros', 20))
            if 5 <= nuevo_limite <= 20:
                coleccion.limite_libros = nuevo_limite
                coleccion.save()
                messages.success(request, f"Límite de libros actualizado a {nuevo_limite}.")
            else:
                messages.error(request, "El límite debe estar entre 5 y 20.")
        except ValueError:
            messages.error(request, "Límite inválido.")
            
    return redirect('materiales:detalle_coleccion', coleccion_id=coleccion_id)
