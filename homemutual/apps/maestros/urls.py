# \apps\maestros\urls.py
from django.urls import path

#-- Tablas
from .views.cuenta_mutual_views import *
from .views.sucursal_views import *

urlpatterns = [
	#-- Tablas:
	#-- Cuenta Mutual.
	path('cuentamutual/', CuentaMutualListView.as_view(), name='cuenta_mutual_list'),
	path('cuentamutual/nueva/', CuentaMutualCreateView.as_view(), name='cuenta_mutual_create'),
	path('cuentamutual/<int:pk>/editar/', CuentaMutualUpdateView.as_view(), name='cuenta_mutual_update'),
	path('cuentamutual/<int:pk>/eliminar/', CuentaMutualDeleteView.as_view(), name='cuenta_mutual_delete'),
	
	#-- Sucursal.
	path('sucursal/', SucursalListView.as_view(), name='sucursal_list'),
	path('sucursal/nueva/', SucursalCreateView.as_view(), name='sucursal_create'),
	path('sucursal/<int:pk>/editar/', SucursalUpdateView.as_view(), name='sucursal_update'),
	path('sucursal/<int:pk>/eliminar/', SucursalDeleteView.as_view(), name='sucursal_delete'),

]