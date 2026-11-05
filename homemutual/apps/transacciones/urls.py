# apps/transacciones/urls.py
from django.urls import path

from .views.transferencia_views import (
	TransferenciaListView,
	TransferenciaCreateView,
	api_movimientos_cvu,
)
from .api import views as api_views


urlpatterns = [
	path('transferencia/', TransferenciaListView.as_view(), name='transferencia_list'),
	path('transferencia/nueva/', TransferenciaCreateView.as_view(), name='transferencia_create'),
	path('api/movimientos/', api_movimientos_cvu, name='api_movimientos_cvu'),
	
    #-- Endpoints JSON (proxy a la API Intermedia).
    path('api/cvus-propias/', api_views.api_cvus_propias, name='api_cvus_propias'),
    path('api/buscar-destinatario/', api_views.api_buscar_destinatario, name='api_buscar_destinatario'),
    path('api/solicitar-transferencia/', api_views.api_solicitar_transferencia, name='api_solicitar_transferencia'),
	path('api/buscar-por-alias/', api_views.api_buscar_por_alias, name='api_buscar_por_alias'),
]