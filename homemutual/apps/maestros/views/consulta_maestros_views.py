# apps/maestros/views/consulta_maestros_views.py
"""
Vistas para consultas a APIs externas y servicios de maestros.
Usa el cliente de Agilpagos con JWT basado en credenciales de sesión.
"""
import logging

import httpx
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from ..models.socio_models import Socio
from ..services.agilpagos_client import (
    agilpagos_get,
    CredentialsNotInSession,
    _token_cache,
)

logger = logging.getLogger(__name__)


# ================================================================
# MAPEOS DE CÓDIGOS DE AGILPAGOS A GUIDs DE CATÁLOGOS
# ================================================================

# Mapeo: Sexo de Agilpagos → campo genero del modelo
GENERO_MAP = {
    'M': 'M',
    'F': 'F',
    'X': 'X',
}

# Mapeo: Estado Civil código → GUID SgEstadoCivil
ESTADO_CIVIL_MAP = {
    'S': 'b2b68f22-e903-4303-a4c3-713d2fe67785',  # Soltero
    'C': '13e36b73-183f-4575-8d18-5c94543d2e07',  # Casado
    'D': 'a2dc98b4-49bf-40a5-be97-e7e3e5decb2c',  # Divorciado
    'V': '868f94c9-f9c0-4701-8173-30376584497a',  # Viudo
    'U': '',                                       # Unión civil (a definir)
}

# Mapeo: Condición Fiscal código → GUID SgCondicionFiscal
CONDICION_FISCAL_MAP = {
    'CF': 'ba933f3f-d18e-4aed-8585-dfa73e27da11',  # Consumidor Final
    'RI': 'f0ea813a-e3e7-4eae-ba1d-02b3917ca59a',  # Responsable Inscripto
    'RNI': '0a98394f-0453-4f3d-b51f-9b59b5a2b963', # Responsable No Inscripto
    'EXE': '60d88f7f-23fa-4884-9814-0371e4f60323',  # Exento
    'RMT': '6c1a3604-63c7-44a5-b66c-17c6cb4266ab', # Monotributista
}

# Mapeo: Tipo Documento → GUID SgEntidadTipoDocumento
TIPO_DOCUMENTO_MAP = {
    'DNI': '209C1CAA-C56D-4E03-BB40-E9EF2F319A3F',
    # Otros tipos a definir según catálogo Agilpagos
}

# Mapeo: Nacionalidad texto → GUID SgNacionalidad
NACIONALIDAD_MAP = {
    'ARGENTINA': '76b19e61-b8dc-40f4-bfab-422cbffe5002',
    # Otras a definir
}


# ================================================================
# MANEJO COMÚN DE ERRORES
# ================================================================
def _error_response(request, exc):
    """Convierte una excepción del cliente de Agilpagos en una JsonResponse."""
    if isinstance(exc, CredentialsNotInSession):
        return JsonResponse({
            'success': False,
            'error': 'Sesión sin credenciales de Agilpagos. Vuelva a iniciar sesión.',
        }, status=401)

    if isinstance(exc, httpx.TimeoutException):
        return JsonResponse({
            'success': False,
            'error': 'Tiempo de espera agotado al conectar con Agilpagos.',
        }, status=408)

    if isinstance(exc, httpx.ConnectError):
        return JsonResponse({
            'success': False,
            'error': 'Error de conexión con Agilpagos.',
        }, status=503)

    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code == 401:
            username = request.session.get('agilpagos_username')
            if username:
                _token_cache.invalidate(username)
            request.session.pop('agilpagos_password', None)
            return JsonResponse({
                'success': False,
                'error': 'Credenciales de Agilpagos inválidas. Vuelva a iniciar sesión.',
            }, status=401)
        if exc.response.status_code == 502:
            return JsonResponse({
                'success': False,
                'error': 'El servidor de Agilpagos está temporalmente fuera de servicio.',
            }, status=503)
        logger.warning(f"Agilpagos respondió {exc.response.status_code}: {exc.response.text[:200]}")
        return JsonResponse({
            'success': False,
            'error': f'Error {exc.response.status_code} de Agilpagos.',
        }, status=502)

    logger.exception("Error inesperado consultando Agilpagos")
    return JsonResponse({
        'success': False,
        'error': 'Error interno.',
    }, status=500)


# ================================================================
# CONSULTAS A LA API DE AGILPAGOS
# ================================================================

