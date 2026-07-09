from django.shortcuts import render


def busqueda(request):
    return render(request, 'busqueda/busqueda.html')
