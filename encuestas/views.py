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
    # 1. Buscamos la pregunta o marcamos error 404 si no existe
    pregunta = get_object_or_404(Pregunta, pk=pregunta_id)
    
    if request.method == 'POST':
        # 2. Le pasamos los datos nuevos, pero le decimos que actualice la instancia existente
        form = PreguntaForm(request.POST, instance=pregunta)
        
        if form.is_valid():
            pregunta_editada = form.save()
            
            # 3. Truco rápido para las opciones: borramos las viejas y guardamos las nuevas
            pregunta.opcion_set.all().delete()
            opciones_enviadas = request.POST.getlist('opciones[]')
            
            for texto in opciones_enviadas:
                if texto.strip(): 
                    Opcion.objects.create(
                        pregunta=pregunta_editada, 
                        texto_opcion=texto
                    )
            
            return redirect('encuestas:inicio')
            
    else:
        # 4. Si es GET, cargamos el formulario lleno con los datos actuales
        form = PreguntaForm(instance=pregunta)

    # Obtenemos las opciones actuales para mandarlas al template
    opciones = pregunta.opcion_set.all()

    return render(request, 'encuestas/editar.html', {
        'form': form,
        'pregunta': pregunta,
        'opciones': opciones
    })