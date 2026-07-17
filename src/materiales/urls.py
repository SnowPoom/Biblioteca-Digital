from django.urls import path
from . import views

app_name = 'materiales'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('materiales/vista-previa/', views.vista_previa_material, name='vista_previa_material'),
    path('materiales/detalle/<int:pk>/', views.detalle_libro, name='detalle_libro'),
    path('materiales/lectura/<int:libro_id>/', views.lectura_material, name='lectura_material'),
    path('materiales/creacion/', views.creacion_material, name='creacion_material'),
    path('materiales/edicion/<int:pk>/', views.edicion_material, name='edicion_material'),
    path('materiales/autoguardar/', views.autoguardar_borrador, name='autoguardar_borrador_nuevo'),
    path('materiales/autoguardar/<int:pk>/', views.autoguardar_borrador, name='autoguardar_borrador'),
    path('materiales/republicar/<int:pk>/', views.republicar_libro, name='republicar_libro'),
    path('materiales/lectura/<int:libro_id>/anotacion/crear/', views.crear_anotacion, name='crear_anotacion'),
    path('materiales/anotacion/<int:anotacion_id>/editar/', views.editar_anotacion, name='editar_anotacion'),
    path('materiales/anotacion/<int:anotacion_id>/eliminar/', views.eliminar_anotacion, name='eliminar_anotacion'),
    path('materiales/<int:libro_id>/descargar/confirmar/<str:formato>/', views.confirmar_descarga, name='confirmar_descarga'),
    path('materiales/<int:libro_id>/descargar/<str:formato>/', views.descargar_libro, name='descargar_libro'),
    path('materiales/<int:libro_id>/descargar/pagina/<int:pagina>/<str:formato>/', views.descargar_pagina, name='descargar_pagina'),
    path('materiales/<int:libro_id>/descargar/rango/<int:inicio>/<int:fin>/<str:formato>/', views.descargar_rango, name='descargar_rango'),
    
    # Rutas de Colecciones
    path('colecciones/<int:coleccion_id>/', views.detalle_coleccion, name='detalle_coleccion'),
    path('colecciones/<int:coleccion_id>/invitar/', views.invitar_a_coleccion, name='invitar_a_coleccion'),
    path('colecciones/<int:coleccion_id>/solicitar-acceso/', views.solicitar_acceso_coleccion, name='solicitar_acceso_coleccion'),
    path('colecciones/<int:coleccion_id>/agregar_libro/', views.agregar_libro_coleccion, name='agregar_libro_coleccion'),
    path('colecciones/<int:coleccion_id>/eliminar_libro/<int:libro_id>/', views.eliminar_libro_coleccion, name='eliminar_libro_coleccion'),
    path('colecciones/invitaciones/<int:invitacion_id>/procesar/<str:accion>/', views.procesar_invitacion, name='procesar_invitacion'),
    path('colecciones/solicitudes/<int:solicitud_id>/procesar/<str:accion>/', views.procesar_solicitud, name='procesar_solicitud'),
    path('api/buscar-usuarios/', views.api_buscar_usuarios, name='api_buscar_usuarios'),
    path('api/buscar-libros/', views.api_buscar_libros, name='api_buscar_libros'),
]
