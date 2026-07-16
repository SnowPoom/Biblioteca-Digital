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
]
