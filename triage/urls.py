from django.urls import path
from . import views

app_name = 'triage'

urlpatterns = [
    path('', views.inicio, name='inicio'),                          # grabar
    path('subir/', views.subir_audio, name='subir_audio'),          # recibe el audio
    path('grabaciones/', views.grabaciones, name='grabaciones'),    # lista numerada
    path('grabaciones/<int:pk>/', views.detalle, name='detalle'),
    path('grabaciones/<int:pk>/transcribir/', views.transcribir_otra_vez, name='transcribir_otra_vez'),
    path('grabaciones/<int:pk>/texto/', views.descargar_texto, name='descargar_texto'),
    path('grabaciones/<int:pk>/eliminar/', views.eliminar, name='eliminar'),
]
