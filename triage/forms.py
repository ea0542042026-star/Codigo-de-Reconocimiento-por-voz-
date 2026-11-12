from django import forms
from .models import Paciente, RegistroTriage


class PacienteForm(forms.ModelForm):
    """Formulario con los datos del paciente."""

    class Meta:
        model = Paciente
        fields = ['nombres', 'apellidos', 'edad', 'sexo']
        error_messages = {
            'nombres': {'required': 'El nombre es obligatorio.'},
            'apellidos': {'required': 'Los apellidos son obligatorios.'},
        }

    def clean_nombres(self):
        """El nombre no puede quedar vacío ni con solo espacios."""
        nombres = self.cleaned_data.get('nombres')
        if not nombres or not nombres.strip():
            raise forms.ValidationError('El nombre es obligatorio.')
        return nombres.strip()

    def clean_apellidos(self):
        """Los apellidos no pueden quedar vacíos ni con solo espacios."""
        apellidos = self.cleaned_data.get('apellidos')
        if not apellidos or not apellidos.strip():
            raise forms.ValidationError('Los apellidos son obligatorios.')
        return apellidos.strip()

    def clean_edad(self):
        """La edad no puede ser negativa."""
        edad = self.cleaned_data.get('edad')
        if edad is None or edad < 0:
            raise forms.ValidationError('La edad no puede ser negativa.')
        return edad


class RegistroTriageForm(forms.ModelForm):
    """Formulario con la evaluación de triage."""

    class Meta:
        model = RegistroTriage
        fields = ['motivo', 'transcripcion', 'presion_sistolica', 'presion_diastolica',
                  'saturacion', 'temperatura', 'dolor', 'prioridad']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 2}),
            'transcripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        """La presión diastólica debe ser menor que la sistólica."""
        datos = super().clean()
        sis = datos.get('presion_sistolica')
        dia = datos.get('presion_diastolica')
        if sis and dia and dia >= sis:
            self.add_error('presion_diastolica', 'Debe ser menor que la presión sistólica.')
        return datos
