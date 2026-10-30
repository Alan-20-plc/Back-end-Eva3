from django.db import models
from django.utils import timezone

class Contratista(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre_completo = models.CharField(max_length=150)
    empresa = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    # Fundamental para el requerimiento: "bloqueo automático de contratistas morosos"
    bloqueado_por_morosidad = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.nombre_completo} - {self.empresa}"

class Herramienta(models.Model):
    # Opciones estrictas requeridas por el caso de estudio
    ESTADOS_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('EN_USO', 'En Uso'),
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('DADO_DE_BAJA', 'Dado de Baja'),
    ]
    
    codigo_inventario = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='DISPONIBLE')
    fecha_adquisicion = models.DateField(default=timezone.now)

    def __str__(self):
        return f"[{self.codigo_inventario}] {self.nombre} - {self.estado}"

class Prestamo(models.Model):
    herramienta = models.ForeignKey(Herramienta, on_delete=models.RESTRICT)
    contratista = models.ForeignKey(Contratista, on_delete=models.RESTRICT)
    fecha_entrega = models.DateField(default=timezone.now)
    fecha_devolucion_esperada = models.DateField()
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    
    # Requerimiento: Módulo de entrega/devolución con firma digital
    firma_digital_entrega = models.BooleanField(default=False, help_text="Firmado al entregar")
    firma_digital_devolucion = models.BooleanField(default=False, help_text="Firmado al devolver")

    def __str__(self):
        return f"Préstamo: {self.herramienta.nombre} a {self.contratista.nombre_completo}"

class Mantenimiento(models.Model):
    herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True)
    descripcion_falla = models.TextField()
    
    # Requerimiento: Programación de mantenimientos preventivos
    proxima_fecha_preventiva = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Mantenimiento de {self.herramienta.nombre} ({self.fecha_inicio})"