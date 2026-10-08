# homemutual\apps\maestros\services\socio_service.py
"""
Servicios para el modelo Socio.
Incluye la creación del User de Django asociado.
"""
import logging

from django.db import transaction
from django.core.exceptions import ValidationError

from apps.usuarios.models import User

logger = logging.getLogger(__name__)


# Password por defecto (solo para desarrollo/pruebas)
DEFAULT_SOCIO_PASSWORD = "user321$$"


def crear_usuario_para_socio(socio, password=None):
    """
    Crea un User de Django asociado al Socio.
    - username = email del Socio
    - password por defecto o la que se pase
    Retorna el User creado.
    """
    if socio.id_user:
        return socio.id_user

    if not socio.email:
        raise ValidationError("El Socio no tiene email, no se puede crear el User.")

    username = socio.email.lower().strip()

    if User.objects.filter(username=username).exists():
        raise ValidationError(
            f"Ya existe un User con el username '{username}'."
        )

    # Crear el User
    user = User.objects.create_user(
        username=username,
        email=socio.email.lower().strip(),
        password=password or DEFAULT_SOCIO_PASSWORD,
        first_name=(socio.nombre or '')[:150],
        last_name=(socio.apellido or '')[:150],
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )

    # Teléfono (concatenado si existe)
    telefono_completo = (
        f"{socio.caracteristica_pais or ''}"
        f"{socio.codigo_area or ''}"
        f"{socio.numero_telefono or ''}"
    )[:15]
    if telefono_completo:
        user.telefono = telefono_completo
        user.save(update_fields=['telefono'])

    logger.info(f"User creado para Socio {socio.pk}: {user.username}")
    return user


@transaction.atomic
def crear_socio_con_usuario(socio, password=None):
    """
    Crea el User y lo asocia al Socio.
    Si algo falla, se revierte toda la transacción.
    """
    user = crear_usuario_para_socio(socio, password=password)
    socio.id_user = user
    socio.save(update_fields=['id_user'])
    return socio