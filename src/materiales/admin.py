from django.contrib import admin

from .models import Categoria, Libro, Anotacion


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
    list_display = ('usuario', 'libro', 'tipo_fragmento', 'fragmento_texto', 'creado')
    list_filter = ('tipo_fragmento',)
    search_fields = ('usuario__username', 'libro__titulo', 'fragmento_texto')

from .models import ComentarioRetroalimentacion

@admin.register(ComentarioRetroalimentacion)
class ComentarioRetroalimentacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'coleccion', 'fecha')
    list_filter = ('coleccion', 'fecha')
    search_fields = ('usuario__username', 'texto')

    def has_delete_permission(self, request, obj=None):
        return False
