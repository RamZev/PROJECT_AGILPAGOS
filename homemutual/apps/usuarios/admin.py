from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

#from apps.usuarios.models.user_models import User
from apps.usuarios.models import User

#-- Esta configuración es para que aparezcan los nuevos campos en el Panel Adm.
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        *BaseUserAdmin.fieldsets,
        (
            'Datos Adicionales',
            {
                'fields': (
                    'email_alt',
                    'telefono',
                ),
            },
        ),
    )

admin.site.register(User, UserAdmin)