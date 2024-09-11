import os
import json
from django.http import FileResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.conf import settings
from apps.funcionarios.models import ConfiguracionVisita, Persona, Visita, Asistente, VisitaAsistente, TipoDocumento,Genero
from .forms import ConfiguracionVisitaForm, PersonaForm, VisitaFormulario

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
            
            # Asignar area o estrategia a visita
            area_seleccionada = visita_form.cleaned_data.get('id_area')
            visita.id_area = area_seleccionada
            # Asignar las líneas seleccionadas a la visita
            lineas_seleccionadas = visita_form.cleaned_data.get('id_linea')
            visita.id_linea.set(lineas_seleccionadas)
            
            # Asignar ambientes seleccionados a la visita
            ambientes_seleccionados = visita_form.cleaned_data.get('id_ambiente')
            visita.id_ambiente.set(ambientes_seleccionados)
            
            #envio de correo 
            subject = 'Estado solicitud de Reserva'
            context = {
                'nombres': persona.nombres,
                'apellidos': persona.apellidos,
                'fecha_inicio': visita.fecha_inicio,
                'fecha_finalizacion': visita.fecha_finalizacion,
                'area': area_seleccionada.nombre,
                'procedencia': visita.procedencia,
                'texto': 'Su solicitud de reserva de visita está en revisión.',
                'correo': persona.correo,
                'imagen_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHfPSiMXl0hYquJSWZk7pGVu5y4nsz-QiiFA&s' 
            }
            html_content = render_to_string('email_template.html', context)
            text_content = strip_tags(html_content)

            # Enviar correo  HTML
            email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.correo])
            email.attach_alternative(html_content, "text/html")
            email.send()
            
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

def configuracion_visitas(request):
    configuraciones = ConfiguracionVisita.objects.all()
    data = [
        {
            'dia_semana': config.dia_semana, 
            'hora_inicio': config.hora_inicio.strftime('%H:%M'),
            'hora_finalizacion': config.hora_finalizacion.strftime('%H:%M')
        } 
        for config in configuraciones
    ]
    return JsonResponse(data, safe=False)



def descargar_excel(request):
    file_path = os.path.join('static', 'files', 'Registro Asistentes.xlsx')
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename="Registro Asistentes.xlsx"'
    return response

def actualizar_estado_visitas():
    now = timezone.now()
    visitas = Visita.objects.filter(fecha_finalizacion__lt=now, estado_finalizado=False)

    for visita in visitas:
        visita.estado_finalizado = True
        visita.save()
        
import pytz # type: ignore
from datetime import datetime

def verificar_fecha(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_finalizacion = request.GET.get('fecha_finalizacion')

    if fecha_inicio and fecha_finalizacion:
        try:
            # Convertir las cadenas de fecha en objetos datetime en UTC
            fecha_inicio_datetime = datetime.fromisoformat(fecha_inicio).astimezone(pytz.utc)
            fecha_finalizacion_datetime = datetime.fromisoformat(fecha_finalizacion).astimezone(pytz.utc)
        except ValueError:
            return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)


        # 1. Comprobar si ya hay una visita agendada en esas fechas y horas
        existe_visita = Visita.objects.filter(
            fecha_inicio__lt=fecha_finalizacion_datetime,
            fecha_finalizacion__gt=fecha_inicio_datetime
        ).exists()


        # Retornar el resultado de la comparación de visitas y reservas
        return JsonResponse({'reservada': existe_visita})

    return JsonResponse({'reservada': False})

#funciones administracion

def administrador_visitas(request):
    user = request.user
    try:
        persona = Persona.objects.get(id=user.id)
    except Persona.DoesNotExist:
        persona = Persona(
            nombres=user.nombres,
            apellidos=user.apellidos,
            telefono=user.telefono,
            correo=user.correo,
        )
        
    actualizar_estado_visitas()
    
    # Obtener todas las visitas y la persona asociada
    visitas = Visita.objects.prefetch_related('visita_asistente').select_related('id_persona').all().order_by('id')

    # Paginación de las visitas
    paginator = Paginator(visitas, 5)  # Número de visitas por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)
    
    persona_form = PersonaForm(instance=persona)
    visita_form = VisitaFormulario()
    
    # Manejo de la configuración de visitas
    if request.method == 'POST':
        config_form = ConfiguracionVisitaForm(request.POST)
        if config_form.is_valid():
            config_form.save()
            return redirect('visitas:administrador_visitas')
    else:
        config_form = ConfiguracionVisitaForm()

    configuraciones = ConfiguracionVisita.objects.all()

    context = {
        'persona': persona,
        'user': user,
        'resultados': resultados,
        'persona_form': persona_form,
        'visita_form': visita_form,
        'config_form': config_form,
        'configuraciones': configuraciones,
    }
    return render(request, 'administracion/admin_visita.html', context)


