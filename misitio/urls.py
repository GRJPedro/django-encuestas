from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [

    path('', TemplateView.as_view(template_name='inicio_sitio.html'), name='inicio_sitio'), 
    
    path('mapa/', TemplateView.as_view(template_name='mapa.html'), name='mapa'),
    
    path('encuestas/', include('encuestas.urls')),
    
    path('admin/', admin.site.urls),
]