@method_decorator(login_required, name='dispatch')
class ConsultarSocioPorCuitView(View):
    """
    Consulta los datos de un socio por CUIT en la API de Agilpagos.
    Endpoint: /maestros/api/consultar-socio/?cuit=20207882950
    Endpoint Agilpagos: GET /maasoft/socio/{cuit}
    """

    def get(self, request, *args, **kwargs):
        cuit = request.GET.get('cuit', '').strip()
        if not cuit or not cuit.isdigit() or len(cuit) != 11:
            return JsonResponse({'success': False, 'error': 'CUIT inválido'}, status=400)

        try:
            response = agilpagos_get(request, f"/maasoft/socio/{cuit}")
        except Exception as e:
            return _error_response(request, e)

        if response.status_code == 200:
            data = response.json()
            # Verificar si hay datos válidos
            if not data or (isinstance(data, dict) and not data.get('CUIT')):
                return JsonResponse(
                    {'success': False, 'error': 'No se encontró el socio en Agilpagos'},
                    status=404,
                )
            return JsonResponse({'success': True, 'data': self._procesar_datos_socio(data)})

        if response.status_code == 404:
            return JsonResponse(
                {'success': False, 'error': 'No se encontró el socio en Agilpagos'},
                status=404,
            )

        return JsonResponse(
            {'success': False, 'error': f'Error {response.status_code} de Agilpagos'},
            status=response.status_code,
        )

    def _procesar_datos_socio(self, data):
        """
        Adapta la respuesta de Agilpagos al formato que espera el frontend.

        Estructura de Agilpagos (endpoint /maasoft/socio/{cuit}):
        {
          "Codigo": 4084,
          "Apellido": "CHAVEZ",
          "Nombre": "MAIRA DAIANA",
          "Sucursal": 1,
          "Sexo": "F",
          "Domicilio": "ITALIA 1050",
          "Codigo Postal": 2240,
          "CUIT": 27356537098,
          ...
        }
        """
        if not isinstance(data, dict):
            return {}

        # Valores raw
        codigo = data.get('Codigo')
        apellido = (data.get('Apellido') or '').strip()
        nombre = (data.get('Nombre') or '').strip()
        sucursal = data.get('Sucursal')
        sexo = (data.get('Sexo') or '').strip().upper()
        domicilio = (data.get('Domicilio') or '').strip()
        cp = data.get('Codigo Postal')
        cuit = data.get('CUIT')
        tipo_doc = (data.get('Tipo Documento') or '').strip().upper()
        nro_doc = data.get('Numero Documento')
        estado_civil = (data.get('Estado Civil') or '').strip().upper()
        cond_fiscal = (data.get('Condicion Fiscal') or '').strip().upper()
        uif = data.get('Sujeto Obligado UIF')
        fecha_nac = data.get('Fecha Nacimiento') or ''
        fecha_ing = data.get('Fecha Ingreso') or ''
        es_pep = (data.get('Es PEP') or 'N').strip().upper() == 'S'
        nacionalidad = (data.get('Nacionalidad') or '').strip().upper()
        telefono = (data.get('Telefono') or '').strip()
        movil = (data.get('Movil') or '').strip()
        email = (data.get('e-Mail') or '').strip()
        codigo_actividad = data.get('Codigo Actividad')

        # Desglosar el domicilio "CALLE 1234" → calle + altura
        calle, altura = self._desglosar_domicilio(domicilio)

        # Desglosar teléfono
        telefono_raw = telefono or movil
        codigo_area, numero_tel = self._desglosar_telefono(telefono_raw)

        return {
            # Datos internos
            'id_socio': str(codigo) if codigo else '',
            'sucursal': str(sucursal) if sucursal else '',

            # Personales
            'apellido': apellido,
            'nombre': nombre,
            'genero': GENERO_MAP.get(sexo, ''),
            'fecha_nacimiento': fecha_nac,

            # Documento
            'numero_documento': str(nro_doc) if nro_doc else '',
            'cuit': str(cuit) if cuit else '',
            'tipo_documento': TIPO_DOCUMENTO_MAP.get(tipo_doc, ''),

            # Contacto
            'email': email,
            'telefono': telefono_raw,
            'movil': movil,
            'codigo_area': codigo_area,
            'numero_telefono': numero_tel,

            # Domicilio
            'domicilio': domicilio,
            'calle': calle,
            'altura': altura,
            'codigo_postal': str(cp) if cp else '',

            # Fiscal
            'estado_civil': ESTADO_CIVIL_MAP.get(estado_civil, ''),
            'condicion_fiscal': CONDICION_FISCAL_MAP.get(cond_fiscal, ''),
            'es_pep': es_pep,
            'sujeto_obligado_uif': uif if uif else '',

            # Nacionalidad
            'nacionalidad': NACIONALIDAD_MAP.get(nacionalidad, ''),

            # Fechas
            'fecha_ingreso': fecha_ing,

            # Código actividad (para mapear a ocupación si aplica)
            'codigo_actividad': codigo_actividad,
        }

    def _desglosar_domicilio(self, domicilio):
        """
        Parsea 'CALLE 1234' o 'AV. SIEMPREVIVA 742' → (calle, altura).
        Ejemplos:
          'ITALIA 1050' → ('ITALIA', '1050')
          'AV. CORRIENTES 1234' → ('AV. CORRIENTES', '1234')
          'SIN NUMERO' → ('SIN NUMERO', '')
        """
        if not domicilio:
            return '', ''
        partes = domicilio.rsplit(' ', 1)
        if len(partes) == 2 and partes[1].strip().isdigit():
            return partes[0].strip(), partes[1].strip()
        return domicilio.strip(), ''

    def _desglosar_telefono(self, telefono):
        """
        Desglosa un teléfono en (código_area, número).
        Formato esperado: 10 dígitos (ej: '3483456789') → ('3483', '456789').
        """
        if not telefono:
            return '', ''
        limpio = ''.join(c for c in str(telefono) if c.isdigit())
        if len(limpio) == 10:
            return limpio[:4], limpio[4:]
        return '', limpio


