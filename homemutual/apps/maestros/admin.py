# neumatic\apps\maestros\apps.py
from django.contrib import admin

from .models.sucursal_models import Sucursal
from .models.sg_catalogo_models import (SgEntidadTipoDocumento, 
                                        SgTipoPersona, 
                                        SgTipoCuenta,
                                        SgMotivoPEP)

# Registramos los modelos independientes
admin.site.register(Sucursal)
admin.site.register(SgEntidadTipoDocumento)
admin.site.register(SgTipoPersona)
admin.site.register(SgTipoCuenta)
admin.site.register(SgMotivoPEP)


