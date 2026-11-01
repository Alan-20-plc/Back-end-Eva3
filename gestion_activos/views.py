from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from datetime import date
from .models import Herramienta, Prestamo, Contratista, Mantenimiento
from django.contrib.auth.models import User

# --- SISTEMA DE AUTENTICACIÓN ---

def registro_usuario(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('username')
        correo = request.POST.get('email')
        contrasena = request.POST.get('password')
        
        if nombre_usuario and correo and contrasena:
            User.objects.create_user(username=nombre_usuario, email=correo, password=contrasena)
            return redirect('login')
            
    return render(request, 'gestion_activos/registro.html')
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
def inventario_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            Herramienta.objects.create(nombre=nombre)
        return redirect('inventario')
        
    herramientas = Herramienta.objects.all()
    return render(request, 'gestion_activos/inventario.html', {'herramientas': herramientas})

def personal_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            Contratista.objects.create(nombre=nombre)
        return redirect('personal')
        
    contratistas = Contratista.objects.all()
    return render(request, 'gestion_activos/personal.html', {'contratistas': contratistas})

def mantenimientos_view(request):
    # 1. Si el administrador hace clic en "Guardar Registro" en la ventana emergente
    if request.method == 'POST':
        herramienta_id = request.POST.get('herramienta_id')
        fecha = request.POST.get('fecha_programada')
        
        # Busca la herramienta en la BD y crea el mantenimiento
        herramienta = Herramienta.objects.get(id=herramienta_id)
        Mantenimiento.objects.create(
            herramienta=herramienta,
            fecha_programada=fecha
        )
        return redirect('mantenimientos') # Recarga la página para mostrar el nuevo dato

    # 2. Si solo está visitando la página (Carga normal)
    mantenimientos = Mantenimiento.objects.all()
    herramientas = Herramienta.objects.all() # Lo enviamos para llenar el menú desplegable
    return render(request, 'gestion_activos/mantenimientos.html', {
        'mantenimientos': mantenimientos,
        'herramientas': herramientas
    })

def reportes_view(request):
    prestamos = Prestamo.objects.all()
    return render(request, 'gestion_activos/reportes.html', {'prestamos': prestamos})