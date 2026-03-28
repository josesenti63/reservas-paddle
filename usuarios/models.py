"""
Modelos de la app 'usuarios'.

PerfilUsuario → extiende el User de Django con datos del socio del club.

¿Por qué extender el User con un perfil en lugar de crear un User personalizado?
Porque para este proyecto los datos extra son pocos (teléfono, número de socio)
y el perfil vinculado es la solución más simple y mantenible.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    """
    Datos adicionales del socio, vinculados al User estándar de Django.
    Se crea automáticamente al registrar un nuevo usuario (ver señal abajo).
    """

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono',
        help_text='Número de contacto (WhatsApp)'
    )
    numero_socio = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Número de socio',
        help_text='Número de socio del club (opcional)'
    )

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuarios'

    def __str__(self):
        return f'Perfil de {self.usuario.get_full_name() or self.usuario.username}'


# ─── Señales ──────────────────────────────────────────────────────────────────
# Cuando Django crea un nuevo User, automáticamente creamos su PerfilUsuario.
# Esto evita tener que crear el perfil a mano en cada vista de registro.

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Se dispara al crear un User nuevo."""
    if created:
        PerfilUsuario.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Se dispara al guardar un User existente."""
    instance.perfil.save()