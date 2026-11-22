from django.contrib import admin
from .models import Grabacion

admin.site.site_header = 'TriageVoz - Administración'
admin.site.site_title = 'TriageVoz'
admin.site.index_title = 'Panel de administración'


@admin.register(Grabacion)
class GrabacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'texto', 'error')
    search_fields = ('texto',)
