from django import forms
from src.materiales.models import Coleccion

class ColeccionForm(forms.ModelForm):
    class Meta:
        model = Coleccion
        fields = ['nombre', 'descripcion', 'visibilidad', 'limite_libros', 'categorias']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Inteligencia Artificial Básica'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la colección...'}),
            'visibilidad': forms.Select(attrs={'class': 'form-control'}),
            'limite_libros': forms.NumberInput(attrs={'class': 'form-control', 'min': '5', 'max': '20'}),
            'categorias': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }
        error_messages = {
            'nombre': {
                'required': 'Este campo es obligatorio.',
                'max_length': 'El nombre es demasiado largo.',
            },
            'limite_libros': {
                'required': 'Este campo es obligatorio.',
                'min_value': 'El mínimo es de 5 libros.',
                'max_value': 'El límite máximo es de 20 libros.',
                'invalid': 'Ingrese un número válido.',
            }
        }

    def clean_categorias(self):
        categorias = self.cleaned_data.get('categorias')
        if not categorias or categorias.count() == 0:
            raise forms.ValidationError("Debe asignar al menos una categoría temática.")
        return categorias
