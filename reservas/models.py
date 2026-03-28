"""
Modelos de la app 'reservas'.

Reserva → el corazón del sistema. Vincula un usuario, una cancha y un horario.
"""

from django.db import models
from django.contrib.auth.models import User
from canchas.models import Cancha, HorarioDisponible


class Reserva(models.Model):
    """
    Representa una reserva de cancha hecha por un usuario.

    Estados posibles:
        pendiente  → reserva creada, esperando pago o confirmación
        confirmada → pago recibido o confirmada manualmente por el club
        cancelada  → cancelada por el usuario o por el club
    """

    ESTADO_PENDIENTE  = 'pendiente'
    ESTADO_CONFIRMADA = 'confirmada'
    ESTADO_CANCELADA  = 'cancelada'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE,  'Pendiente'),
        (ESTADO_CONFIRMADA, 'Confirmada'),
        (ESTADO_CANCELADA,  'Cancelada'),
    ]

    # ─── Relaciones ───────────────────────────────────────────────────────────
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Usuario'
    )
    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Cancha'
    )
    horario = models.ForeignKey(
        HorarioDisponible,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name='Horario'
    )

    # ─── Datos de la reserva ──────────────────────────────────────────────────
    fecha = models.DateField(
        verbose_name='Fecha',
        help_text='Día en que se jugará'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name='Estado'
    )
    pagado = models.BooleanField(
        default=False,
        verbose_name='Pagado'
    )

    # ─── Auditoría ────────────────────────────────────────────────────────────
    creada_en     = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['fecha', 'horario__hora_inicio']

        # Restricción clave: no puede haber dos reservas
        # para la misma cancha, el mismo día y el mismo horario.
        constraints = [
            models.UniqueConstraint(
                fields=['cancha', 'fecha', 'horario'],
                name='reserva_unica_por_cancha_fecha_horario'
            )
        ]

    def __str__(self):
        return (
            f'{self.cancha} · {self.fecha} · '
            f'{self.horario} · {self.usuario.get_full_name() or self.usuario.username}'
        )

    def esta_confirmada(self):
        return self.estado == self.ESTADO_CONFIRMADA

    def esta_cancelada(self):
        return self.estado == self.ESTADO_CANCELADA

    def puede_cancelarse(self):
        """
        Una reserva solo puede cancelarse si no está ya cancelada.
        En la Parte 2 se agrega la validación de anticipación mínima.
        """
        return self.estado != self.ESTADO_CANCELADA
    

class Pago(models.Model):
    """
    Registra cada intento de pago vinculado a una reserva.
 
    Diseñado para funcionar con el simulador interno ahora
    y con MercadoPago real en el futuro sin cambiar la estructura.
    """
 
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADO = 'aprobado'
    ESTADO_RECHAZADO = 'rechazado'
    ESTADO_SIMULADO = 'simulado'
    
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_APROBADO, 'Aprobado'),
        (ESTADO_RECHAZADO, 'Rechazado'),
        (ESTADO_SIMULADO, 'Simulado (demo)'),
    ]
    
    reserva = models.OneToOneField(
        Reserva,
        on_delete=models.CASCADE,
        related_name='pago',
        verbose_name='Reserva',
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto',
        help_text='En pesos argentinos',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name='Estado del pago',
    )
    
    # Campos para MercadoPago real (vacíos en modo simulado)
    mp_preference_id = models.CharField(
        max_length=200, blank=True,
        verbose_name='MP Preference ID',
    )
    mp_payment_id = models.CharField(
        max_length=200, blank=True,
        verbose_name='MP Payment ID',
    )
 
    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
 
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-creado_en']
 
    def __str__(self):
        return (
            f'Pago #{self.id} · {self.reserva.cancha} · '
            f'${self.monto} · {self.get_estado_display()}'
        )
 
    def esta_aprobado(self):
        """Un pago simulado también cuenta como aprobado."""
        return self.estado in (self.ESTADO_APROBADO, self.ESTADO_SIMULADO)
 