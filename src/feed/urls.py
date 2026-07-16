from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('perfil/<str:username>/', views.perfil_publico, name='perfil_publico'),
    path('seguir/<int:usuario_id>/', views.seguir_usuario, name='seguir_usuario'),
    path('dejar-de-seguir/<int:usuario_id>/', views.dejar_de_seguir, name='dejar_de_seguir'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
]
