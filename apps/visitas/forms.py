from django import forms
from apps.funcionarios.models import ConfiguracionVisita, Persona, Area, Ambiente, Linea, Genero, Visita, TipoDocumento, Asistente 
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

class BootstrapFormMixin:
    def _init_bootstrap(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.widgets.TextInput, forms.widgets.Select,
                                   forms.widgets.EmailInput, forms.widgets.PasswordInput,
                                   forms.widgets.FileInput, forms.widgets.DateInput,
                                   forms.widgets.DateTimeInput, forms.widgets.TimeInput)):
                classes = widget.attrs.get('class', '')
                widget.attrs.update({'class': f'{classes} form-control'.strip()})

                # Estilos específicos para los campos de ConfiguracionVisitaForm
        if 'dia_semana' in self.fields:
            self.fields['dia_semana'].widget.attrs.update({'class': 'form-control', 'style': 'width: 100%;'})
        if 'hora_inicio' in self.fields:
            self.fields['hora_inicio'].widget.attrs.update({'class': 'form-control', 'style': 'width: 100%;'})
        if 'hora_finalizacion' in self.fields:
            self.fields['hora_finalizacion'].widget.attrs.update({'class': 'form-control', 'style': 'width: 100%;'})
            # clases
        if 'fecha_inicio' in self.fields:
            self.fields['fecha_inicio'].widget.attrs.update({'class': 'datetime-picker form-control'})
        if 'fecha_finalizacion' in self.fields:
            self.fields['fecha_finalizacion'].widget.attrs.update({'class': 'datetime-picker form-control'})

        if 'grabacion' in self.fields:
            self.fields['grabacion'].widget.attrs.update({'class': 'd-none'})




class PersonaForm(forms.ModelForm, BootstrapFormMixin):
    id_tipo_documento_asistente = forms.ModelChoiceField(queryset=TipoDocumento.objects.all(), label="Tipo de Documento del Asistente", empty_label="Seleccione el tipo de documento",required=False)
    nombre_asistente = forms.CharField(max_length=50, label="Nombre del Asistente",required=False)
    apellidos_asistente = forms.CharField(max_length=50, label="Apellidos del Asistente",required=False)
    telefono_asistente = forms.CharField(max_length=10, label="Teléfono del Asistente",required=False)
    correo_asistente = forms.EmailField(label="Correo del Asistente",required=False)
    identificacion_asistente = forms.CharField(max_length=10, label="Identificación del Asistente",required=False)

    
    discapacidad_asistente = forms.CharField(max_length=50,required=False)
    procedencia_asistente = forms.CharField(max_length=50,required=False)
    id_genero_asistente = forms.ModelChoiceField(queryset=Genero.objects.all(), empty_label="Seleccione el género",required=False)


    class Meta:
        model = Persona
        fields = ['id_genero', 'id_tipo_documento_asistente', 'nombre_asistente', 'apellidos_asistente', 'telefono_asistente', 'correo_asistente', 'identificacion_asistente', 'identificacion', 'nombres', 'apellidos', 'telefono', 'correo','id_tipo_documento']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_tipo_documento'].queryset = TipoDocumento.objects.all()
        self.fields['id_tipo_documento'].empty_label = "Seleccione un tipo de documento"
        self.fields['id_genero'].queryset = Genero.objects.all()
        self.fields['id_genero'].empty_label = "Seleccione el género"
        self.fields['procedencia_asistente'].widget.attrs.update({'placeholder': 'Ingrese la procedencia'})
        self.fields['discapacidad_asistente'].widget.attrs.update({'placeholder': 'Ingrese la discapacidad'})
        self.fields['nombre_asistente'].widget.attrs.update({'placeholder': 'Ingrese el nombre'})
        self.fields['apellidos_asistente'].widget.attrs.update({'placeholder': 'Ingrese el apellido'})
        self.fields['correo_asistente'].widget.attrs.update({'placeholder': 'Ingrese el correo'})
        self.fields['telefono_asistente'].widget.attrs.update({'placeholder': 'Ingrese el numero telefonico'})
        self.fields['identificacion_asistente'].widget.attrs.update({'placeholder': 'Ingrese la identificacion'})
        self._init_bootstrap()


    def save(self, commit=True):
        persona = super().save(commit=False)
        
        # Actualizar o crear el Asistente con los campos adicionales
        asistente, created = Asistente.objects.update_or_create(
            identificacion_asistente=self.cleaned_data['identificacion_asistente'],
            defaults={
                'nombre_asistente': self.cleaned_data['nombre_asistente'],
                'apellidos_asistente': self.cleaned_data['apellidos_asistente'],
                'telefono_asistente': self.cleaned_data['telefono_asistente'],
                'correo_asistente': self.cleaned_data['correo_asistente'],
                'id_tipo_documento_asistente': self.cleaned_data['id_tipo_documento_asistente'],
                'discapacidad_asistente': self.cleaned_data['discapacidad_asistente'],
                'procedencia_asistente': self.cleaned_data['procedencia_asistente'],
                'id_genero_asistente': self.cleaned_data['id_genero_asistente'],
                
            }
        )

        persona.id_tipo_documento_asistente = asistente
        if commit:
            persona.save()

        return persona





