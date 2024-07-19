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
