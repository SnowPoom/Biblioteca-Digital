from django.shortcuts import render

from django.http import HttpResponse

def inicio(request):
    return HttpResponse("<h1>Hola Mundo - Biblioteca Digital</h1>")