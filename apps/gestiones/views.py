# Librerias para la autenticacion y gestion de usuarios

from django.contrib.auth import logout  # Función para cerrar sesión de un usuario.
from django.contrib.auth import authenticate, login  # Funciones para autenticar y loguear usuarios.
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView  # Vistas de Django para restablecimiento de contraseña.
from django.contrib.auth import get_user_model  # Función para obtener el modelo de usuario actual.

from django.shortcuts import redirect, render,get_object_or_404  # Funciones de atajo de Django: redirect para redirigir a una URL y render para renderizar plantillas HTML.

from django.contrib import messages  # Módulo para generar alertas y mensajes de feedback para el usuario.

# Librerías para Formularios Personalizados

from .forms import LoginForm  # Importa el formulario personalizado de inicio de sesión.
from .forms import PersonaForm  # Importa el formulario personalizado para la gestión de personas.
from .forms import CustomPasswordResetForm  # Importa el formulario personalizado para la solicitud de restablecimiento de contraseña.
from .forms import CustomSetPasswordForm  # Importa el formulario personalizado para establecer una nueva contraseña.

from apps.funcionarios.models import Persona, TipoDocumento, Cargo, Dependencia  # Importa el modelo Persona desde la aplicación 'funcionarios'.

from django.urls import reverse_lazy  # Función para obtener una URL perezosamente, útil para redireccionamientos y configuración de vistas basadas en clase.

from django.utils.encoding import force_str  # Función para forzar la codificación de una cadena.
from django.utils.http import urlsafe_base64_decode  # Función para decodificar una cadena base64 de manera segura para URLs.
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.forms.models import model_to_dict
from .forms import PerfilForm, ImagenPerfilForm



from django.core.serializers.json import DjangoJSONEncoder
import json


def Home(request):
    return render(request,'home.html')

# Registro de usuario

def registro(request):
    if request.method == 'POST': # Verifica si la solicitud es POST (cuando se envía el formulario)
        form = PersonaForm(request.POST) # Crea una instancia de PersonaForm con los datos POST recibidos
        if form.is_valid():
            form.save() # Guardar datos de persona en la base de datos
            return redirect('gestiones:login')
    else:
        form = PersonaForm()

    # Listar las opciones en el formulario de registro

    tipo_documento_opciones = json.dumps(list(TipoDocumento.objects.values('id', 'nombre')), cls=DjangoJSONEncoder)
    cargo_opciones = json.dumps(list(Cargo.objects.values('id', 'nombre')), cls=DjangoJSONEncoder)
    dependencia_opciones = json.dumps(list(Dependencia.objects.values('id', 'nombre')), cls=DjangoJSONEncoder)

    context = {
        'form': form,
        'tipo_documento_opciones': tipo_documento_opciones,
        'cargo_opciones': cargo_opciones,
        'dependencia_opciones': dependencia_opciones,
    }

    return render(request, 'registro.html', context)

def calendario(request):
    """
    pasa de login a principal
    """
    user = request.user
    nombre_completo = f"{user.nombres} {user.apellidos}"
    context = {
        'nombre_completo': nombre_completo
    }
    return render(request, 'calendario.html',context)



#cerrar sesion por ahora
def logout_view(request):
    """
    perfil out
    """
    logout(request)
    return redirect('gestiones:login')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                user = Persona.objects.get(correo=email)
                if not user.estado:  # Verificar si el estado del usuario es False
                    messages.error(request, "Su cuenta está desactivada. Por favor, contacte con el administrador.")
                    return redirect('gestiones:login')
                else:
                    user_auth = authenticate(request, username=user.correo, password=password)
                    if user_auth is not None:
                        login(request, user_auth)
                        if user.is_superuser:  # Verificar si el usuario es superusuario
                            return redirect('reservas:gestion_perfil')  # Redirigir a la vista de administración
                        return redirect('gestiones:calendario')  # Redirigir a la página principal después de iniciar sesión
                    else:
                        messages.error(request, "Correo o contraseña incorrectos.")
            except Persona.DoesNotExist:
                messages.error(request, "Usuario no encontrado.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

User = get_user_model()
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('login')  # URL a donde redirigir después de cambiar la contraseña

    def form_valid(self, form):
        # Cambiar la contraseña del usuario
        user = form.save()

        # Actualizar el correo electrónico en el modelo Persona
        try:
            persona = Persona.objects.get(correo=user.email)
            persona.correo = user.email  # Actualiza el correo electrónico con el nuevo valor
            persona.save()
        except Persona.DoesNotExist:
            # Maneja el caso donde no existe una Persona asociada al correo electrónico
            pass

        return super().form_valid(form)

    def get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            return user
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None




#perfil_usuario
@login_required
def perfil_usuario(request):
    """
    Perfil usuario
    """    
    user = request.user
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=user)
        if form.is_valid():
            original_data = model_to_dict(user)
            form_data = form.cleaned_data
            changes = {key: form_data[key] for key in form_data if form_data[key] != original_data.get(key)}
            
            if changes:
                form.save()
                messages.success(request, 'Perfil actualizado correctamente.')
            else:
                messages.info(request, 'No se realizaron cambios en el perfil.')
            return redirect('gestiones:perfil_usuario')  # Redirigir para evitar reenvío de formulario
    else:
        form = PerfilForm(instance=user)

    nombre_completo = f"{user.nombres} {user.apellidos}"
    context = {
        'form': form,
        'nombre_completo': nombre_completo
        
    }

    return render(request, 'perfil_usuario.html', context)

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('gestiones:login')

@login_required
def inhabilitar_cuenta(request):
    user = request.user
    persona = get_object_or_404(Persona, correo=user.correo) 
    persona.estado = False
    persona.save()
    messages.success(request, 'Cuenta eliminada correctamente.')
    return redirect('gestiones:home')

@login_required
def actualizar_imagen_perfil(request):
    if request.method == 'POST':
        form = ImagenPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def eliminar_imagen_perfil(request):
    user = request.user
    user.imagen_perfil.delete()  # Eliminar la imagen de perfil
    user.save()
    messages.success(request, 'Imagen de perfil eliminada correctamente.')
    return JsonResponse({'success': True})



from django.contrib.auth.views import PasswordChangeView
from django.http import JsonResponse
from django.template.loader import render_to_string

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'

    def form_invalid(self, form):
        if self.request.is_ajax():
            html = render_to_string(self.template_name, {'form': form}, request=self.request)
            return JsonResponse({'html': html}, status=400)
        else:
            return super().form_invalid(form)

    def form_valid(self, form):
        if self.request.is_ajax():
            form.save()
            return JsonResponse({'message': 'Contraseña cambiada con éxito.'})
        else:
            return super().form_valid(form)
