# apps/consultas/urls.py
from django.urls import path
from .views.consulta_cvu_views import ConsultaCvuPorCuitView
from .views.cuenta_cvu_views import MisCuentasCvuView


urlpatterns = [
    # path('', consulta_cvu_views.ConsultaCvuPorCuitView.as_view(), name='consulta_cvu_por_cuit'),
    path('cvu-por-cuit/', ConsultaCvuPorCuitView.as_view(), name='consulta_cvu_por_cuit'),
	
	path('mis-cuentas-cvu/', MisCuentasCvuView.as_view(), name='mis_cuentas_cvu'),
]