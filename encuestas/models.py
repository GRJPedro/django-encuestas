import datetime
from django.utils import timezone

from django.contrib.gis.db import models 

class Pregunta(models.Model):
    texto_pregunta = models.CharField(max_length=200)
    fecha_publicacion = models.DateTimeField("fecha de publicación")
    
    ubicacion = models.PointField(null=True, blank=True, srid=4326)

    def __str__(self):
        return self.texto_pregunta
    
    def publicada_recientemente(self):
        return self.fecha_publicacion >= timezone.now() - datetime.timedelta(days=1)

class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    texto_opcion = models.CharField(max_length=200)
    votos = models.IntegerField(default=0)
    
    def __str__(self):
        return self.texto_opcion