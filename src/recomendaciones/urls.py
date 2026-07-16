from django.urls import path
from . import views

app_name = 'recomendaciones'

urlpatterns = [
    path('', views.recomendaciones, name='recomendaciones'),
]
