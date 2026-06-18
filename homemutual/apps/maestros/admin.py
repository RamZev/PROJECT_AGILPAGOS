# neumatic\apps\maestros\apps.py
from django.contrib import admin

from .models.cuenta_mutual_models import CuentaMutual
from .models.sucursal_models import Sucursal
from .models.sg_catalogo_models import SgEntidadTipoDocumento, SgTipoPersona, SgTipoCuenta

# Registramos los modelos independientes
admin.site.register(CuentaMutual)
admin.site.register(Sucursal)
admin.site.register(SgEntidadTipoDocumento)
admin.site.register(SgTipoPersona)
admin.site.register(SgTipoCuenta)

