"""
URLs principales del proyecto reservas_paddle.
Las URLs de cada app se van habilitando por partes.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path('admin/', admin.site.urls),
    
    # App reservas: incluye la pagina de inicio y las URLs de reservas
    path('', include('reservas.urls')),
    
    # App usuarios: registro, login, logout, perfil
    path('usuarios/', include('usuarios.urls')),
]
