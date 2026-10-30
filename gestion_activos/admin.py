from django.contrib import admin
from .models import Contratista, Herramienta, Prestamo, Mantenimiento

@admin.register(Contratista)
class ContratistaAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre_completo', 'empresa', 'telefono', 'bloqueado_por_morosidad')
    list_filter = ('bloqueado_por_morosidad', 'empresa')
    search_fields = ('rut', 'nombre_completo')

@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    # Columnas que se verán en la tabla principal
    list_display = ('codigo_inventario', 'nombre', 'marca', 'estado')
    # Panel lateral para filtrar rápido
    list_filter = ('estado', 'marca')
    # Barra de búsqueda superior
    search_fields = ('codigo_inventario', 'nombre')

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('herramienta', 'contratista', 'fecha_entrega', 'fecha_devolucion_esperada', 'fecha_devolucion_real')
    list_filter = ('firma_digital_entrega', 'firma_digital_devolucion')
    search_fields = ('herramienta__nombre', 'contratista__nombre_completo')
    # Ordenar para que los préstamos más recientes salgan primero
    ordering = ('-fecha_entrega',)

@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ('herramienta', 'fecha_inicio', 'fecha_fin', 'proxima_fecha_preventiva')
    list_filter = ('fecha_inicio',)
    search_fields = ('herramienta__nombre', 'descripcion_falla')