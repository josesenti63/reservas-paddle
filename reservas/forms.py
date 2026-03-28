"""
    Formularios de app 'reservas'
    
    ReservaFrom -> el formulario principal que usa el socio para reservar una cancha
"""
    
from django import forms
from django.utils import timezone
from .models import Reserva
from canchas.models import Cancha, HorarioDisponible

class ReservaForm(forms.ModelForm):
    """
    Formulario para crear una nueva reserva.
 
    Solo muestra canchas activas y horarios activos.
    La validación de disponibilidad real se hace en el método clean().
    """
    
    class Meta:
        model = Reserva
        fields =['cancha', 'fecha', 'horario']
        widgets = {
            # Input de fecha del navegador -> abre el calendario del celular
            
            'fecha' : forms.DateInput (
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                },
                format='%Y-%m-%d',
            ),
            'cancha': forms.Select(attrs={'class':'form-select'}),
            'horario': forms.Select(attrs={'class':'form-select'}),
        } 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Solo mostrar canchas activas
        self.fields['cancha'].queryset = Cancha.objects.filter(activa=True)
        
        # Solo mostrar horarios activos
        self.fields['horario'].queryset= HorarioDisponible.objects.filter(activo=True)
        
        # Etiquetas en español
        self.fields['cancha'].label  = 'Cancha'
        self.fields['fecha'].label   = 'Fecha'
        self.fields['horario'].label = 'Horario'
 
        # Mensaje de ayuda bajo el campo fecha
        self.fields['fecha'].help_text = 'Seleccioná el día que querés jugar.'
        
    def clean_fecha(self):
        """
        Validación 1: la fecha no puede ser en el pasado.
        No tiene sentido reservar para ayer.
        """
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError('No podes reservar para una fecha pasada')
        return fecha
    
    def clean(self):
        """
        Validación 2: verificar que la cancha no esté ya reservada
        para esa fecha y horario.
 
        Esta validación necesita los tres campos juntos (cancha + fecha + horario),
        por eso va en clean() y no en clean_campo_individual().
        """
        cleaned_data = super().clean()
        cancha  = cleaned_data.get('cancha')
        fecha   = cleaned_data.get('fecha')
        horario = cleaned_data.get('horario')
 
        if cancha and fecha and horario:
            reserva_existente = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha,
                horario=horario,
            ).exclude(estado=Reserva.ESTADO_CANCELADA)
 
            if reserva_existente.exists():
                raise forms.ValidationError(
                    f'La {cancha} ya está reservada para ese día y horario. '
                    f'Elegí otro horario o cancha disponible.'
                )
 
        return cleaned_data