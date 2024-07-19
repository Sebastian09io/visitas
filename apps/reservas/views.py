from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from apps.funcionarios.models import Persona, Implemento, Espacio, TipoDocumento
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import PerfilForm, ImagenPerfilForm
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.http import JsonResponse
from rest_framework import viewsets
from apps.reservas.models import Reserva
from apps.reservas.forms import ReservaForm
from django.core.mail import send_mail
from apps.reservas.serializers import ReservaSerializer

# Reservas

def gestion_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.save()
            enviar_correo_confirmacion(reserva)
            return JsonResponse({'success': True})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'error': errors})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def enviar_correo_confirmacion(reserva):
    subject = 'Confirmación de reserva'
    message = f"Tu reserva para el espacio {reserva.espacio.nombre} ha sido confirmada.\n\nDetalles de la reserva:\nMotivo: {reserva.motivo}\nFecha y hora de inicio: {reserva.fecha_inicio}\nFecha y hora de fin: {reserva.fecha_fin}"
    from_email = 'noreply@miapp.com'
    recipient_list = [reserva.usuario.email]
    send_mail(subject, message, from_email, recipient_list)

class ReservaViewSet(viewsets.ModelViewSet): # Clase que permite hacer CRUD usando Django REST
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    
def administracion_reservas (request):
        return render(request, 'administracion/gestion_reserva.html')


def gestion_implemento(request):
    if request.method == 'POST':
        implemento_id = request.POST.get('implemento_id')
        if implemento_id:
            implemento = get_object_or_404(Implemento, id=implemento_id)
            implemento.estado = not implemento.estado
            implemento.save()
            return redirect('reservas:gestion_implemento')  # Redirige para actualizar la página

    implementos = Implemento.objects.all().order_by('id')  # Ordenar los resultados por 'id'
    paginator = Paginator(implementos, 6)  # Número de usuarios por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)

    context = {
        'resultados': resultados,
    }
    return render(request, 'administracion/gestion_implemento.html', context)