@method_decorator(login_required, name='dispatch')
class ConsultarExistenciaCuitView(View):
    """
    Verifica si un CUIT existe en Agilpagos.
    Endpoint: /maestros/api/validar-cuit-existencia/?cuit=27356537098
    Endpoint Agilpagos: GET /maasoft/socio/verificar/{cuit}
    """

    def get(self, request, *args, **kwargs):
        cuit = request.GET.get('cuit', '').strip()
        if not cuit or not cuit.isdigit() or len(cuit) != 11:
            return JsonResponse({'success': False, 'error': 'CUIT inválido'}, status=400)

        try:
            response = agilpagos_get(request, f"/maasoft/socio/verificar/{cuit}")
        except Exception as e:
            return _error_response(request, e)

        if response.status_code == 200:
            data = response.json()
            # Interpretar la respuesta: si viene el CUIT y datos, existe
            if isinstance(data, dict) and data.get('CUIT'):
                return JsonResponse({'exists': True, 'data': data})
            if isinstance(data, bool):
                return JsonResponse({'exists': data})
            if isinstance(data, str):
                # Puede venir "Existe" o "No existe"
                existe = 'no' not in data.lower()
                return JsonResponse({'exists': existe, 'detail': data})
            return JsonResponse({'exists': False, 'detail': 'No registrado'})

        return JsonResponse(
            {'exists': False, 'detail': f'Error {response.status_code}'},
            status=response.status_code,
        )


@method_decorator(login_required, name='dispatch')
class ConsultarSocioPorNumeroDocumentoView(View):
    """
    Consulta los datos de un socio por número de documento.
    ⚠️ No hay endpoint confirmado en Agilpagos para esto.
    Se mantiene como stub por si se agrega.
    """

    def get(self, request, *args, **kwargs):
        documento = request.GET.get('documento', '').strip()
        if not documento or not documento.isdigit():
            return JsonResponse({'success': False, 'error': 'Documento inválido'}, status=400)

        # TODO: Implementar cuando exista el endpoint en Agilpagos
        return JsonResponse({
            'success': False,
            'error': 'Endpoint no disponible aún.',
        }, status=501)


@method_decorator(login_required, name='dispatch')
class HealthCheckView(View):
    """Chequeo de estado de la API de Agilpagos."""
    def get(self, request, *args, **kwargs):
        try:
            response = agilpagos_get(request, "/maasoft/socio/verificar/27356537098")
            return JsonResponse({
                'success': True,
                'status': 'OK',
                'api_status': 'online' if response.status_code in (200, 404) else 'offline',
                'status_code': response.status_code,
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'status': 'ERROR',
                'api_status': 'offline',
                'error': str(e),
            }, status=503)


# ================================================================
# VALIDACIONES DE UNICIDAD (locales, sobre el modelo Socio)
# ================================================================

@method_decorator(login_required, name='dispatch')
class ValidarUnicidadEmailView(View):
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email', '').strip()
        exclude_pk = request.GET.get('exclude', '').strip()
        if not email:
            return JsonResponse({'exists': False, 'error': 'Email requerido'}, status=400)
        qs = Socio.objects.filter(email__iexact=email)
        if exclude_pk and exclude_pk.isdigit():
            qs = qs.exclude(pk=int(exclude_pk))
        return JsonResponse({'exists': qs.exists()})


@method_decorator(login_required, name='dispatch')
class ValidarUnicidadTelefonoView(View):
    def get(self, request, *args, **kwargs):
        telefono = request.GET.get('numero_telefono', '').strip()
        exclude_pk = request.GET.get('exclude', '').strip()
        if not telefono:
            return JsonResponse({'exists': False, 'error': 'Teléfono requerido'}, status=400)
        qs = Socio.objects.filter(numero_telefono=telefono)
        if exclude_pk and exclude_pk.isdigit():
            qs = qs.exclude(pk=int(exclude_pk))
        return JsonResponse({'exists': qs.exists()})