"""
Configuración del panel de administración para la app 'reservas'.
El administrador del club ve y gestiona todas las reservas desde aquí.
"""

from django.contrib import admin
from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """
    Vista de administración para Reserva.

    Funcionalidades:
    - Ver todas las reservas con filtros por fecha, estado y cancha
    - Cambiar el estado de varias reservas a la vez (acción masiva)
    - Buscar por nombre de usuario o cancha
    """

    list_display  = ('fecha', 'horario', 'cancha', 'usuario', 'estado', 'pagado', 'creada_en')
    list_filter   = ('estado', 'pagado', 'cancha', 'fecha')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'cancha__nombre')
    date_hierarchy = 'fecha'
    list_editable = ('estado', 'pagado')
    ordering      = ('-fecha', 'horario__hora_inicio')

    # ─── Acciones masivas ─────────────────────────────────────────────────────
    actions = ['confirmar_reservas', 'cancelar_reservas']

    @admin.action(description='Confirmar reservas seleccionadas')
    def confirmar_reservas(self, request, queryset):
        cantidad = queryset.update(estado=Reserva.ESTADO_CONFIRMADA)
        self.message_user(request, f'{cantidad} reserva(s) confirmada(s).')

    @admin.action(description='Cancelar reservas seleccionadas')
    def cancelar_reservas(self, request, queryset):
        cantidad = queryset.update(estado=Reserva.ESTADO_CANCELADA)
        self.message_user(request, f'{cantidad} reserva(s) cancelada(s).')
        
        
from .models import Pago


class PagoInline(admin.StackedInline):
    """
    Muestra el pago dentro de la ficha de la reserva.
    El admin puede ver y modificar el estado del pago
    sin salir de la reserva.
    """
    model      = Pago
    can_delete = False
    extra      = 0
    readonly_fields = ('creado_en', 'mp_preference_id', 'mp_payment_id')
    
    
# Actualizamos ReservaAdmin para incluir el pago inline
# Desregistramos y volvemos a registrar con la nueva config
admin.site.unregister(Reserva)
 
 
@admin.register(Reserva)
class ReservaAdminConPago(admin.ModelAdmin):
 
    list_display   = ('fecha', 'horario', 'cancha', 'usuario', 'estado', 'pagado', 'pago_estado')
    list_filter    = ('estado', 'pagado', 'cancha', 'fecha')
    search_fields  = ('usuario__username', 'usuario__first_name', 'cancha__nombre')
    date_hierarchy = 'fecha'
    list_editable  = ('estado', 'pagado')
    ordering       = ('-fecha', 'horario__hora_inicio')
    inlines        = [PagoInline]
 
    actions = ['confirmar_reservas', 'cancelar_reservas', 'marcar_pagadas']
 
    @admin.display(description='Estado del pago')
    def pago_estado(self, obj):
        try:
            return obj.pago.get_estado_display()
        except Pago.DoesNotExist:
            return '—'
 
    @admin.action(description='Confirmar reservas seleccionadas')
    def confirmar_reservas(self, request, queryset):
        cantidad = queryset.update(estado=Reserva.ESTADO_CONFIRMADA)
        self.message_user(request, f'{cantidad} reserva(s) confirmada(s).')
 
    @admin.action(description='Cancelar reservas seleccionadas')
    def cancelar_reservas(self, request, queryset):
        cantidad = queryset.update(estado=Reserva.ESTADO_CANCELADA)
        self.message_user(request, f'{cantidad} reserva(s) cancelada(s).')
 
    @admin.action(description='Marcar como pagadas (modo manual)')
    def marcar_pagadas(self, request, queryset):
        cantidad = queryset.update(pagado=True, estado=Reserva.ESTADO_CONFIRMADA)
        self.message_user(request, f'{cantidad} reserva(s) marcada(s) como pagadas y confirmadas.')
 
 
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display  = ('id', 'reserva', 'monto', 'estado', 'creado_en')
    list_filter   = ('estado',)
    readonly_fields = ('mp_preference_id', 'mp_payment_id', 'creado_en', 'actualizado_en')
    search_fields = ('reserva__usuario__username', 'reserva__cancha__nombre')