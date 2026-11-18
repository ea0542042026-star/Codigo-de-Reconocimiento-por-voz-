from django.contrib import admin
from .models import Paciente, RegistroTriage

admin.site.site_header = 'TriageVoz - Administración'
admin.site.site_title = 'TriageVoz'
admin.site.index_title = 'Panel de administración'


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'edad', 'sexo', 'telefono', 'fecha_registro')
    list_filter = ('sexo',)
    search_fields = ('nombres', 'apellidos', 'telefono')


@admin.register(RegistroTriage)
class RegistroTriageAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'prioridad', 'prioridad_sugerida', 'estado', 'fecha')
    list_filter = ('prioridad', 'estado')
    search_fields = ('paciente__nombres', 'paciente__apellidos', 'motivo', 'sintomas')
