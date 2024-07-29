import os
import json
from django.http import FileResponse
from django.core.paginator import Paginator
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from apps.funcionarios.models import Persona, Visita, Asistente, VisitaAsistente, TipoDocumento,Genero
from .forms import PersonaForm, VisitaFormulario

def home_visita(request):
    user = request.user
    
    # Instanciar objetos
    try:
        persona = Persona.objects.get(id=user.id)
        visita = persona.id_visita
    except Persona.DoesNotExist:
        persona = Persona(user=user)
        visita = Visita()
    
    if request.method == 'POST':
        persona_form = PersonaForm(request.POST, instance=persona)
        visita_form = VisitaFormulario(request.POST, instance=visita)
        
        if persona_form.is_valid() and visita_form.is_valid():
            persona = persona_form.save(commit=False)
            visita = visita_form.save(commit=False)  # Guardar de forma diferida para actualizar el campo grabacion
            
            # Procesar el estado de grabación
            grabacion_estado = request.POST.get('grabacion') == 'True'
            visita.grabacion = grabacion_estado

            # Guardar visita
            visita.save()
            persona.id_visita = visita
            persona.save()
            
            # Procesar los asistentes
            asistentes_data = request.POST.get('asistentes')
            if asistentes_data:
                asistentes = json.loads(asistentes_data)
                for asistente_data in asistentes:
                    # Pasar str a int
                    id_tipo_documento_str = asistente_data.get('idTipoDocumento')
                    id_tipo_documento = int(id_tipo_documento_str)
                    
                    genero_a_str = asistente_data.get('genero_a')
                    genero_asistente = int(genero_a_str)

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

                    VisitaAsistente.objects.get_or_create(visita=visita, asistente=asistente)

            messages.success(request, 'Visita asignada y asistentes registrados.')
            return redirect('visitas:home_visita')
        else:
            messages.error(request, 'Formulario inválido. Por favor revise los datos ingresados.')
    else:
        persona_form = PersonaForm(instance=persona)
        visita_form = VisitaFormulario(instance=visita)
        id_area_value = persona_form['id_area'].value() if persona_form['id_area'].value() else None

    context = {
        'user': user,
        'persona_form': persona_form,
        'visita_form': visita_form,
        'id_area_value': id_area_value, 
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
        visita = persona.id_visita
    except Persona.DoesNotExist:
        persona = Persona(user=user)
        visita = Visita()
        
    if request.method == 'POST':
        pass

    personas = Persona.objects.all().order_by('id')  # Ordenar los resultados por 'id'
    paginator = Paginator(personas, 6)  # Número de usuarios por página
    page_number = request.GET.get('page')
    resultados = paginator.get_page(page_number)
    
    context = {
        'user': user,
        'resultados': resultados,
        }
    return render(request, 'administracion/admin_visita.html', context)