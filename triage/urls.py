from django.urls import path
from . import views

app_name = 'triage'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('audio/', views.pagina_audio, name='pagina_audio'),
    path('audio/subir/', views.subir_audio, name='subir_audio'),
]
