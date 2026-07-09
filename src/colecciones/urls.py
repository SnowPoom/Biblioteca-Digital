from django.urls import path
from . import views

app_name = 'colecciones'

urlpatterns = [
    path('', views.colecciones, name='colecciones'),
]
