"""
URL configuration for config project.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Inicio y cierre de sesión (vistas que ya trae Django)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('salir/', auth_views.LogoutView.as_view(), name='logout'),

    path('', include('triage.urls')),
]

# Para poder abrir los audios guardados en media/ mientras desarrollamos - T013
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
