from django import forms
from apps.funcionarios.models import Persona, Area, Ambiente, Linea, Genero, Visita, TipoDocumento, Asistente 
from django.core.exceptions import ValidationError
import datetime

class BootstrapFormMixin:
    def _init_bootstrap(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.widgets.TextInput, forms.widgets.Select,
                                   forms.widgets.EmailInput, forms.widgets.PasswordInput,
                                   forms.widgets.FileInput, forms.widgets.DateInput,
                                   forms.widgets.DateTimeInput)):
                classes = widget.attrs.get('class', '')
                widget.attrs.update({'class': f'{classes} form-control'.strip()})

        # Añadir clases adicionales a campos específicos
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
    id_linea = forms.ModelChoiceField(queryset=Linea.objects.all(), label="linea", empty_label="Seleccione la línea",required=False)
    
    discapacidad_asistente = forms.CharField(max_length=50,required=False)
    procedencia_asistente = forms.CharField(max_length=50,required=False)
    id_genero_asistente = forms.ModelChoiceField(queryset=Genero.objects.all(), empty_label="Seleccione el género",required=False)


    class Meta:
        model = Persona
        fields = ['id_genero', 'id_area', 'id_linea', 'id_ambiente', 'id_tipo_documento_asistente', 'nombre_asistente', 'apellidos_asistente', 'telefono_asistente', 'correo_asistente', 'identificacion_asistente', 'identificacion', 'nombres', 'apellidos', 'telefono', 'correo','id_tipo_documento']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_tipo_documento'].queryset = TipoDocumento.objects.all()
        self.fields['id_tipo_documento'].empty_label = "Seleccione un tipo de documento"
        self.fields['id_genero'].queryset = Genero.objects.all()
        self.fields['id_genero'].empty_label = "Seleccione el género"
        self.fields['id_area'].initial = None
        self.fields['id_area'].queryset = Area.objects.all()
        self.fields['id_area'].empty_label = "Seleccione una estrategia"
        self.fields['id_ambiente'].initial = None        
        self.fields['id_ambiente'].queryset = Ambiente.objects.all()
        self.fields['id_ambiente'].empty_label = "Seleccione el ambiente"
        self.fields['id_linea'].initial = None
        self.fields['id_linea'].queryset = Linea.objects.all()
        self.fields['id_linea'].empty_label = "Seleccione la linea"
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

    class Meta:
        model = Visita
        fields = ['fecha_inicio', 'fecha_finalizacion', 'discapacidad', 'procedencia','grabacion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['procedencia'].widget.attrs.update({'placeholder': 'Ingrese su procedencia'})
        self.fields['discapacidad'].widget.attrs.update({'placeholder': 'Ingrese su discapacidad'})
        self._init_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_finalizacion = cleaned_data.get("fecha_finalizacion")

        if fecha_inicio and fecha_finalizacion:
            # Validar que la fecha de inicio y finalización sean el mismo día
            if fecha_inicio.date() != fecha_finalizacion.date():
                raise forms.ValidationError("La fecha de inicio y finalización deben ser el mismo día.")
            
            # Validar que no sea fin de semana
            if fecha_inicio.weekday() >= 5 or fecha_finalizacion.weekday() >= 5:
                raise forms.ValidationError("No se permiten reservas los sábados y domingos.")
            
            # Validar las horas permitidas
            if fecha_inicio.time() == datetime.time(12, 0):
                raise forms.ValidationError("No es posible establecer la fecha de inicio a las 12:00.")

            if not ((datetime.time(8, 0) <= fecha_inicio.time() <= datetime.time(12, 0)) or (datetime.time(14, 0) <= fecha_inicio.time() <= datetime.time(17, 0))):
                raise forms.ValidationError("La hora de inicio debe estar entre las 08:00-12:00 o 14:00-17:00.")
            
            if not ((datetime.time(8, 0) <= fecha_finalizacion.time() <= datetime.time(12, 0)) or (datetime.time(14, 0) <= fecha_finalizacion.time() <= datetime.time(17, 0))):
                raise forms.ValidationError("La hora de finalización debe estar entre las 08:00-12:00 o 14:00-17:00.")












