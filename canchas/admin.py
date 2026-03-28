"""
Configuración del panel de administración para la app 'canchas'.
El administrador del club gestiona canchas y horarios desde aquí.
"""

from django.contrib import admin
from .models import Cancha, HorarioDisponible


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    """
    Vista de administración para Cancha.
    Muestra nombre, estado y fecha de creación.
    Permite filtrar por activa/inactiva y buscar por nombre.
    """
    list_display  = ('nombre', 'activa', 'creada_en')
    list_filter   = ('activa',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activa',)   # se puede activar/desactivar directo desde la lista


@admin.register(HorarioDisponible)
class HorarioDisponibleAdmin(admin.ModelAdmin):
    """
    Vista de administración para HorarioDisponible.
    """
    list_display  = ('__str__', 'dias_semana', 'activo')
    list_filter   = ('activo',)
    list_editable = ('activo',)