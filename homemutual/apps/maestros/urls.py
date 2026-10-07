# \apps\maestros\urls.py
from django.urls import path

#-- Tablas
# from .views.cuenta_mutual_views import *
from .views.sucursal_views import *
from .views.sg_nacionalidad_views import *
from .views.sg_provincia_views import *
from .views.sg_estado_civil_views import *
from .views.sg_condicion_fiscal_views import *
from .views.sg_ocupacion_views import *
from .views.sg_motivo_pep_views import *
from .views.sg_estado_transaccion_views import *
from .views.socio_views import *
from .views.cuenta_cvu_views import *

#-- NUEVO: Vistas de consultas a APIs externas
from .views.consulta_maestros_views import (
     ConsultarSocioPorCuitView,
     ConsultarSocioPorNumeroDocumentoView,
     HealthCheckView,
     ConsultarExistenciaCuitView,
     ValidarUnicidadEmailView,
     ValidarUnicidadTelefonoView,
 )

urlpatterns = [
	#-- Tablas:
	#-- Cuenta Mutual.
	# path('cuentamutual/', CuentaMutualListView.as_view(), name='cuenta_mutual_list'),
	# path('cuentamutual/nueva/', CuentaMutualCreateView.as_view(), name='cuenta_mutual_create'),
	# path('cuentamutual/<int:pk>/editar/', CuentaMutualUpdateView.as_view(), name='cuenta_mutual_update'),
	# path('cuentamutual/<int:pk>/eliminar/', CuentaMutualDeleteView.as_view(), name='cuenta_mutual_delete'),
	
	#-- Sucursal.
	path('sucursal/', SucursalListView.as_view(), name='sucursal_list'),
	path('sucursal/nueva/', SucursalCreateView.as_view(), name='sucursal_create'),
	path('sucursal/<int:pk>/editar/', SucursalUpdateView.as_view(), name='sucursal_update'),
	path('sucursal/<int:pk>/eliminar/', SucursalDeleteView.as_view(), name='sucursal_delete'),

	#-- Sg Nacionalidad.
    path('sg-nacionalidad/', SgNacionalidadListView.as_view(), name='sg_nacionalidad_list'),
    path('sg-nacionalidad/nueva/', SgNacionalidadCreateView.as_view(), name='sg_nacionalidad_create'),
    path('sg-nacionalidad/<str:pk>/editar/', SgNacionalidadUpdateView.as_view(), name='sg_nacionalidad_update'),
    path('sg-nacionalidad/<str:pk>/eliminar/', SgNacionalidadDeleteView.as_view(), name='sg_nacionalidad_delete'),
    
	#-- Sg Provincia.  
    path('sg-provincia/', SgProvinciaListView.as_view(), name='sg_provincia_list'),
    path('sg-provincia/nueva/', SgProvinciaCreateView.as_view(), name='sg_provincia_create'),
    path('sg-provincia/<str:pk>/editar/', SgProvinciaUpdateView.as_view(), name='sg_provincia_update'),
    path('sg-provincia/<str:pk>/eliminar/', SgProvinciaDeleteView.as_view(), name='sg_provincia_delete'),
    
	 #-- Sg Estado Civil. 
    path('sg-estado-civil/', SgEstadoCivilListView.as_view(), name='sg_estado_civil_list'),
    path('sg-estado-civil/nueva/', SgEstadoCivilCreateView.as_view(), name='sg_estado_civil_create'),
    path('sg-estado-civil/<str:pk>/editar/', SgEstadoCivilUpdateView.as_view(), name='sg_estado_civil_update'),
    path('sg-estado-civil/<str:pk>/eliminar/', SgEstadoCivilDeleteView.as_view(), name='sg_estado_civil_delete'),
    
	#-- Sg Condición Fiscal.
    path('sg-condicion-fiscal/', SgCondicionFiscalListView.as_view(), name='sg_condicion_fiscal_list'),
    path('sg-condicion-fiscal/nueva/', SgCondicionFiscalCreateView.as_view(), name='sg_condicion_fiscal_create'),
    path('sg-condicion-fiscal/<str:pk>/editar/', SgCondicionFiscalUpdateView.as_view(), name='sg_condicion_fiscal_update'),
    path('sg-condicion-fiscal/<str:pk>/eliminar/', SgCondicionFiscalDeleteView.as_view(), name='sg_condicion_fiscal_delete'),
    
	#-- Sg Ocupacion.  ← NUEVO
    path('sg-ocupacion/', SgOcupacionListView.as_view(), name='sg_ocupacion_list'),
    path('sg-ocupacion/nueva/', SgOcupacionCreateView.as_view(), name='sg_ocupacion_create'),
    path('sg-ocupacion/<str:pk>/editar/', SgOcupacionUpdateView.as_view(), name='sg_ocupacion_update'),
    path('sg-ocupacion/<str:pk>/eliminar/', SgOcupacionDeleteView.as_view(), name='sg_ocupacion_delete'),

    #-- Sg Motivo PEP.  ← NUEVO
    path('sg-motivo-pep/', SgMotivoPEPListView.as_view(), name='sg_motivo_pep_list'),
    path('sg-motivo-pep/nueva/', SgMotivoPEPCreateView.as_view(), name='sg_motivo_pep_create'),
    path('sg-motivo-pep/<str:pk>/editar/', SgMotivoPEPUpdateView.as_view(), name='sg_motivo_pep_update'),
    path('sg-motivo-pep/<str:pk>/eliminar/', SgMotivoPEPDeleteView.as_view(), name='sg_motivo_pep_delete'),

    #-- Sg Estado Transaccion.  ← NUEVO
    path('sg-estado-transaccion/', SgEstadoTransaccionListView.as_view(), name='sg_estado_transaccion_list'),
    path('sg-estado-transaccion/nueva/', SgEstadoTransaccionCreateView.as_view(), name='sg_estado_transaccion_create'),
    path('sg-estado-transaccion/<str:pk>/editar/', SgEstadoTransaccionUpdateView.as_view(), name='sg_estado_transaccion_update'),
    path('sg-estado-transaccion/<str:pk>/eliminar/', SgEstadoTransaccionDeleteView.as_view(), name='sg_estado_transaccion_delete'),

    #-- Socio
    path('socio/', SocioListView.as_view(), name='socio_list'),
    path('socio/nueva/', SocioCreateView.as_view(), name='socio_create'),
    path('socio/<int:pk>/editar/', SocioUpdateView.as_view(), name='socio_update'),
    path('socio/<int:pk>/eliminar/', SocioDeleteView.as_view(), name='socio_delete'),
    
    #-- Cuenta CVU
    path('cuenta-cvu/', CuentaCvuListView.as_view(), name='cuenta_cvu_list'),
    path('cuenta-cvu/nueva/', CuentaCvuCreateView.as_view(), name='cuenta_cvu_create'),
    path('cuenta-cvu/<int:pk>/editar/', CuentaCvuUpdateView.as_view(), name='cuenta_cvu_update'),
    path('cuenta-cvu/<int:pk>/eliminar/', CuentaCvuDeleteView.as_view(), name='cuenta_cvu_delete'),
    
    # ================================================================
    # NUEVO: API para consultas a servicios externos
    # ================================================================
    
    # Consultar socio por CUIT
    path('api/consultar-socio/', ConsultarSocioPorCuitView.as_view(), name='consultar_socio_por_cuit'),
    
    # Consultar socio por Número de Documento
    path('api/consultar-socio-documento/', ConsultarSocioPorNumeroDocumentoView.as_view(), name='consultar_socio_por_documento'),
    
    # Health Check de la API de Maasoft
    path('api/health/', HealthCheckView.as_view(), name='api_health_check'),

    # ---- Validaciones de unicidad ----
    path('api/validar-cuit-existencia/', ConsultarExistenciaCuitView.as_view(), name='validar_cuit_existencia'),
    path('api/validar-email/', ValidarUnicidadEmailView.as_view(), name='validar_email'),
    path('api/validar-telefono/', ValidarUnicidadTelefonoView.as_view(), name='validar_telefono'),
]