def registrar_implemento(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:  # Validación simple
            Implemento.objects.create(nombre=nombre)
            return redirect('reservas:gestion_implemento')  # Redirecciona después de crear el objeto

    implementos = Implemento.objects.all()
    return render(request, 'administracion/gestion_implemento.html', {'implementos': implementos})

def eliminar_implemento(request, implemento_id):
    implemento = get_object_or_404(Implemento, id=implemento_id)
    implemento.delete()
    return redirect('reservas:gestion_implemento')

def buscar_implemento(request):
    """
    Función para la gestión de búsqueda de implementos.
    """
    # Recuperar la consulta de búsqueda y el filtro de estado del parámetro GET
    query = request.GET.get('buscar', '')
    estado = request.GET.get('estado', 'todos')

    # Inicializar resultados como una lista vacía
    resultados = Implemento.objects.all()

    if query:
        # Filtrar resultados por coincidencias en varios campos de texto
        resultados = Implemento.objects.filter(
            Q(nombre__icontains=query) 
        )

    # Aplicar filtro de estado
    if estado == 'habilitados':
        resultados = resultados.filter(estado=True)
    elif estado == 'inhabilitados':
        resultados = resultados.filter(estado=False)

    # Ordenar los resultados antes de paginar
    resultados = resultados.order_by('id')
    # Paginador
    paginator = Paginator(resultados, 6)  # Número de usuarios por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)

    context = {'resultados': resultados, 'query': query, 'estado': estado}

    return render(request, 'administracion/gestion_implemento.html', context)

def gestion_funcionario(request):
    if request.method == 'POST':
        persona_id = request.POST.get('persona_id')
        if persona_id:
            persona = get_object_or_404(Persona, id=persona_id)
            persona.estado = not persona.estado
            persona.save()
            return redirect('reservas:gestion_funcionario')  # Redirige para actualizar la página

    personas = Persona.objects.all().order_by('id')  # Ordenar los resultados por 'id'
    paginator = Paginator(personas, 6)  # Número de usuarios por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)

    context = {
        'resultados': resultados,
    }
    return render(request, 'administracion/gestion_funcionario.html', context)

def buscar_funcionario(request):
    """
    Función para la gestión de búsqueda de funcionarios.
    """
    # Recuperar la consulta de búsqueda y el filtro de estado del parámetro GET
    query = request.GET.get('buscar', '')
    estado = request.GET.get('estado', 'todos')

    # Inicializar resultados como una lista vacía
    resultados = Persona.objects.all()

    if query:
        # Filtrar resultados por coincidencias en varios campos de texto
        resultados = Persona.objects.filter(
            Q(identificacion__icontains=query) 
#            Q(id_cargo__nombre__icontains=query) |  
#            Q(id_dependencia__nombre__icontains=query)
        )

    # Aplicar filtro de estado
    if estado == 'habilitados':
        resultados = resultados.filter(estado=True)
    elif estado == 'inhabilitados':
        resultados = resultados.filter(estado=False)

    # Ordenar los resultados antes de paginar
    resultados = resultados.order_by('id')
    # Paginador
    paginator = Paginator(resultados, 6)  # Número de usuarios por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)

    context = {'resultados': resultados, 'query': query, 'estado': estado}

    return render(request, 'administracion/gestion_funcionario.html', context)

#espacios
def gestion_espacio(request):
    if request.method == 'POST':
        espacio_id = request.POST.get('espacio_id')
        if espacio_id:
            espacio = get_object_or_404(Espacio, id=espacio_id)
            espacio.estado = not espacio.estado
            espacio.save()
            return redirect('reservas:gestion_espacio')  # Redirige para actualizar la página

    espacios = Espacio.objects.all().order_by('id')  # Ordenar los resultados por 'id'
    paginator = Paginator(espacios, 6)  # Número de usuarios por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)

    context = {
        'resultados': resultados,
    }
    return render(request, 'administracion/gestion_espacio.html', context)

def registrar_espacio(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:  # Validación simple
            Espacio.objects.create(nombre=nombre)
            return redirect('reservas:gestion_espacio')  # Redirecciona después de crear el objeto

    espacios = Espacio.objects.all()
    return render(request, 'administracion/gestion_espacio.html', {'espacios': espacios})

def eliminar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)
    espacio.delete()
    return redirect('reservas:gestion_espacio')

def buscar_espacio(request):
    """
    Función para la gestión de búsqueda de espacios.
    """
    # Recuperar la consulta de búsqueda y el filtro de estado del parámetro GET
    query = request.GET.get('buscar', '')
    estado = request.GET.get('estado', 'todos')

    # Inicializar resultados como una lista vacía
    resultados = Espacio.objects.all()

    if query:
        # Filtrar resultados por coincidencias en varios campos de texto
        resultados = Espacio.objects.filter(
            Q(nombre__icontains=query) 
        )

    # Aplicar filtro de estado
    if estado == 'habilitados':
        resultados = resultados.filter(estado=True)
    elif estado == 'inhabilitados':
        resultados = resultados.filter(estado=False)

    # Ordenar los resultados antes de paginar
    resultados = resultados.order_by('id')
    # Paginador
    paginator = Paginator(resultados, 6)  # Número de usuarios por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)

    context = {'resultados': resultados, 'query': query, 'estado': estado}

    return render(request, 'administracion/gestion_espacio.html', context)



def registro_temporal(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:  # Validación simple
            TipoDocumento.objects.create(nombre=nombre)
            return redirect('gestiones:login')  # Redirecciona después de crear el objeto

    documentos = TipoDocumento.objects.all()
    return render(request, 'administracion/registro_temporal.html', {'documentos': documentos})





#gestion_perfil
@login_required
def gestion_perfil(request):
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
    else:
        form = PerfilForm(instance=user)

    nombre_completo = f"{user.nombres} {user.apellidos}"
    context = {
        'form': form,
        'nombre_completo': nombre_completo
    }

    return render(request, 'administracion/perfil_admin.html', context)

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

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('reservas:gestion_perfil')

    def form_valid(self, form):
        if self.request.is_ajax():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': str(self.success_url)}, status=200)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        return super().form_invalid(form)