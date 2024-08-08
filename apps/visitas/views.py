import os
import json
from django.http import FileResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from apps.funcionarios.models import Persona, Visita, Asistente, VisitaAsistente, TipoDocumento,Genero
from .forms import PersonaForm, VisitaFormulario

def home_visita(request):
    user = request.user
    
    # Instanciar objetos
    try:
        persona = Persona.objects.get(id=user.id)
    except Persona.DoesNotExist:
        persona = Persona(user=user)

    if request.method == 'POST':
        persona_form = PersonaForm(request.POST, instance=persona)
        visita_form = VisitaFormulario(request.POST)
        
        if persona_form.is_valid() and visita_form.is_valid():
            persona = persona_form.save(commit=False)
            visita = visita_form.save(commit=False)  # Guardar de forma diferida para actualizar el campo grabacion
            
            # Procesar el estado de grabación
            grabacion_estado = request.POST.get('grabacion') == 'True'
            visita.grabacion = grabacion_estado

            # Asignar la persona a la visita
            visita.id_persona = persona
            
            # Guardar visita y persona
            visita.save()
            persona.save()
            
            #envio de correo 
            user_email = request.user.correo
            subject = 'Solicitud de Reserva en Revisión'
            message = 'Tu solicitud de reserva de visita está en revisión.'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
            
            # Procesar los asistentes
            asistentes_data = request.POST.get('asistentes')
            if asistentes_data:
                asistentes = json.loads(asistentes_data)
                for asistente_data in asistentes:
                    id_tipo_documento = int(asistente_data.get('idTipoDocumento'))
                    genero_asistente = int(asistente_data.get('genero_a'))

                    asistente, created = Asistente.objects.get_or_create(
                        identificacion_asistente=asistente_data['identificacion'],
                        defaults={
                            'nombre_asistente': asistente_data['nombres'],
                            'apellidos_asistente': asistente_data['apellidos'],
                            'telefono_asistente': asistente_data['telefono'],
                            'correo_asistente': asistente_data['correo'],
                            'id_tipo_documento_asistente': TipoDocumento.objects.get(id=id_tipo_documento),
                            'discapacidad_asistente': asistente_data['discapacidad_a'],
                            'procedencia_asistente': asistente_data['procedencia_a'],
                            'id_genero_asistente': Genero.objects.get(id=genero_asistente)
                        }
                    )

                    # Relacionar el asistente con la visita
                    VisitaAsistente.objects.get_or_create(visita=visita, asistente=asistente)

            messages.success(request, 'Visita y asistentes registrados, Se envió un correo con la informacion del estado de revisión se la visita.')
            return redirect('visitas:home_visita')
        else:
            messages.error(request, 'Formulario inválido. Por favor revise los datos ingresados.')
    else:
        persona_form = PersonaForm(instance=persona)
        visita_form = VisitaFormulario()

    context = {
        'user': user,
        'persona_form': persona_form,
        'visita_form': visita_form,
    }
    return render(request, 'visita.html', context)



def descargar_excel(request):
    file_path = os.path.join('static', 'files', 'Registro Asistentes.xlsx')
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename="Registro Asistentes.xlsx"'
    return response




def administrador_visitas(request):
    user = request.user
    try:
        persona = Persona.objects.get(id=user.id)
    except Persona.DoesNotExist:
        persona = Persona(user=user)
    
    # Obtener todas las visitas y la persona asociada
    visitas = Visita.objects.prefetch_related('visita_asistente').select_related('id_persona').all().order_by('id')

    # Paginación de las visitas
    paginator = Paginator(visitas, 5)  # Número de visitas por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)
    
    persona_form = PersonaForm(instance=persona)
    visita_form = VisitaFormulario()

    context = {
        'persona': persona,
        'user': user,
        'resultados': resultados,
        'persona_form': persona_form,
        'visita_form': visita_form,
    }
    return render(request, 'administracion/admin_visita.html', context)






def buscar_visita(request):
    """
    Función para la gestión de búsqueda de visitas.
    """
    # Recuperar la consulta de búsqueda y el filtro de estado del parámetro GET
    query = request.GET.get('buscar', '')
    estado = request.GET.get('estado', 'todos')

    # Inicializar resultados como una lista de todas las visitas
    resultados = Visita.objects.all()

    if query:
        # Filtrar resultados por coincidencias en varios campos de texto de Persona
        personas = Persona.objects.filter(
            Q(identificacion__icontains=query) |
            Q(nombres__icontains=query) |  
            Q(apellidos__icontains=query)
        )
        # Filtrar visitas basadas en las personas encontradas
        resultados = resultados.filter(id_persona__in=personas)



    # Aplicar filtro de estado de la visita
    if estado == 'habilitados':
        resultados = resultados.filter(estado_revision=True)
    elif estado == 'inhabilitados':
        resultados = resultados.filter(estado_revision=False)
    elif estado == 'finalizado':
        resultados = resultados.filter(estado_finalizado=True)
    

    # Ordenar los resultados antes de paginar
    resultados = resultados.order_by('id')

    # Paginador
    paginator = Paginator(resultados, 5)  # Número de visitas por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)

    context = {
        'resultados': resultados,
        'query': query,
        'estado': estado,
    }

    return render(request, 'administracion/admin_visita.html', context)


def rechazar_visita(request, visita_id):
    if request.method == 'POST':
        visita = get_object_or_404(Visita, id=visita_id)
        visita.estado_rechazado = True
        try:
            visita.save()
            user_email = request.user.correo
            
            if user_email: 
                subject = 'Estado de solicitud de reserva'
                message = 'Tu solicitud de reserva de visita ha sido rechazada.'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def aprobar_visita(request, visita_id):
    if request.method == 'POST':
        visita = get_object_or_404(Visita, id=visita_id)
        visita.estado_revision = True
        try:
            visita.save()
            user_email = request.user.correo
            
            if user_email: 
                subject = 'Estado de solicitud de reserva'
                message = 'Tu solicitud de reserva de visita ha sido aprobada.'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})