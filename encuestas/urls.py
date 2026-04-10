from django.urls import path
from . import views

app_name = "encuestas"

urlpatterns = [
    # Rutas principales
    path("", views.InicioView.as_view(), name="inicio"),
    path("<int:pk>/", views.DetalleView.as_view(), name="detalle"),
    path("<int:pregunta_id>/votar/", views.votar, name="votar"),

    # Rutas de creación y autenticación
    path("crear/", views.crear_encuesta, name="crear"),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    
    # Rutas de edición
    path('editar/<int:pregunta_id>/', views.editar_encuesta, name='editar'),
    path('opcion/<int:opcion_id>/eliminar/', views.eliminar_opcion, name='eliminar_opcion'),
]