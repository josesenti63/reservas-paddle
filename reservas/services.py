"""
Servicio de pagos — reservas/services.py

Encapsula toda la lógica de pagos en un solo lugar.
Hoy usa el simulador interno; cuando haya credenciales reales
de MercadoPago solo se modifica este archivo, sin tocar vistas ni modelos.

Patrón usado: Service Layer.
Las vistas llaman a estas funciones y no saben si el pago
es simulado o real. Eso hace que el código sea fácil de mantener.
"""

from decimal import Decimal
from django.utils import timezone
from .models import Reserva, Pago


# ─── Precio base por hora de cancha ──────────────────────────────────────────
# En producción esto podría estar en la base de datos
# (un campo precio en el modelo Cancha).
PRECIO_POR_HORA = Decimal('3500.00')  # pesos argentinos


def calcular_monto(reserva: Reserva) -> Decimal:
    """
    Calcula el monto a cobrar por una reserva.
    Por ahora precio fijo; en el futuro puede variar por cancha u horario.
    """
    return PRECIO_POR_HORA


def iniciar_pago(reserva: Reserva) -> dict:
    """
    Crea o recupera el Pago asociado a una reserva
    y devuelve los datos necesarios para mostrar la pantalla de pago.

    Retorna un dict con:
        pago       → instancia del modelo Pago
        monto      → Decimal con el monto
        simulado   → True (cambiar a False cuando se integre MP real)
    """
    # Si ya existe un pago pendiente para esta reserva, lo reutilizamos
    pago, creado = Pago.objects.get_or_create(
        reserva=reserva,
        defaults={
            'monto' : calcular_monto(reserva),
            'estado': Pago.ESTADO_PENDIENTE,
        }
    )

    return {
        'pago'    : pago,
        'monto'   : pago.monto,
        'simulado': True,  # ← cambiar a False al integrar MP real
    }


def procesar_pago_simulado(pago: Pago, resultado: str) -> bool:
    """
    Simula la respuesta de MercadoPago.

    resultado puede ser:
        'aprobar'  → simula pago exitoso
        'rechazar' → simula pago fallido

    Retorna True si el pago quedó aprobado, False si fue rechazado.
    """
    if resultado == 'aprobar':
        pago.estado = Pago.ESTADO_SIMULADO
        pago.save()

        # Confirmar la reserva y marcarla como pagada
        pago.reserva.estado = Reserva.ESTADO_CONFIRMADA
        pago.reserva.pagado = True
        pago.reserva.save()
        return True

    elif resultado == 'rechazar':
        pago.estado = Pago.ESTADO_RECHAZADO
        pago.save()
        return False

    return False


# ─── Estructura para MercadoPago real (a completar en producción) ─────────────

def iniciar_pago_mercadopago(reserva: Reserva) -> dict:
    """
    PRODUCCIÓN: crea una preferencia de pago en MercadoPago.

    Para activar:
    1. pip install mercadopago
    2. Agregar MP_ACCESS_TOKEN en el .env
    3. Descomentar el código de abajo y comentar el simulador en iniciar_pago()

    import mercadopago
    from django.conf import settings

    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": f"Reserva {reserva.cancha.nombre} - {reserva.fecha}",
            "quantity": 1,
            "unit_price": float(calcular_monto(reserva)),
        }],
        "back_urls": {
            "success": f"{settings.SITE_URL}/reservas/pago/exito/",
            "failure": f"{settings.SITE_URL}/reservas/pago/error/",
            "pending": f"{settings.SITE_URL}/reservas/pago/pendiente/",
        },
        "auto_return": "approved",
        "external_reference": str(reserva.id),
        "notification_url": f"{settings.SITE_URL}/reservas/pago/webhook/",
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    pago = Pago.objects.create(
        reserva=reserva,
        monto=calcular_monto(reserva),
        mp_preference_id=preference["id"],
    )

    return {
        "init_point": preference["init_point"],   # URL de pago de MP
        "pago": pago,
    }
    """
    raise NotImplementedError(
        "Integración con MercadoPago no activada. "
        "Seguí las instrucciones en el docstring de esta función."
    )


def webhook_mercadopago(payment_id: str) -> bool:
    """
    PRODUCCIÓN: recibe y procesa la notificación de MercadoPago.

    MP envía un POST a /reservas/pago/webhook/ cuando se aprueba un pago.
    Esta función verifica el pago contra la API de MP y actualiza la reserva.

    import mercadopago
    from django.conf import settings

    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
    payment_info = sdk.payment().get(payment_id)
    data = payment_info["response"]

    if data["status"] == "approved":
        reserva_id = data["external_reference"]
        pago = Pago.objects.get(reserva_id=reserva_id)
        pago.mp_payment_id = payment_id
        pago.estado = Pago.ESTADO_APROBADO
        pago.save()

        pago.reserva.pagado = True
        pago.reserva.estado = Reserva.ESTADO_CONFIRMADA
        pago.reserva.save()
        return True

    return False
    """
    raise NotImplementedError("Webhook de MercadoPago no activado.")