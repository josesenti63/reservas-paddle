"""
URLs de la app 'reservas'.
"""

from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    # Página principal: calendario de disponibilidad
    # ej: / o /?fecha=2024-07-15
    path('', views.inicio, name='inicio'),

    # Formulario para crear una reserva
    # ej: /reservas/crear/
    path('reservas/crear/', views.crear_reserva, name='crear_reserva'),

    # Historial de reservas del usuario
    # ej: /reservas/mis-reservas/
    path('reservas/mis-reservas/', views.mis_reservas, name='mis_reservas'),

    # Cancelar una reserva por ID
    # ej: /reservas/cancelar/5/
    path('reservas/cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    
    # ─── Pago ──────────────────────────────────────────────────────────────────
    # Pantalla de pago (simulador o MP en producción)
    path('reservas/pago/<int:reserva_id>/', views.pago, name='pago'),
 
    # Procesar resultado del simulador (solo POST)
    path('reservas/pago/<int:reserva_id>/procesar/', views.procesar_pago, name='procesar_pago'),
 
    # Pantalla de éxito después del pago
    path('reservas/pago/<int:reserva_id>/exito/', views.pago_exito, name='pago_exito'),
 
    # Pantalla de error / pago rechazado
    path('reservas/pago/<int:reserva_id>/error/', views.pago_error, name='pago_error'),
]
