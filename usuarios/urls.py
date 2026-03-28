from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Registro de nuevo socio
    path('registro/', views.registro, name='registro'),
    
    # Inicio de sesión
    path('login/', views.login_view, name='login'),
    
    # Cierre de sesión
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil del socio
    path('perfil/', views.perfil, name='perfil'),
]