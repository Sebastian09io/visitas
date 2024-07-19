from django import forms
from apps.funcionarios.models import Persona, TipoDocumento, Cargo, Dependencia
from apps.reservas.models import Reserva

class BootstrapFormMixin:
    def _init_bootstrap(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.widgets.TextInput, forms.widgets.Select,
                                    forms.widgets.EmailInput, forms.widgets.PasswordInput,
                                    forms.widgets.FileInput)):
                widget.attrs.update({'class': 'form-control'})

class PerfilForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Persona
        fields = ['id_tipo_documento', 'identificacion', 'nombres', 'apellidos', 'telefono', 'correo', 'id_cargo', 'id_dependencia']

    def __init__(self, *args, **kwargs):
        super(PerfilForm, self).__init__(*args, **kwargs)
        self.fields['id_tipo_documento'].queryset = TipoDocumento.objects.all()
        self.fields['id_tipo_documento'].empty_label = "Seleccione un tipo de documento"
        self.fields['id_cargo'].queryset = Cargo.objects.all()
        self.fields['id_cargo'].empty_label = "Seleccione un cargo"
        self.fields['id_dependencia'].queryset = Dependencia.objects.all()
        self.fields['id_dependencia'].empty_label = "Seleccione una dependencia"
        self._init_bootstrap()

    def save(self, commit=True):
        user = super(PerfilForm, self).save(commit=False)
        if commit:
            user.save()
        return user

class ImagenPerfilForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['imagen_perfil']

# Reserva de espacio
class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['id_espacio', 'motivo', 'fecha_inicio', 'fecha_finalizacion']

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_finalizacion = cleaned_data.get("fecha_finalizacion")
        espacio = cleaned_data.get("id_espacio")

        if fecha_inicio and fecha_finalizacion:
            if fecha_inicio >= fecha_finalizacion:
                raise forms.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

            reservas = Reserva.objects.filter(espacio=espacio, fecha_inicio__lt=fecha_finalizacion, fecha_fin__gt=fecha_inicio)
            if reservas.exists():
                raise forms.ValidationError("Este espacio ya está reservado en el periodo seleccionado.")

        return cleaned_data