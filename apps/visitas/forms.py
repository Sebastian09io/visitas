from django import forms
from apps.funcionarios.models import Persona, Area, Ambiente, Linea, Genero, Visita, TipoDocumento, Asistente 

class BootstrapFormMixin:
    def _init_bootstrap(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.widgets.TextInput, forms.widgets.Select,
                                   forms.widgets.EmailInput, forms.widgets.PasswordInput,
                                   forms.widgets.FileInput, forms.widgets.DateInput,
                                   forms.widgets.DateTimeInput)):
                widget.attrs.update({'class': 'form-control'})

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
        self.fields['id_area'].queryset = Area.objects.all()
        self.fields['id_area'].empty_label = "Seleccione una estrategia"
        self.fields['id_ambiente'].queryset = Ambiente.objects.all()
        self.fields['id_ambiente'].empty_label = "Seleccione el ambiente"
        self.fields['id_linea'].queryset = Linea.objects.all()
        self.fields['id_linea'].empty_label = "Seleccione la linea"
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
    fecha_inicio = forms.DateTimeField(label="Fecha de inicio", widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}))
    fecha_finalizacion = forms.DateTimeField(label="Fecha de finalización", widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}))
    grabacion =forms.BooleanField(required=False, initial=False) 
    class Meta:
        model = Visita
        fields = [ 'fecha_inicio', 'fecha_finalizacion', 'discapacidad', 'procedencia',]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['procedencia'].widget.attrs.update({'placeholder': 'Ingrese su procedencia'})
        self.fields['discapacidad'].widget.attrs.update({'placeholder': 'Ingrese su discapacidad'})
        self._init_bootstrap()