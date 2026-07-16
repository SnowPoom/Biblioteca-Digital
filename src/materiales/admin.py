from django.contrib import admin

from .models import Categoria, Libro


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'estado', 'numero_paginas', 'creado')
    list_filter = ('estado', 'categorias')
    search_fields = ('titulo', 'autor__username')
