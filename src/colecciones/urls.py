from django.urls import path
from . import views

app_name = 'colecciones'

urlpatterns = [
    path('crear/', views.crear_coleccion, name='crear_coleccion'),
    path('editar/<int:coleccion_id>/', views.editar_coleccion, name='editar_coleccion'),
]
