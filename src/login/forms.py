from django import forms
from django.contrib.auth import authenticate, get_user_model

from .models import PerfilUsuario


User = get_user_model()

TIPOS_USUARIO = [
    (PerfilUsuario.ESTUDIANTE, 'Estudiante'),
    (PerfilUsuario.PROFESOR, 'Profesor'),
]

AVATARES_DISPONIBLES = [
    f'avatar{i}.png' for i in range(1, 8)
]


class InicioSesionFormulario(forms.Form):
    correo = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(
            attrs={
                'class': 'field-input',
                'id': 'correo',
                'autocomplete': 'email',
                'placeholder': 'correo@ejemplo.com',
            }
        ),
    )
    contrasena = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'field-input',
                'id': 'contrasena',
                'autocomplete': 'current-password',
            }
        ),
    )

    error_messages = {
        'invalid_login': 'Correo electrónico o contraseña incorrectos.',
        'inactive': 'Esta cuenta no está activa.',
    }

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.usuario = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        correo = cleaned_data.get('correo')
        contrasena = cleaned_data.get('contrasena')

        if correo and contrasena:
            usuario = authenticate(
                request=self.request,
                username=correo,
                password=contrasena,
            )

            if usuario is None and '@' in correo:
                try:
                    usuario_obj = User.objects.get(email__iexact=correo)
                except User.DoesNotExist:
                    usuario_obj = None

                if usuario_obj is not None:
                    usuario = authenticate(
                        request=self.request,
                        username=usuario_obj.get_username(),
                        password=contrasena,
                    )

            if usuario is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            if not usuario.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )

            self.usuario = usuario

        return cleaned_data


class RegistroFormulario(forms.Form):
    nombre = forms.CharField(
        label='Nombre completo',
        widget=forms.TextInput(
            attrs={
                'class': 'field-input',
                'id': 'nombre',
                'placeholder': 'Tu nombre',
            }
        ),
    )
    nickname = forms.CharField(
        label='Nickname',
        widget=forms.TextInput(
            attrs={
                'class': 'field-input',
                'id': 'nickname',
                'placeholder': 'Tu nickname',
            }
        ),
    )
    correo = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(
            attrs={
                'class': 'field-input',
                'id': 'correo',
                'autocomplete': 'email',
                'placeholder': 'correo@ejemplo.com',
            }
        ),
    )
    contrasena1 = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'field-input',
                'id': 'contrasena1',
                'autocomplete': 'new-password',
            }
        ),
    )
    contrasena2 = forms.CharField(
        label='Confirmar contraseña',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'field-input',
                'id': 'contrasena2',
                'autocomplete': 'new-password',
            }
        ),
    )
    rol = forms.ChoiceField(
        label='Tipo de usuario',
        choices=TIPOS_USUARIO,
        widget=forms.Select(
            attrs={
                'class': 'field-input',
                'id': 'rol',
            }
        ),
    )
    avatar = forms.CharField(
        widget=forms.HiddenInput(
            attrs={'id': 'avatar'}
        ),
        initial='avatar1.png',
    )

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar', 'avatar1.png')
        if avatar not in AVATARES_DISPONIBLES:
            raise forms.ValidationError('El avatar seleccionado no es valido.')
        return avatar

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip().lower()
        if User.objects.filter(email__iexact=correo).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return correo

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname'].strip()
        if User.objects.filter(username__iexact=nickname).exists():
            raise forms.ValidationError('Este nickname ya está en uso.')
        return nickname

    def clean(self):
        cleaned_data = super().clean()
        contrasena1 = cleaned_data.get('contrasena1')
        contrasena2 = cleaned_data.get('contrasena2')

        if contrasena1 and contrasena2 and contrasena1 != contrasena2:
            raise forms.ValidationError('Las contraseñas deben coincidir.')

        return cleaned_data

    def save(self):
        correo = self.cleaned_data['correo']
        contrasena = self.cleaned_data['contrasena1']
        rol = self.cleaned_data['rol']
        nombre = self.cleaned_data['nombre']
        nickname = self.cleaned_data['nickname']
        avatar = self.cleaned_data.get('avatar', 'avatar1.png')

        usuario = User.objects.create_user(
            username=nickname,
            email=correo,
            password=contrasena,
            first_name=nombre,
        )
        PerfilUsuario.objects.create(usuario=usuario, rol=rol, avatar=avatar)
        return usuario


class OlvidoContrasenaFormulario(forms.Form):
    correo = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(
            attrs={
                'class': 'field-input',
                'id': 'correo',
                'autocomplete': 'email',
                'placeholder': 'correo@ejemplo.com',
            }
        ),
    )

    def obtener_usuario(self):
        correo = self.cleaned_data.get('correo', '').strip().lower()
        try:
            return User.objects.get(email__iexact=correo)
        except User.DoesNotExist:
            return None


class ReinicioContrasenaFormulario(forms.Form):
    contrasena1 = forms.CharField(
        label='Nueva contraseña',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'field-input',
                'id': 'contrasena1',
                'autocomplete': 'new-password',
            }
        ),
    )
    contrasena2 = forms.CharField(
        label='Confirmar nueva contraseña',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'field-input',
                'id': 'contrasena2',
                'autocomplete': 'new-password',
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        contrasena1 = cleaned_data.get('contrasena1')
        contrasena2 = cleaned_data.get('contrasena2')

        if contrasena1 and contrasena2 and contrasena1 != contrasena2:
            raise forms.ValidationError('Las contraseñas deben coincidir.')

        return cleaned_data
