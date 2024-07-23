import json
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.funcionarios.models import Visita, Asistente, VisitaAsistente
from .forms import VisitForm

def home_visita(request):
    user = request.user
    if request.method == 'POST':
        form = VisitForm(request.POST)

        if form.is_valid():
            # Guarda la visita primero
            visita = form.save()

            # Procesar la grabación
            grabacion_estado = request.POST.get('grabacion') == 'True'
            visita.grabacion = grabacion_estado
            visita.save()

            # Procesar los asistentes
            asistentes_data = request.POST.get('asistentes')
            
            if asistentes_data:
                asistentes = json.loads(asistentes_data)
                for asistente_data in asistentes:
                    asistente, created = Asistente.objects.get_or_create(
                        identificacion_asistente=asistente_data['identificacion'],
                        defaults={
                            'nombre_asistente': asistente_data['nombres'],
                            'apellidos_asistente': asistente_data['apellidos'],
                            'telefono_asistente': asistente_data['telefono'],
                            'correo_asistente': asistente_data['correo'],
                            'id_tipo_documento_asistente': asistente_data['idTipoDocumento']
                        }
                    )
                    VisitaAsistente.objects.get_or_create(visita=visita, asistente=asistente)

            messages.success(request, 'Visita asignada y asistentes registrados.')
            return redirect('visitas:home_visita')

        else:
            messages.error(request, 'Formulario inválido. Por favor revise los datos ingresados.')
    else:
        form = VisitForm()
            # Obtener el valor de id_area del formulario
    id_area_value = form['id_area'].value()
    context = {
        'user': user,
        'form': form,
        'id_area_value': id_area_value,  # Añadir el valor al contexto
    }
    return render(request, 'visita.html', context)
