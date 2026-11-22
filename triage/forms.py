from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistroForm(UserCreationForm):
    """Formulario para crear una cuenta nueva.

    Hereda de UserCreationForm (ya trae usuario y las dos contraseñas)
    y le agrega el nombre y el correo electrónico.
    """

    first_name = forms.CharField(label='Nombre completo', max_length=150)
    email = forms.EmailField(label='Correo electrónico')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
        labels = {'username': 'Usuario'}
        help_texts = {'username': 'Solo letras, números y @ . + - _'}

    def clean_email(self):
        """No se puede usar un correo que ya tiene otra cuenta."""
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return email
