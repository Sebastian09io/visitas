"""
formularios
"""
import re # Importa el módulo de expresiones regulares.

# Librerias Django para formularios

from django import forms  # Importa la funcionalidad principal para crear formularios.
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm  # Formularios predefinidos para la autenticación y gestión de usuarios.

# Librerias para Modelos

from apps.funcionarios.models import Persona, Cargo, Dependencia, TipoDocumento  # Importa el modelo Persona desde la aplicación 'funcionarios'.
from django.contrib.auth.models import User  # Importa el modelo User para la autenticación y gestión de usuarios.
from django.contrib.auth import get_user_model  # Función para obtener el modelo de usuario actual.

# Librerias para envio de correos

from django.core.mail import send_mail  # Función para enviar correos electrónicos.
from django.contrib.auth.tokens import default_token_generator  # Generador de tokens para la autenticación segura en el restablecimiento de contraseña.

# Librerías para Codificación y Decodificación

from django.utils.http import urlsafe_base64_encode  # Función para codificar una cadena en base64 de manera segura para URLs.
from django.utils.encoding import force_bytes  # Función para forzar la codificación de una cadena.
from django.utils.translation import gettext as _

# Librerias para renderizar plantillas

from django.template.loader import render_to_string  # Función para renderizar plantillas en formato de cadena.
from django.contrib.sites.shortcuts import get_current_site  # Función para obtener el sitio actual en el contexto de la solicitud.
from django.contrib import messages

User = get_user_model()

# Clase de formulario registro
class PersonaForm(UserCreationForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = Persona
        fields = ['id_tipo_documento', 'identificacion', 'nombres', 'apellidos', 'telefono', 'correo', 'id_cargo', 'id_dependencia']
        # Aplicamos los estilos de Boostrap a cada campo
        widgets = {
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese sus apellidos'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su correo electrónico'}),
            'id_tipo_documento': forms.HiddenInput(),
            'id_cargo': forms.HiddenInput(),
            'id_dependencia': forms.HiddenInput(),
        }
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ejemplo@gmail.com '}),
        label="Correo"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su contraseña'}),
        label="Contraseña"
    )

# Clase de recuperacion de contraseña
class CustomPasswordResetForm(PasswordResetForm):
    correo = forms.EmailField(
        label="Correo Electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        print(f"Correo ingresado: {correo}")

        # Validación de correo electrónico
        if not correo:
            raise forms.ValidationError("Debe ingresar un correo electrónico.")

        # Verificar si el correo está asociado a un usuario en la base de datos
        try:
            user = User.objects.get(correo=correo)
        except User.DoesNotExist:
            raise forms.ValidationError("No existe un usuario con ese correo electrónico.")

        # Generar el token para el usuario
        token = default_token_generator.make_token(user)

        if self.request:
            # Obtener la URL para restablecer la contraseña
            current_site = get_current_site(self.request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"http://{current_site.domain}/recuperar/{uid}/{token}/"

            # Renderizar el cuerpo del correo electrónico
            email_body = render_to_string('email/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })

            # Enviar el correo electrónico
            send_mail(
                'Restablecer Contraseña',
                email_body,
                'from@example.com',
                [correo],
                fail_silently=False,
            )

            # Enviar mensaje para mostrar en el template
            messages.success(self.request, 'Se ha enviado un correo electrónico para restablecer tu contraseña.')

        return correo

# Clase de reestablecer contraseña
class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Extrae 'request' de kwargs si está presente
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # Aquí puedes usar self.request para acceder al objeto 'request' si es necesario
        return super().save(commit=commit)

    new_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class BootstrapFormMixin:
    def _init_bootstrap(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.widgets.TextInput, forms.widgets.Select,
                                    forms.widgets.EmailInput, forms.widgets.PasswordInput,
                                    forms.widgets.FileInput)):
                widget.attrs.update({'class': 'form-control'})

class PerfilForm(forms.ModelForm, BootstrapFormMixin):


    class Meta:
        model = Persona
        fields = ['id_tipo_documento', 'identificacion', 'nombres', 'apellidos', 'telefono', 'correo', 'id_cargo', 'id_dependencia']

    def __init__(self, *args, **kwargs):
        super(PerfilForm, self).__init__(*args, **kwargs)
        self.fields['id_tipo_documento'].queryset = TipoDocumento.objects.all()
        self.fields['id_tipo_documento'].empty_label = "Seleccione un tipo de documento"
        self.fields['id_cargo'].queryset = Cargo.objects.all()
        self.fields['id_cargo'].empty_label = "Seleccione un cargo"
        self.fields['id_dependencia'].queryset = Dependencia.objects.all()
        self.fields['id_dependencia'].empty_label = "Seleccione una dependencia"
        self._init_bootstrap()




    def save(self, commit=True):
        user = super(PerfilForm, self).save(commit=False)
        if commit:
            user.save()
        return user

class ImagenPerfilForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['imagen_perfil']
