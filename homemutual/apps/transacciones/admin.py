from django.contrib import admin


from .models.transacciones_models import CashoutRequest

# Registramos los modelos independientes
admin.site.register(CashoutRequest)

