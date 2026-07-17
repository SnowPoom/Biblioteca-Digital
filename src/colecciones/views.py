from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from src.materiales.models import Coleccion, ParticipacionColeccion
from .forms import ColeccionForm



@login_required
def crear_coleccion(request):
    """Crea una nueva colección asignando al usuario como creador y administrador."""
    if request.method == 'POST':
        form = ColeccionForm(request.POST)
        if form.is_valid():
            from django.db import transaction
            with transaction.atomic():
                coleccion = form.save(commit=False)
                coleccion.creador = request.user
                coleccion.save()
                form.save_m2m() # Guardar las categorías
            
            messages.success(request, "Colección creada exitosamente.")
            return redirect('feed:perfil_publico', username=request.user.username)
    else:
        form = ColeccionForm()
        
    return render(request, 'colecciones/crear_coleccion.html', {
        'form': form
    })

@login_required
def editar_coleccion(request, coleccion_id):
    coleccion = get_object_or_404(Coleccion, id=coleccion_id)
    
    es_admin = coleccion.es_administrador(request.user)
    if not es_admin:
        messages.error(request, "No tienes permisos para editar esta colección.")
        return redirect('materiales:detalle_coleccion', coleccion_id=coleccion.id)

    if request.method == 'POST':
        form = ColeccionForm(request.POST, instance=coleccion)
        if form.is_valid():
            form.save()
            messages.success(request, "Colección actualizada exitosamente.")
            return redirect('materiales:detalle_coleccion', coleccion_id=coleccion.id)
    else:
        form = ColeccionForm(instance=coleccion)
        
    return render(request, 'colecciones/crear_coleccion.html', {
        'form': form,
        'es_edicion': True,
        'coleccion': coleccion
    })
