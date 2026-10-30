from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from gestion_activos.views import dashboard, login_usuario, registro_usuario, logout_usuario

schema_view = get_schema_view(
   openapi.Info(title="BuildCorp API", default_version='v1', description="API BuildCorp"),
   public=True, permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('login/', login_usuario, name='login'),
    path('registro/', registro_usuario, name='registro'),
    path('logout/', logout_usuario, name='logout'),
    path('api/', include('gestion_activos.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]