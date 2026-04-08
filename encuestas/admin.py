from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from .models import Pregunta, Opcion

@admin.register(Pregunta)
class PreguntaAdmin(gis_admin.GISModelAdmin):
    list_display = ('texto_pregunta', 'fecha_publicacion', 'ubicacion')

admin.site.register(Opcion)