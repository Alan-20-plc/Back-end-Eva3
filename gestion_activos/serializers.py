from rest_framework import serializers
from .models import Contratista, Herramienta, Prestamo
from datetime import date

class HerramientaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Herramienta
        fields = '__all__'

class PrestamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestamo
        fields = '__all__'

    def validate(self, data):
        contratista = data.get('contratista')
        herramienta = data.get('herramienta')

        # REGLA 1: Validar si la herramienta está disponible
        if herramienta.estado != 'DISPONIBLE':
            raise serializers.ValidationError("Error: La herramienta no está disponible para préstamo.")

        # REGLA 2: Bloqueo Automático por Morosidad
        prestamos_atrasados = Prestamo.objects.filter(
            contratista=contratista,
            fecha_devolucion_real__isnull=True,
            fecha_devolucion_esperada__lt=date.today()
        )

        if prestamos_atrasados.exists():
            contratista.bloqueado_por_morosidad = True
            contratista.save()
            raise serializers.ValidationError("OPERACIÓN DENEGADA: El contratista está bloqueado por morosidad (tiene préstamos atrasados).")

        if contratista.bloqueado_por_morosidad:
            raise serializers.ValidationError("OPERACIÓN DENEGADA: El contratista se encuentra bloqueado en el sistema.")

        return data