"""
Configuración del panel de administración para la app 'usuarios'.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario


class PerfilInline(admin.StackedInline):
    """
    Muestra el perfil del socio dentro de la ficha del User.
    Así el administrador ve todo en una sola pantalla.
    """
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Datos de socio'


class UserAdmin(BaseUserAdmin):
    """
    Extiende el UserAdmin de Django para incluir el perfil inline.
    """
    inlines = (PerfilInline,)


# Reemplazamos el UserAdmin por defecto con el nuestro
admin.site.unregister(User)
admin.site.register(User, UserAdmin)