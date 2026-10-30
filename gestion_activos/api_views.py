from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from datetime import date
from .models import Herramienta, Prestamo
from .serializers import HerramientaSerializer, PrestamoSerializer

class HerramientaViewSet(viewsets.ModelViewSet):
    queryset = Herramienta.objects.all()
    serializer_class = HerramientaSerializer

class PrestamoViewSet(viewsets.ModelViewSet):
    queryset = Prestamo.objects.all()
    serializer_class = PrestamoSerializer

    def perform_create(self, serializer):
        # Al crear un préstamo, la herramienta pasa a "EN USO"
        with transaction.atomic():
            prestamo = serializer.save()
            herramienta = prestamo.herramienta
            herramienta.estado = 'EN_USO'
            herramienta.save()

    # Endpoint personalizado para devolver la herramienta
    @action(detail=True, methods=['post'])
    def devolver(self, request, pk=None):
        prestamo = self.get_object()
        
        if prestamo.fecha_devolucion_real:
            return Response({"error": "Esta herramienta ya fue devuelta."}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # 1. Registrar devolución y firma digital
            prestamo.fecha_devolucion_real = date.today()
            prestamo.firma_digital_devolucion = True
            prestamo.save()

            # 2. Volver a dejar la herramienta DISPONIBLE
            herramienta = prestamo.herramienta
            herramienta.estado = 'DISPONIBLE'
            herramienta.save()

            # 3. Revisar si hay que desbloquear al contratista
            contratista = prestamo.contratista
            prestamos_atrasados = Prestamo.objects.filter(
                contratista=contratista,
                fecha_devolucion_real__isnull=True,
                fecha_devolucion_esperada__lt=date.today()
            )
            if not prestamos_atrasados.exists():
                contratista.bloqueado_por_morosidad = False
                contratista.save()

        return Response({"status": "Herramienta devuelta exitosamente. Estado actualizado a DISPONIBLE."})