class VisitaFormulario(forms.ModelForm, BootstrapFormMixin):
    discapacidad = forms.CharField(max_length=50, label="Discapacidad")
    procedencia = forms.CharField(max_length=80, label="Procedencia")
    fecha_inicio = forms.DateTimeField(label="Fecha de inicio", widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    fecha_finalizacion = forms.DateTimeField(label="Fecha de finalización", widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    grabacion = forms.BooleanField(required=False, initial=False)
    id_linea = forms.ModelMultipleChoiceField(
        queryset=Linea.objects.all(),
        label="Línea",
        widget=forms.CheckboxSelectMultiple,
        required=False)
    
    id_ambiente = forms.ModelMultipleChoiceField(
        queryset=Ambiente.objects.all(),
        label="Ambiente",
        widget=forms.CheckboxSelectMultiple,
        required=False)
    
    id_area = forms.ModelMultipleChoiceField(        
        queryset=Area.objects.all(),
        label="Estrategia",
        widget=forms.CheckboxSelectMultiple,
        required=False)

    class Meta:
        model = Visita
        fields = ['fecha_inicio', 'fecha_finalizacion', 'discapacidad', 'procedencia', 'grabacion', 'id_linea', 'id_ambiente', 'id_area']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['procedencia'].widget.attrs.update({'placeholder': 'Ingrese su procedencia'})
        self.fields['discapacidad'].widget.attrs.update({'placeholder': 'Ingrese su discapacidad'})
        self.fields['id_linea'].queryset = Linea.objects.all()
        self.fields['id_linea'].empty_label = None
        self.fields['id_ambiente'].queryset = Ambiente.objects.all()
        self.fields['id_ambiente'].empty_label = None
        self.fields['id_area'].queryset = Area.objects.all()
        self.fields['id_area'].empty_label = None
        self._init_bootstrap()

def clean(self):
    cleaned_data = super().clean()
    fecha_inicio = cleaned_data.get("fecha_inicio")
    fecha_finalizacion = cleaned_data.get("fecha_finalizacion")

    now = timezone.now()
    local_now = timezone.localtime(now)

    if fecha_inicio and fecha_inicio < local_now:
        raise forms.ValidationError("No se puede agendar para una fecha anterior a hoy.")

    if fecha_finalizacion and fecha_finalizacion < local_now:
        raise forms.ValidationError("No se puede agendar para una fecha anterior a hoy.")

    if fecha_inicio and fecha_finalizacion:
        if fecha_inicio.date() != fecha_finalizacion.date():
            raise forms.ValidationError("La fecha de inicio y finalización deben ser el mismo día.")

        # Consultar configuraciones
        configuraciones = ConfiguracionVisita.objects.filter(dia_semana=fecha_inicio.weekday())
        if not configuraciones.exists():
            raise forms.ValidationError("No hay configuraciones para el día seleccionado.")
        


        # Validar que no existan 2 visitas a la vez
        existing_visits = Visita.objects.filter(
            fecha_inicio__lt=fecha_finalizacion,
            fecha_finalizacion__gt=fecha_inicio
        )

        if existing_visits.exists():
            raise forms.ValidationError("Ya hay una visita agendada en este intervalo de tiempo.")

    return cleaned_data




class ConfiguracionVisitaForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = ConfiguracionVisita
        fields = ['dia_semana', 'hora_inicio', 'hora_finalizacion']
        widgets = {
            'hora_inicio': forms.TimeInput(format='%H:%M', attrs={
                'type': 'time',
                'min': '08:00',
                'max': '18:00'
            }),
            'hora_finalizacion': forms.TimeInput(format='%H:%M', attrs={
                'type': 'time',
                'min': '08:00',
                'max': '18:00'
            }),
            'dia_semana': forms.Select(choices=[(None, 'Seleccione un día')] + ConfiguracionVisita.DIA_SEMANA_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap()



    def clean_hora_inicio(self):
        hora_inicio = self.cleaned_data['hora_inicio']
        if hora_inicio < datetime.time(8, 0) or hora_inicio > datetime.time(18, 0):
            raise ValidationError('La hora de inicio debe estar entre 08:00 y 18:00.')
        return hora_inicio

    def clean_hora_finalizacion(self):
        hora_finalizacion = self.cleaned_data['hora_finalizacion']
        if hora_finalizacion < datetime.time(8, 0) or hora_finalizacion > datetime.time(18, 0):
            raise ValidationError('La hora de finalización debe estar entre 08:00 y 18:00.')
        return hora_finalizacion

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_finalizacion = cleaned_data.get('hora_finalizacion')

        if hora_inicio and hora_finalizacion and hora_finalizacion <= hora_inicio:
            raise ValidationError('La hora de finalización debe ser después de la hora de inicio.')

        return cleaned_data







