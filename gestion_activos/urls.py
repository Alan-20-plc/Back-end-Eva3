from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import HerramientaViewSet, PrestamoViewSet

# El DefaultRouter crea automáticamente todas las rutas GET, POST, PUT y DELETE
router = DefaultRouter()
router.register(r'herramientas', HerramientaViewSet)
router.register(r'prestamos', PrestamoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]