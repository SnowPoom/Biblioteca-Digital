from django.urls import path
from . import views

app_name = 'recomendaciones'

urlpatterns = [
    path('', views.recomendaciones, name='recomendaciones'),
    path(
        'descartar/<int:publicacion_id>/',
        views.descartar_recomendacion,
        name='descartar_recomendacion',
    ),
]

