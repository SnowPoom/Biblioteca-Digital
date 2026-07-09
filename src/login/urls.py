from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('olvido/', views.olvido_contrasena, name='olvido_contrasena'),
    path('reiniciar/<uuid:codigo>/', views.reiniciar_contrasena, name='reiniciar_contrasena'),
    path('panel/', views.panel, name='panel'),
    path('cerrar/', views.cerrar_sesion, name='cerrar_sesion'),
]