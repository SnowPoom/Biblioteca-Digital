from django.shortcuts import render


def colecciones(request):
    return render(request, 'colecciones/colecciones.html')
