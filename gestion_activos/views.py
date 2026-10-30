from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from datetime import date
from .models import Herramienta, Prestamo, Contratista, Mantenimiento

# --- SISTEMA DE AUTENTICACIÓN ---

def registro_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f"Cuenta creada exitosamente. Bienvenido a BuildCorp, {usuario.username}.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'gestion_activos/registro.html', {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'gestion_activos/login.html', {'form': form})

def logout_usuario(request):
    logout(request)
    messages.info(request, "Has cerrado sesión de forma segura.")
    return redirect('login')

# --- DASHBOARD Y LÓGICA DE NEGOCIO ---

@login_required(login_url='login')
def dashboard(request):
    # SEGURIDAD: Si alguien intenta hacer un POST (prestar/devolver) y NO es administrador
    if request.method == 'POST' and not request.user.is_staff:
        messages.error(request, "ACCESO DENEGADO: Solo el personal administrativo puede registrar movimientos.")
        return redirect('dashboard')

    # Lógica: Registrar un nuevo préstamo
    if request.method == 'POST' and 'prestar' in request.POST:
        contratista_id = request.POST.get('contratista')
        herramienta_id = request.POST.get('herramienta')
        fecha_esperada = request.POST.get('fecha_esperada')
        firma_ok = request.POST.get('firma_entrega') == 'on'

        contratista = get_object_or_404(Contratista, id=contratista_id)
        herramienta = get_object_or_404(Herramienta, id=herramienta_id)

        if contratista.bloqueado_por_morosidad:
            messages.error(request, f"DENEGADO: {contratista.nombre_completo} está bloqueado.")
        elif herramienta.estado != 'DISPONIBLE':
            messages.error(request, "DENEGADO: La herramienta no está disponible.")
        elif not firma_ok:
            messages.error(request, "Falta la firma digital del responsable.")
        else:
            with transaction.atomic():
                Prestamo.objects.create(
                    herramienta=herramienta, contratista=contratista,
                    fecha_devolucion_esperada=fecha_esperada, firma_digital_entrega=firma_ok
                )
                herramienta.estado = 'EN_USO'
                herramienta.save()
                messages.success(request, "Préstamo registrado correctamente.")
        return redirect('dashboard')

    # Lógica: Devolver herramienta
    if request.method == 'POST' and 'devolver' in request.POST:
        prestamo_id = request.POST.get('prestamo_id')
        firma_dev = request.POST.get('firma_devolucion') == 'on'
        prestamo = get_object_or_404(Prestamo, id=prestamo_id)

        if not firma_dev:
            messages.error(request, "Se requiere firma para la devolución.")
        else:
            with transaction.atomic():
                prestamo.fecha_devolucion_real = date.today()
                prestamo.firma_digital_devolucion = firma_dev
                prestamo.save()

                herramienta = prestamo.herramienta
                herramienta.estado = 'DISPONIBLE'
                herramienta.save()

                atrasados = Prestamo.objects.filter(
                    contratista=prestamo.contratista,
                    fecha_devolucion_real__isnull=True,
                    fecha_devolucion_esperada__lt=date.today()
                )
                if not atrasados.exists():
                    prestamo.contratista.bloqueado_por_morosidad = False
                    prestamo.contratista.save()
                messages.success(request, "Devolución exitosa. Inventario actualizado.")
        return redirect('dashboard')

    context = {
        'herramientas': Herramienta.objects.all(),
        'prestamos_activos': Prestamo.objects.filter(fecha_devolucion_real__isnull=True),
        'contratistas': Contratista.objects.all(),
        'mantenimientos': Mantenimiento.objects.all().order_by('proxima_fecha_preventiva'),
    }
    return render(request, 'gestion_activos/dashboard.html', context)