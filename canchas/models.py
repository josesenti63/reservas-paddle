"""
Modelos de la app 'canchas'.

Cancha            → representa una cancha física del club
HorarioDisponible → define los bloques de tiempo reservables
"""

from django.db import models


class Cancha(models.Model):
    """
    Una cancha física del club.
    El administrador la crea y la activa o desactiva según disponibilidad.
    """

    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Ej: Cancha 1, Cancha Central, Cancha Techada'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Información adicional (superficie, iluminación, etc.)'
    )
    activa = models.BooleanField(
        default=True,
        verbose_name='Activa',
        help_text='Desmarcá si la cancha está fuera de servicio'
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'
        ordering = ['nombre']

    def __str__(self):
        estado = '✓' if self.activa else '✗'
        return f'{estado} {self.nombre}'


class HorarioDisponible(models.Model):
    """
    Bloque horario en el que se puede hacer una reserva.
    Ej: 08:00–09:00, lunes a viernes.

    Los días de la semana se guardan como texto separado por comas.
    Ej: "lunes,martes,miércoles,jueves,viernes"
    """

    DIAS_CHOICES = [
        ('lunes',     'Lunes'),
        ('martes',    'Martes'),
        ('miércoles', 'Miércoles'),
        ('jueves',    'Jueves'),
        ('viernes',   'Viernes'),
        ('sábado',    'Sábado'),
        ('domingo',   'Domingo'),
    ]

    hora_inicio = models.TimeField(
        verbose_name='Hora de inicio',
        help_text='Ej: 08:00'
    )
    hora_fin = models.TimeField(
        verbose_name='Hora de fin',
        help_text='Ej: 09:00'
    )
    # Guardamos los días como texto para simplicidad.
    # Ej: "lunes,martes,miércoles,jueves,viernes"
    dias_semana = models.CharField(
        max_length=100,
        verbose_name='Días disponibles',
        help_text='Separados por coma. Ej: lunes,martes,miércoles'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    class Meta:
        verbose_name = 'Horario disponible'
        verbose_name_plural = 'Horarios disponibles'
        ordering = ['hora_inicio']

    def __str__(self):
        return f'{self.hora_inicio.strftime("%H:%M")} – {self.hora_fin.strftime("%H:%M")}'

    def get_dias_lista(self):
        """Devuelve los días como lista Python. Útil en templates."""
        return [d.strip() for d in self.dias_semana.split(',')]