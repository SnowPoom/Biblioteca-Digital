from django.urls import path
from . import views

app_name = 'colecciones'

urlpatterns = [
    path('crear/', views.crear_coleccion, name='crear_coleccion'),
]
