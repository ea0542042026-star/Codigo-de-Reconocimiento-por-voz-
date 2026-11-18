import re

from django import forms
from .models import Paciente, RegistroTriage


class PacienteForm(forms.ModelForm):
    """Formulario con los datos del paciente."""

    class Meta:
        model = Paciente
        fields = ['nombres', 'apellidos', 'edad', 'sexo', 'telefono']
        error_messages = {
            'nombres': {'required': 'El nombre es obligatorio.'},
            'apellidos': {'required': 'Los apellidos son obligatorios.'},
            'edad': {'required': 'La edad es obligatoria.'},
            'sexo': {'required': 'Elige el sexo.'},
        }
        widgets = {
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej. 7777-8888'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Texto en español para la opción vacía de la lista de sexo
        self.fields['sexo'].choices = [('', '-- Elige --')] + Paciente.SEXO

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

    def clean_telefono(self):
        """Solo números y guion, de 8 dígitos (formato de El Salvador)."""
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono and not re.fullmatch(r'\d{4}-?\d{4}', telefono):
            raise forms.ValidationError('Escribe 8 números, por ejemplo 7777-8888.')
        return telefono


class ElegirPacienteForm(forms.Form):
    """Permite elegir un paciente que ya existe, en vez de escribirlo de nuevo."""

    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(), required=False,
        empty_label='-- Paciente nuevo --', label='Paciente registrado')


class RegistroTriageForm(forms.ModelForm):
    """Formulario con la evaluación de triage."""

    class Meta:
        model = RegistroTriage
        fields = ['motivo', 'transcripcion', 'presion_sistolica', 'presion_diastolica',
                  'frecuencia_cardiaca', 'saturacion', 'temperatura', 'dolor', 'prioridad']
        error_messages = {
            'motivo': {'required': 'Escribe el motivo de consulta.'},
        }
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