def cargar_asistentes(request, visita_id):
    visita = get_object_or_404(Visita, id=visita_id)
    asistentes = visita.visita_asistente.all()  # Obtén los asistentes relacionados con la visita
    
    # Obtener los IDs de tipo de documento y género
    asistentes_data = []
    for asistente in asistentes:
        asistentes_data.append({
            'id': asistente.id,
            'nombre_asistente': asistente.nombre_asistente,
            'apellidos_asistente': asistente.apellidos_asistente,
            'telefono_asistente': asistente.telefono_asistente,
            'correo_asistente': asistente.correo_asistente,
            'identificacion_asistente': asistente.identificacion_asistente,
            'discapacidad_asistente': asistente.discapacidad_asistente,
            'procedencia_asistente': asistente.procedencia_asistente,
            'id_tipo_documento_asistente_nombre': asistente.id_tipo_documento_asistente.nombre if asistente.id_tipo_documento_asistente else 'N/A',
            'id_genero_asistente_nombre': asistente.id_genero_asistente.nombre if asistente.id_genero_asistente else 'N/A',
        })
    
    # Devolver la información de los asistentes como JSON
    return JsonResponse({'asistentes': asistentes_data})


def eliminar_horario(request, horario_id):
    hora = get_object_or_404(ConfiguracionVisita, id=horario_id)
    hora.delete()
    return redirect('visitas:administrador_visitas')




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
    elif estado == 'rechazado':
        resultados = resultados.filter(estado_rechazado=True)
    

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
    user = request.user
    try:
        persona = Persona.objects.get(id=user.id)
    except Persona.DoesNotExist:
        persona = Persona(user=user)
    
    if request.method == 'POST':
        visita = get_object_or_404(Visita, id=visita_id)
        visita.estado_rechazado = True
        
        try:
            visita.save()
            
            # Obtener el área seleccionada desde la instancia de la visita
            area_seleccionada = visita.id_area

            # Contexto para el correo electrónico
            context = {
                'nombres': persona.nombres,
                'apellidos': persona.apellidos,
                'fecha_inicio': visita.fecha_inicio,
                'fecha_finalizacion': visita.fecha_finalizacion,
                'area': area_seleccionada.nombre,
                'procedencia': visita.procedencia,
                'texto': 'Su solicitud de reserva de visita ha sido rechazada.',
                'correo': persona.correo,
                'imagen_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHfPSiMXl0hYquJSWZk7pGVu5y4nsz-QiiFA&s' 
            }
            
            # Renderizar el contenido HTML del correo
            html_content = render_to_string('email_template.html', context)
            text_content = strip_tags(html_content)

            # Enviar correo HTML
            email = EmailMultiAlternatives(
                subject='Estado solicitud de Reserva',
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.correo]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})



def aprobar_visita(request, visita_id):
    user = request.user
    try:
        persona = Persona.objects.get(id=user.id)
    except Persona.DoesNotExist:
        persona = Persona(user=user)
    if request.method == 'POST':
        visita = get_object_or_404(Visita, id=visita_id)
        visita.estado_revision = True
        try:
            visita.save()
            user_email = request.user.correo
            
            # Obtener el área seleccionada desde la instancia de la visita
            area_seleccionada = visita.id_area

            # Contexto para el correo electrónico
            context = {
                'nombres': persona.nombres,
                'apellidos': persona.apellidos,
                'fecha_inicio': visita.fecha_inicio,
                'fecha_finalizacion': visita.fecha_finalizacion,
                'area': area_seleccionada.nombre,
                'procedencia': visita.procedencia,
                'texto': 'Su solicitud de reserva de visita ha sido aprobada.',
                'correo': persona.correo,
                'imagen_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHfPSiMXl0hYquJSWZk7pGVu5y4nsz-QiiFA&s' 
            }
            
            # Renderizar el contenido HTML del correo
            html_content = render_to_string('email_template.html', context)
            text_content = strip_tags(html_content)

            # Enviar correo HTML
            email = EmailMultiAlternatives(
                subject='Estado solicitud de Reserva',
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.correo]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

