from django.urls import path
from . import views

app_name = 'materiales'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('materiales/vista-previa/', views.vista_previa_material, name='vista_previa_material'),
<<<<<<< HEAD
    path('materiales/detalle/<int:pk>/', views.detalle_libro, name='detalle_libro'),
    path('materiales/lectura/', views.lectura_material, name='lectura_material'),
=======
    path('materiales/lectura/<int:libro_id>/', views.lectura_material, name='lectura_material'),
>>>>>>> 611c206086779698a35086298d2c145ca4bc942f
    path('materiales/creacion/', views.creacion_material, name='creacion_material'),
]