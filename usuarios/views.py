"""
Vistas de la app 'usuarios'.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegistroForm, PerfilForm


def registro(request):
    if request.user.is_authenticated:
        return redirect('reservas:inicio')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'¡Bienvenido/a, {user.first_name}! Tu cuenta fue creada correctamente.'
            )
            return redirect('reservas:inicio')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('reservas:inicio')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'reservas:inicio')
            messages.success(request, f'¡Bienvenido/a de nuevo, {user.first_name or user.username}!')
            return redirect(next_url)
        else:
            error = 'Usuario o contraseña incorrectos.'

    return render(request, 'usuarios/login.html', {'error': error})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('reservas:inicio')


@login_required
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(
            request.POST,
            instance=request.user.perfil,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(
            instance=request.user.perfil,
            user=request.user,
        )

    from reservas.models import Reserva
    ultimas_reservas = Reserva.objects.filter(
        usuario=request.user
    ).order_by('-fecha', '-creada_en')[:5]

    context = {
        'form'            : form,
        'ultimas_reservas': ultimas_reservas,
    }
    return render(request, 'usuarios/perfil.html', context)