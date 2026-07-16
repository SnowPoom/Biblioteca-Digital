from django.contrib import admin

from .models import Anotacion, Categoria, Libro


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'estado', 'numero_paginas', 'creado')
    list_filter = ('estado', 'categorias')
    search_fields = ('titulo', 'autor__username')


@admin.register(Anotacion)
class AnotacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'tipo_fragmento', 'contenido', 'creado')
    list_filter = ('tipo_fragmento', 'libro')
    search_fields = ('contenido', 'fragmento_texto', 'usuario__username')
