# \apps\maestros\urls.py
from django.urls import path

#-- Tablas
from .views.cuenta_mutual_views import *
from .views.sucursal_views import *
from .views.sg_nacionalidad_views import *
from .views.sg_provincia_views import *
from .views.sg_estado_civil_views import *

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

	#-- Sg Nacionalidad.
    path('sg-nacionalidad/', SgNacionalidadListView.as_view(), name='sg_nacionalidad_list'),
    path('sg-nacionalidad/nueva/', SgNacionalidadCreateView.as_view(), name='sg_nacionalidad_create'),
    path('sg-nacionalidad/<int:pk>/editar/', SgNacionalidadUpdateView.as_view(), name='sg_nacionalidad_update'),
    path('sg-nacionalidad/<int:pk>/eliminar/', SgNacionalidadDeleteView.as_view(), name='sg_nacionalidad_delete'),
    
	#-- Sg Provincia.  
    path('sg-provincia/', SgProvinciaListView.as_view(), name='sg_provincia_list'),
    path('sg-provincia/nueva/', SgProvinciaCreateView.as_view(), name='sg_provincia_create'),
    path('sg-provincia/<int:pk>/editar/', SgProvinciaUpdateView.as_view(), name='sg_provincia_update'),
    path('sg-provincia/<int:pk>/eliminar/', SgProvinciaDeleteView.as_view(), name='sg_provincia_delete'),
    
	 #-- Sg Estado Civil. 
    path('sg-estado-civil/', SgEstadoCivilListView.as_view(), name='sg_estado_civil_list'),
    path('sg-estado-civil/nueva/', SgEstadoCivilCreateView.as_view(), name='sg_estado_civil_create'),
    path('sg-estado-civil/<int:pk>/editar/', SgEstadoCivilUpdateView.as_view(), name='sg_estado_civil_update'),
    path('sg-estado-civil/<int:pk>/eliminar/', SgEstadoCivilDeleteView.as_view(), name='sg_estado_civil_delete'),
]