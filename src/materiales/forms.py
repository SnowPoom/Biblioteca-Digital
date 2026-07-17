from django import forms
from django.utils.html import strip_tags

from .models import Libro, Categoria


class PublicacionLibroFormulario(forms.ModelForm):
    """Formulario para la publicacion de un libro original en la plataforma."""

    categorias = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={
            'required': 'El libro debe pertenecer a al menos una categoria tematica.',
        },
    )

    class Meta:
        model = Libro
        fields = ['titulo', 'portada', 'contenido_texto', 'numero_paginas', 'categorias']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'id': 'id-titulo',
            }),
            'contenido_texto': forms.HiddenInput(attrs={
                'id': 'id-contenido-texto',
            }),
            'numero_paginas': forms.HiddenInput(attrs={
                'id': 'id-numero-paginas',
            }),
            'portada': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'id': 'id-portada',
            }),
        }
        error_messages = {
            'titulo': {
                'required': 'El titulo del libro es obligatorio.',
            },
            'portada': {
                'required': 'La portada del libro es obligatoria.',
            },
            'contenido_texto': {
                'required': 'El contenido textual es obligatorio.',
            },
        }

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        query = Libro.objects.filter(titulo__iexact=titulo)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
            
        if query.exists():
            raise forms.ValidationError('Ya existe un libro con este mismo nombre.')
        return titulo

    def clean_contenido_texto(self):
        contenido = self.cleaned_data.get('contenido_texto', '')
        
        # Eliminar etiquetas HTML y espacios en blanco
        texto_limpio = strip_tags(contenido).replace('&nbsp;', '').strip()
        
        if not texto_limpio:
            raise forms.ValidationError(
                'El libro debe tener contenido textual (palabras reales). No se permiten libros vacíos o que solo contengan imágenes.'
            )
        return contenido

    def clean_numero_paginas(self):
        paginas = self.cleaned_data.get('numero_paginas', 0)
        if paginas > 500:
            raise forms.ValidationError(
                'El libro no puede exceder las 500 paginas.'
            )
        if paginas < 1:
            raise forms.ValidationError(
                'El libro debe tener al menos 1 pagina.'
            )
        return paginas

    def clean_portada(self):
        portada = self.cleaned_data.get('portada')
        if not portada and not (self.instance and self.instance.portada):
            raise forms.ValidationError(
                'La portada es obligatoria. Sube una imagen para la portada del libro.'
            )
        return portada

class ComentarioRetroalimentacionForm(forms.ModelForm):
    """Formulario para añadir comentarios de retroalimentación a libros en colecciones."""
    class Meta:
        from .models import ComentarioRetroalimentacion
        model = ComentarioRetroalimentacion
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe tu comentario o sugerencia de mejora aquí...',
                'id': 'id_texto_comentario'
            })
        }
        error_messages = {
            'texto': {
                'required': 'El texto del comentario no puede estar vacío.'
            }
        }
