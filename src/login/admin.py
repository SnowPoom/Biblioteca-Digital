from django.contrib import admin

from .models import PerfilUsuario, RecuperacionContrasena


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'creado')
    search_fields = ('usuario__email', 'rol')


@admin.register(RecuperacionContrasena)
class RecuperacionContrasenaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'codigo', 'creado', 'usado')
    list_filter = ('usado',)
    search_fields = ('usuario__email',)
