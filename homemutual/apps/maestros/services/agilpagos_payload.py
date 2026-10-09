# apps/maestros/services/agilpagos_payload.py
"""
Servicio para construir el payload de alta de Usuario + CVU en Agilpagos.
Combina: datos del Socio + datos de la CuentaCvu + constantes.
"""
import logging
from datetime import date

from apps.maestros.models.sg_catalogo_models import SgConstanteAgilpagos

logger = logging.getLogger(__name__)


# ============================================================
# VALORES POR DEFECTO (fallback si no están en SgConstanteAgilpagos)
# ============================================================
DEFAULT_CONSTANTES = {
    'ID_TIPO_DOCUMENTO_DNI': '209C1CAA-C56D-4E03-BB40-E9EF2F319A3F',
    'ID_TIPO_PERSONA_FISICA': '20EB9127-7CA8-49E0-9E0B-CA8293218ACA',
    'ID_TIPO_CUENTA_CVU': 'D2483A34-78BE-40A2-B8CB-07AD4BCF6F61',
    'ID_ENTIDAD_TIPO_DOCUMENTO': 'CAE2882B-493C-4E1A-A6E7-B5E2BD25F808',
    'ID_NACIONALIDAD_PAIS_DOMICILIO_AR': '76B19E61-B8DC-40F4-BFAB-422CBFFE5002',
}


def get_constante(clave, default=''):
    """Lee una constante de SgConstanteAgilpagos."""
    try:
        return SgConstanteAgilpagos.objects.get(clave=clave).valor
    except SgConstanteAgilpagos.DoesNotExist:
        logger.warning(f"Constante '{clave}' no encontrada. Usando default.")
        return DEFAULT_CONSTANTES.get(clave, default)


def build_constantes_payload():
    """Construye el bloque de constantes para el payload."""
    return {
        "idTipoDocumento": get_constante('ID_TIPO_DOCUMENTO_DNI'),
        "idTipoPersona": get_constante('ID_TIPO_PERSONA_FISICA'),
        "idTipoCuenta": get_constante('ID_TIPO_CUENTA_CVU'),
        "idEntidadTipoDocumento": get_constante('ID_ENTIDAD_TIPO_DOCUMENTO'),
        "idPaisDomicilio": get_constante(
            'ID_NACIONALIDAD_PAIS_DOMICILIO_AR',
            '76B19E61-B8DC-40F4-BFAB-422CBFFE5002',
        ),
    }


def build_alta_payload(socio, cuenta_cvu):
    """
    Construye el JSON completo de alta de Usuario + CVU para Agilpagos.

    Combina:
    - Datos del Socio (método to_agilpagos_payload_usuario).
    - Datos de la CuentaCvu (método to_agilpagos_payload_cvu).
    - Constantes (desde SgConstanteAgilpagos).
    - Fecha de alta: hoy.

    Returns:
        dict: payload listo para enviar al endpoint /onboarding/usuario/alta.
    """
    # 1. Constantes
    constantes = build_constantes_payload()

    # 2. Datos del Socio
    datos_socio = socio.to_agilpagos_payload_usuario()

    # 3. Datos de la CVU
    datos_cvu = cuenta_cvu.to_agilpagos_payload_cvu()

    # 4. Fecha de alta: HOY
    datos_fecha = {
        "fechaAlta": date.today().isoformat(),
    }

    # 5. Fusión: los últimos pisan a los anteriores si hay claves duplicadas
    payload = {
        **datos_socio,
        **datos_cvu,
        **constantes,
        **datos_fecha,
    }

    # 6. Limpiar campos con valor None
    payload = {k: v for k, v in payload.items() if v is not None}

    logger.info(f"Payload construido para CuentaCvu {cuenta_cvu.pk}: {list(payload.keys())}")
    return payload