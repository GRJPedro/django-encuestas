from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic

from django.utils import timezone 
from .models import Pregunta, Opcion 
from .forms import PreguntaForm 

from .models import Opcion, Pregunta

class InicioView(generic.ListView):
    template_name = "encuestas/index.html"
    context_object_name = "ultimas_preguntas"

    def get_queryset(self):
        """Regresa las últimas cinco preguntas publicadas."""
        return Pregunta.objects.order_by("-fecha_publicacion")[:5]


class DetalleView(generic.DetailView):
    model = Pregunta
    template_name = "encuestas/detalle.html"


def votar(request, pregunta_id):
    pregunta = get_object_or_404(Pregunta, pk=pregunta_id)
    try:
        opcion_seleccionada = pregunta.opcion_set.get(pk=request.POST["opcion"])
    except (KeyError, Opcion.DoesNotExist):
        return render(
            request,
            "encuestas/detalle.html",
            {
                "pregunta": pregunta,
                "error_message": "No seleccionaste ninguna opción.",
            },
        )
    else:
        opcion_seleccionada.votos = F("votos") + 1
        opcion_seleccionada.save()
        return HttpResponseRedirect(reverse("encuestas:detalle", args=(pregunta.id,)))


@login_required
def crear_encuesta(request):
    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        
        if form.is_valid():
            # aqui se guarda la pregunta
            nueva_pregunta = form.save(commit=False)
            nueva_pregunta.fecha_publicacion = timezone.now()
            nueva_pregunta.save() 
            
            #aqui se registran las opciones getlist obtiene todos los inputs que tengan el name="opciones[]"
            opciones_enviadas = request.POST.getlist('opciones[]')
            
            #Guardamos cada opción en la base de datos vinculándola a la pregunta
            for texto in opciones_enviadas:
                if texto.strip(): 
                    Opcion.objects.create(
                        pregunta=nueva_pregunta, 
                        texto_opcion=texto
                    )
            
            return redirect('encuestas:inicio')
            
    else:
        form = PreguntaForm()

    return render(request, 'encuestas/crear.html', {'form': form})



#Aqui este pedo ya que son las usuarios y autenticaciones
def registro(request):
    # Si el usuario le dio clic al botón de enviar (POST)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # Aquí se guarda el usuario en la base de datos como el /admin
            return redirect('encuestas:inicio') # Lo mandamos al inicio tras registrarse
    # Si el usuario apenas entró a la página a ver el formulario (GET)
    else:
        form = UserCreationForm()
    
    # Renderizamos la plantilla pasándole el formulario al registro.html
    return render(request, 'encuestas/registro.html', {'form': form})


def iniciar_sesion(request):
    if request.method == 'POST':
        
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Si el usuario y contraseña son correctos, obtenemos al usuario
            usuario = form.get_user()
            login(request, usuario)
            return redirect('encuestas:inicio')
    else:
        form = AuthenticationForm()
    
    return render(request, 'encuestas/login.html', {'form': form})

def cerrar_sesion(request):
    # Esta función borra la sesión del navegador
    logout(request)
    return redirect('encuestas:inicio')


@login_required
def editar_encuesta(request, pregunta_id):
    pregunta = get_object_or_404(Pregunta, pk=pregunta_id)
    
    if request.method == 'POST':
        form = PreguntaForm(request.POST, instance=pregunta)
        
        if form.is_valid():
            pregunta_editada = form.save()
            
            opciones_enviadas = request.POST.getlist('opciones[]')
            
            # Aqui se sacan las opciones actuales de la DB
            opciones_db = pregunta.opcion_set.values_list('texto_opcion', flat=True)
            
            # Las pasamos a minúsculas, les quitamos espacios y las metemos a un SET
            opciones_existentes = set([texto.strip().lower() for texto in opciones_db])
            
            for texto in opciones_enviadas:
                texto_limpio = texto.strip()
                texto_comparar = texto_limpio.lower() 
                
                # Si tiene texto y NO está en nuestro filtro de opciones existentes...
                if texto_limpio and texto_comparar not in opciones_existentes:
                    
                    # Lo creamos usando el texto_limpio original (para respetar si el usuario usó mayúsculas)
                    Opcion.objects.create(
                        pregunta=pregunta_editada, 
                        texto_opcion=texto_limpio
                    )
                    opciones_existentes.add(texto_comparar)
            
            return redirect('encuestas:inicio')
            
    else:
        # Si es GET, cargamos el formulario lleno con los datos actuales
        form = PreguntaForm(instance=pregunta)

    # Obtenemos las opciones actuales para mandarlas al template
    opciones = pregunta.opcion_set.all()

    return render(request, 'encuestas/editar.html', {
        'form': form,
        'pregunta': pregunta,
        'opciones': opciones
    })


# Funcion para eliminar una opcion de las preguntas
@login_required
def eliminar_opcion(request, opcion_id):
    # Buscamos la opción específica
    opcion = get_object_or_404(Opcion, pk=opcion_id)
    
    # Guardamos el ID de la pregunta para saber a dónde regresar
    pregunta_id = opcion.pregunta.id
    
    opcion.delete()
    
    # Redirigimos de vuelta a la página de edición de esa misma pregunta
    return redirect('encuestas:editar', pregunta_id=pregunta_id)