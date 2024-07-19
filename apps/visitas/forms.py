from django import forms
from apps.funcionarios.models import Persona, Area, Ambiente, Linea, Genero, Visita

class BootstrapFormMixin:
    def _init_bootstrap(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.widgets.TextInput, forms.widgets.Select,
                                forms.widgets.EmailInput, forms.widgets.PasswordInput,
                                forms.widgets.FileInput, forms.widgets.DateInput,
                                forms.widgets.DateTimeInput)):
                widget.attrs.update({'class': 'form-control'})


class VisitForm(forms.ModelForm, BootstrapFormMixin):
    discapacidad = forms.CharField(max_length=50, label="Discapacidad")
    procedencia = forms.CharField(max_length=80, label="Procedencia")
    fecha_inicio = forms.DateTimeField(label="Fecha de inicio", widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}))
    fecha_finalizacion = forms.DateTimeField(label="Fecha de finalización", widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}))

    class Meta:
        model = Persona
        fields = ['id_genero', 'id_visita', 'id_area', 'id_linea', 'id_ambiente', 'fecha_inicio', 'fecha_finalizacion', 'discapacidad', 'procedencia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_genero'].queryset = Genero.objects.all()
        self.fields['id_genero'].empty_label = "Seleccione el género"
        self.fields['id_area'].queryset = Area.objects.all()
        self.fields['id_area'].empty_label = "Seleccione una estrategia"
        self.fields['id_ambiente'].queryset = Ambiente.objects.all()
        self.fields['id_ambiente'].empty_label = "Seleccione el ambiente"
        self.fields['id_linea'].queryset = Linea.objects.all()
        self.fields['id_linea'].empty_label = "Seleccione la linea"

        if self.instance.id_visita:
            visita = self.instance.id_visita
            self.initial['fecha_inicio'] = visita.fecha_inicio
            self.initial['fecha_finalizacion'] = visita.fecha_finalizacion
            self.initial['discapacidad'] = visita.discapacidad
            self.initial['procedencia'] = visita.procedencia

        self.fields['procedencia'].widget.attrs.update({'placeholder': 'Ingrese su procedencia'})
        self.fields['discapacidad'].widget.attrs.update({'placeholder': 'Ingrese su discapacidad'})

        self._init_bootstrap()

    def save(self, commit=True):
        persona = super().save(commit=False)

        if not persona.id_visita:
            visita = Visita()
        else:
            visita = persona.id_visita

        visita.fecha_inicio = self.cleaned_data['fecha_inicio']
        visita.fecha_finalizacion = self.cleaned_data['fecha_finalizacion']
        visita.discapacidad = self.cleaned_data['discapacidad']
        visita.procedencia = self.cleaned_data['procedencia']

        if commit:
            visita.save()
            persona.id_visita = visita
            persona.save()

        return persona
