from django import forms
from .models import Pregunta

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['texto_pregunta'] 
        labels = {
            'texto_pregunta': '¿Cuál es tu pregunta?',
        }
        widgets = {
            'texto_pregunta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. ¿Qué vas a comer hoy?'}),
        }