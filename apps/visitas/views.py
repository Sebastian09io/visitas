from django.shortcuts import render, redirect, get_object_or_404
from apps.funcionarios.models import Visita
from .forms import VisitForm
from django.contrib import messages
from django.forms.models import model_to_dict

def home_visita(request):
    user = request.user
    if request.method == 'POST':
        form = VisitForm(request.POST, instance=user)
        if form.is_valid():
            original_data = model_to_dict(user)
            form_data = form.cleaned_data
            changes = {key: form_data[key] for key in form_data if form_data[key] != original_data.get(key)}

            if changes:
                form.save()
                messages.success(request, 'Visita asignada.')
            else:
                messages.info(request, 'No se han realizado cambios.')

            grabacion_estado = request.POST.get('grabacion') == 'True'
            if user.id_visita:
                grabacion = get_object_or_404(Visita, id=user.id_visita.id)
                grabacion.grabacion = grabacion_estado
                grabacion.save()

            return redirect('visitas:home_visita')

    else:
        form = VisitForm(instance=user)

    # Obtener el valor de id_area del formulario
    id_area_value = form['id_area'].value()

    context = {
        'user': user,
        'form': form,
        'id_area_value': id_area_value,  # Añadir el valor al contexto
    }
    return render(request, 'visita.html', context)

import json
from django.http import HttpResponse
from apps.funcionarios.models import Visita, Persona, Asistente, VisitaAsistente

def guardar_visita(request):
    if request.method == 'POST':
        form = VisitForm(request.POST)
        if form.is_valid():
            # Guardar la visita
            visita = form.save()

            # Procesar los asistentes
            asistentes_data = request.POST.get('asistentes')
            if asistentes_data:
                asistentes = json.loads(asistentes_data)
                for asistente_data in asistentes:
                    asistente, created = Asistente.objects.get_or_create(
                        nombre=asistente_data['nombres'],
                        correo=asistente_data['correo'],
                        defaults={
                            'telefono': asistente_data['telefono'],
                            'id_tipo_documento': asistente_data['idTipoDocumento'],
                            'identificacion': asistente_data['identificacion']
                        }
                    )
                    VisitaAsistente.objects.create(visita=visita, asistente=asistente)

            return redirect('nombre_de_la_vista_a_donde_redirigir')  # Cambia esto al nombre de la vista a la que deseas redirigir
    else:
        form = VisitForm()

    return render(request, 'nombre_del_template.html', {'form': form})
