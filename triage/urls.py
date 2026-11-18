from django.urls import path
from . import views

app_name = 'triage'

urlpatterns = [
    # Panel
    path('', views.inicio, name='inicio'),

    # Pacientes
    path('pacientes/', views.pacientes_lista, name='pacientes'),
    path('pacientes/nuevo/', views.paciente_nuevo, name='paciente_nuevo'),
    path('pacientes/<int:pk>/', views.paciente_detalle, name='paciente_detalle'),
    path('pacientes/<int:pk>/editar/', views.paciente_editar, name='paciente_editar'),
    path('pacientes/<int:pk>/eliminar/', views.paciente_eliminar, name='paciente_eliminar'),

    # Audio y Whisper
    path('audio/', views.pagina_audio, name='pagina_audio'),
    path('audio/subir/', views.subir_audio, name='subir_audio'),
    path('audio/transcribir/', views.transcribir_audio, name='transcribir_audio'),

    # Triage
    path('registro/nuevo/', views.registro_nuevo, name='registro_nuevo'),
    path('registro/analizar/', views.analizar_texto, name='analizar_texto'),
    path('registro/<int:pk>/', views.registro_detalle, name='registro_detalle'),
    path('registro/<int:pk>/estado/', views.registro_estado, name='registro_estado'),

    # Historial y reportes
    path('historial/', views.historial, name='historial'),
    path('historial/exportar/', views.exportar_csv, name='exportar_csv'),
    path('reportes/', views.reportes, name='reportes'),
]
