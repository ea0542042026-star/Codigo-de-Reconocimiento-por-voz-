from django import forms
from .models import Paciente, RegistroTriage


class PacienteForm(forms.ModelForm):
    """Formulario con los datos del paciente."""

    class Meta:
        model = Paciente
        fields = ['nombres', 'apellidos', 'edad', 'sexo']


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
