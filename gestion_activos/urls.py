from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import HerramientaViewSet, PrestamoViewSet
from . import views

# El DefaultRouter crea automáticamente todas las rutas GET, POST, PUT y DELETE
router = DefaultRouter()
router.register(r'herramientas', HerramientaViewSet)
router.register(r'prestamos', PrestamoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Nuevos endpoints para la barra lateral
    path('inventario/', views.inventario_view, name='inventario'),
    path('personal/', views.personal_view, name='personal'),
    path('mantenimientos/', views.mantenimientos_view, name='mantenimientos'),
    path('reportes/', views.reportes_view, name='reportes'),
]