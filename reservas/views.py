"""
Vistas de la app 'reservas'.
 
inicio          → calendario de disponibilidad (página principal)
crear_reserva   → formulario para hacer una reserva
mis_reservas    → historial de reservas del usuario logueado
cancelar_reserva → cancelar una reserva propia
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Reserva
from .forms import ReservaForm
from canchas.models import Cancha, HorarioDisponible


# Create your views here.
def inicio(request):
    """
    Página principal: muestra el calendario de disponibilidad de hoy.
 
    Para cada cancha activa y cada horario activo, calcula si está
    libre o ocupada en la fecha seleccionada (por defecto hoy).
 
    El usuario puede cambiar la fecha con un parámetro GET:
    ej: /?fecha=2024-07-15
    """
 
    # Fecha seleccionada (por defecto hoy)
    fecha_str = request.GET.get('fecha')
    try:
        from datetime import date
        fecha = date.fromisoformat(fecha_str) if fecha_str else timezone.localdate()
    except ValueError:
        fecha = timezone.localdate()
 
    canchas  = Cancha.objects.filter(activa=True)
    horarios = HorarioDisponible.objects.filter(activo=True)
 
    # Reservas confirmadas o pendientes para esa fecha
    reservas_del_dia = Reserva.objects.filter(
        fecha=fecha,
    ).exclude(estado=Reserva.ESTADO_CANCELADA)
 
    # Construimos una estructura fácil de usar en el template:
    # disponibilidad[horario][cancha] = True (libre) o False (ocupada)
    disponibilidad = {}
    for horario in horarios:
        disponibilidad[horario] = {}
        for cancha in canchas:
            ocupada = reservas_del_dia.filter(
                horario=horario,
                cancha=cancha
            ).exists()
            disponibilidad[horario][cancha] = not ocupada
 
    context = {
        'fecha'         : fecha,
        'canchas'       : canchas,
        'horarios'      : horarios,
        'disponibilidad': disponibilidad,
        'hoy'           : timezone.localdate(),
    }
    return render(request, 'reservas/inicio.html', context)


@login_required
def crear_reserva(request):
    """
    Formulario para crear una reserva.
 
    GET  → muestra el formulario vacío
    POST → valida y guarda la reserva
 
    Requiere login: si el usuario no está autenticado lo manda al login.
    """
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)  # No guardar todavía
            reserva.usuario = request.user     # Asignar el usuario logueado
            reserva.estado  = Reserva.ESTADO_PENDIENTE
            reserva.save()
 
            messages.success(
                request,
                f'✓ Reserva creada para el {reserva.fecha} '
                f'en {reserva.cancha} a las {reserva.horario}.'
            )
            return redirect('reservas:mis_reservas')
    else:
        # Si viene de la página de inicio con cancha y fecha preseleccionadas
        initial = {
            'fecha'  : request.GET.get('fecha'),
            'cancha' : request.GET.get('cancha'),
            'horario': request.GET.get('horario'),
        }
        form = ReservaForm(initial=initial)
 
    return render(request, 'reservas/crear_reserva.html', {'form': form})


@login_required
def mis_reservas(request):
    """
    Muestra las reservas del usuario logueado.
 
    Separa las reservas en dos grupos:
    - próximas: fechas de hoy en adelante, no canceladas
    - pasadas:  fechas anteriores a hoy o canceladas
    """
    hoy = timezone.localdate()
 
    proximas = Reserva.objects.filter(
        usuario=request.user,
        fecha__gte=hoy,
    ).exclude(estado=Reserva.ESTADO_CANCELADA).order_by('fecha', 'horario__hora_inicio')
 
    pasadas = Reserva.objects.filter(
        usuario=request.user,
    ).filter(
        fecha__lt=hoy
    ).order_by('-fecha', 'horario__hora_inicio')
 
    context = {
        'proximas': proximas,
        'pasadas' : pasadas,
        'hoy'     : hoy,
    }
    return render(request, 'reservas/mis_reservas.html', context)


@login_required
def cancelar_reserva(request, reserva_id):
    """
    Cancela una reserva del usuario logueado.
 
    Seguridad: usamos get_object_or_404 con usuario=request.user
    para que un usuario no pueda cancelar reservas ajenas.
 
    Solo acepta POST para evitar cancelaciones accidentales por GET.
    """
    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        usuario=request.user  # ← seguridad: solo sus propias reservas
    )
 
    if request.method == 'POST':
        if reserva.puede_cancelarse():
            reserva.estado = Reserva.ESTADO_CANCELADA
            reserva.save()
            messages.success(request, f'Reserva del {reserva.fecha} cancelada.')
        else:
            messages.error(request, 'Esta reserva no puede cancelarse.')
 
        return redirect('reservas:mis_reservas')
 
    # GET → pantalla de confirmación antes de cancelar
    return render(request, 'reservas/confirmar_cancelacion.html', {'reserva': reserva})


# ----- Vistas de pago ----------------------------------------------------------------

@login_required
def pago(request, reserva_id):
    """
    Pantalla de pago para una reserva pendiente.
 
    Muestra el monto y los botones del simulador.
    En producción, esta vista redirige al Checkout Pro de MercadoPago.
    """
    from .services import iniciar_pago
    
    reserva = get_object_or_404(
        Reserva,
        id = reserva_id,
        usuario = request.user,
        estado=Reserva.ESTADO_PENDIENTE,
    )
    
    datos_pago = iniciar_pago(reserva)
    
    return render(request, 'reservas/pago.html', {
        'reserva'  : reserva,
        'pago'     : datos_pago['pago'],
        'monto'    : datos_pago['monto'],
        'simulado' : datos_pago['simulado'],
    })
    
    
@login_required
def procesar_pago(request, reserva_id):
    """
    Procesa la decisión del simulador (aprobar o rechazar).
    Solo acepta POST.
 
    En producción este endpoint no existe: MercadoPago
    redirige directamente a /pago/exito/ o /pago/error/.
    """
    from .services import procesar_pago_simulado
    from .models import Pago
    
    if request.method != 'POST':
        return redirect('reservas:mis_reservas')
    
    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        usuario=request.user,
    )
    
    try:
        pago_obj= reserva.pago 
    except Pago.DoesNotExist:
        messages.error(request, 'No se encontró el pago para esta resserva.')
        return redirect('reservas:mis_reservas')
    
    resultado = request.POST.get('resultado', 'rechazar')
    aprobado = procesar_pago_simulado(pago_obj, resultado)
    
    if aprobado:
        return redirect('reservas:pago_exito', reserva_id=reserva.id)
    else:
        return redirect('reservas:pago_error', reserva_id=reserva.id)
    
    
@login_required
def pago_exito(request, reserva_id):
    """Pantalla de confirmación de pago exitoso."""
    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        usuario=request.user,
    )
    return render(request, 'reservas/pago_exito.html', {'reserva': reserva})


@login_required
def pago_error(request, reserva_id):
    """Pantalla de pago rechazado o fallido."""
    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        usuario=request.user,
    )
    return render(request, 'reservas/pago_error.html', {'reserva': reserva})
    