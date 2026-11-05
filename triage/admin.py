from django.contrib import admin
from .models import Paciente, RegistroTriage


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'edad', 'sexo')
    search_fields = ('nombres', 'apellidos')


@admin.register(RegistroTriage)
class RegistroTriageAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'prioridad', 'fecha')
    list_filter = ('prioridad',)
    search_fields = ('paciente__nombres', 'paciente__apellidos', 'motivo')
