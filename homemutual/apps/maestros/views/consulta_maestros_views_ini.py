# apps/maestros/views/consulta_maestros_views.py
"""
Vistas para consultas a APIs externas y servicios de maestros
"""
import requests
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings
# from ..models.cuenta_mutual_models import CuentaMutual

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class ConsultarSocioPorCuitView(View):
    """
    Vista para consultar los datos de un socio por CUIT
    Endpoint: /maestros/api/consultar-socio/?cuit=20207882950
    Consume la API de Maasoft para obtener los datos del socio
    """
    API_BASE_URL = 'http://186.189.231.237:8081/maasoft'
    TIMEOUT = 10

    def get(self, request, *args, **kwargs):
        cuit = request.GET.get('cuit', '').strip()
        if not cuit or not cuit.isdigit() or len(cuit) != 11:
            return JsonResponse({'success': False, 'error': 'CUIT inválido'}, status=400)

        try:
            data = self._consultar_api(cuit)
            if data:
                response_data = self._procesar_datos_socio(data)
                return JsonResponse({'success': True, 'data': response_data})
            else:
                return JsonResponse({'success': False, 'error': 'No se encontró el socio'}, status=404)
        except requests.exceptions.Timeout:
            return JsonResponse({'success': False, 'error': 'Tiempo de espera agotado'}, status=408)
        except requests.exceptions.ConnectionError:
            return JsonResponse({'success': False, 'error': 'Error de conexión'}, status=503)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Error interno'}, status=500)

    def _consultar_api(self, cuit):
        url = f"{self.API_BASE_URL}/socio/{cuit}"
        headers = {'accept': 'application/json', 'User-Agent': 'MutualApp/1.0'}
        response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _procesar_datos_socio(self, data):
        # nombre_completo = data.get('Nombre', '')
        # apellido, nombre = self._desglosar_nombre(nombre_completo)
        return {
            'cuit': data.get('CUIT', ''),
            'apellido': data.get('Apellido', ''),      # ← usar directamente
            'nombre': data.get('Nombre', ''),          # ← usar directamente
            'genero': self._mapear_genero(data.get('Sexo', '')),
            'fecha_nacimiento': data.get('Fecha Nacimiento', ''),
            'numero_documento': str(data.get('Numero Documento', '')),
            'tipo_documento': data.get('Tipo Documento', ''),
            'email': data.get('e-Mail', ''),
            'telefono': data.get('Telefono', '') or data.get('Movil', ''),
            'telefono_2': data.get('Telefono 2', ''),
            'movil': data.get('Movil', ''),
            'id_socio': data.get('Codigo', ''),
            'sucursal': data.get('Sucursal', ''),
            'domicilio': data.get('Domicilio', ''),
            'codigo_postal': data.get('Codigo Postal', ''),
            'estado_civil': self._mapear_estado_civil(data.get('Estado Civil', '')),
            'condicion_fiscal': self._mapear_condicion_fiscal(data.get('Condicion Fiscal', '')),
            'es_pep': data.get('Es PEP', 'N') == 'S',
            'sujeto_obligado_uif': data.get('Sujeto Obligado UIF', ''),
            'nacionalidad': data.get('Nacionalidad', ''),
            'residente': data.get('Residente', ''),
            'codigo_actividad': data.get('Codigo Actividad', ''),
            'fecha_ingreso': data.get('Fecha Ingreso', ''),
        }

    def _desglosar_nombre(self, nombre_completo):
        if not nombre_completo:
            return '', ''
        if ',' in nombre_completo:
            partes = nombre_completo.split(',', 1)
            return partes[0].strip(), partes[1].strip() if len(partes) > 1 else ''
        return '', nombre_completo.strip()

    def _mapear_genero(self, codigo):
        mapa = {'M': 'M', 'F': 'F', 'X': 'X'}
        return mapa.get(codigo, '')

    def _mapear_estado_civil(self, codigo):
        # mapa = {'S': 'Soltero', 'C': 'Casado', 'D': 'Divorciado', 'V': 'Viudo', 'U': 'Unión civil'}
        # return mapa.get(codigo, '')
        return codigo

    def _mapear_condicion_fiscal(self, codigo):
        # mapa = {'CF': 'Consumidor Final', 'RI': 'IVA Responsable Inscripto', 
        #         'RNI': 'IVA Responsable no Inscripto', 'MT': 'Responsable Monotributo',
        #         'EX': 'IVA Sujeto Exento'}
        # return mapa.get(codigo, '')
        return codigo

@method_decorator(login_required, name='dispatch')
class ConsultarSocioPorNumeroDocumentoView(View):
    API_BASE_URL = 'http://186.189.231.237:8081/maasoft'
    TIMEOUT = 10

    def get(self, request, *args, **kwargs):
        documento = request.GET.get('documento', '').strip()
        if not documento or not documento.isdigit():
            return JsonResponse({'success': False, 'error': 'Documento inválido'}, status=400)

        try:
            url = f"{self.API_BASE_URL}/socio/documento/{documento}"
            headers = {'accept': 'application/json', 'User-Agent': 'MutualApp/1.0'}
            response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if data:
                return JsonResponse({'success': True, 'data': self._procesar_datos_socio(data)})
            return JsonResponse({'success': False, 'error': 'No encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def _procesar_datos_socio(self, data):
        # similar al método anterior
        nombre_completo = data.get('Nombre', '')
        apellido, nombre = self._desglosar_nombre(nombre_completo)
        return {
            'cuit': data.get('CUIT', ''),
            'apellido': apellido,
            'nombre': nombre,
            'genero': self._mapear_genero(data.get('Sexo', '')),
            'fecha_nacimiento': data.get('Fecha Nacimiento', ''),
            'numero_documento': str(data.get('Numero Documento', '')),
            'tipo_documento': data.get('Tipo Documento', ''),
            'email': data.get('e-Mail', ''),
            'telefono': data.get('Telefono', '') or data.get('Movil', ''),
            'telefono_2': data.get('Telefono 2', ''),
            'movil': data.get('Movil', ''),
            'id_socio': data.get('Codigo', ''),
            'sucursal': data.get('Sucursal', ''),
            'domicilio': data.get('Domicilio', ''),
            'codigo_postal': data.get('Codigo Postal', ''),
            'estado_civil': self._mapear_estado_civil(data.get('Estado Civil', '')),
            'condicion_fiscal': self._mapear_condicion_fiscal(data.get('Condicion Fiscal', '')),
            'es_pep': data.get('Es PEP', 'N') == 'S',
            'sujeto_obligado_uif': data.get('Sujeto Obligado UIF', ''),
            'nacionalidad': data.get('Nacionalidad', ''),
            'residente': data.get('Residente', ''),
            'codigo_actividad': data.get('Codigo Actividad', ''),
            'fecha_ingreso': data.get('Fecha Ingreso', ''),
        }

    def _desglosar_nombre(self, nombre_completo):
        if not nombre_completo:
            return '', ''
        if ',' in nombre_completo:
            partes = nombre_completo.split(',', 1)
            return partes[0].strip(), partes[1].strip() if len(partes) > 1 else ''
        return '', nombre_completo.strip()

    def _mapear_genero(self, codigo):
        mapa = {'M': 'M', 'F': 'F', 'X': 'X'}
        return mapa.get(codigo, '')

    def _mapear_estado_civil(self, codigo):
        mapa = {'S': 'Soltero', 'C': 'Casado', 'D': 'Divorciado', 'V': 'Viudo', 'U': 'Unión civil'}
        return mapa.get(codigo, '')

    def _mapear_condicion_fiscal(self, codigo):
        mapa = {'CF': 'Consumidor Final', 'RI': 'IVA Responsable Inscripto', 
                'RNI': 'IVA Responsable no Inscripto', 'MT': 'Responsable Monotributo',
                'EX': 'IVA Sujeto Exento'}
        return mapa.get(codigo, '')


@method_decorator(login_required, name='dispatch')
class HealthCheckView(View):
    API_BASE_URL = 'http://186.189.231.237:8081/maasoft'
    TIMEOUT = 5

    def get(self, request, *args, **kwargs):
        try:
            response = requests.get(f"{self.API_BASE_URL}/health", timeout=self.TIMEOUT)
            return JsonResponse({
                'success': True,
                'status': 'OK',
                'api_status': 'online' if response.status_code == 200 else 'offline',
                'status_code': response.status_code
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'status': 'ERROR',
                'api_status': 'offline',
                'error': str(e)
            }, status=503)


# ================================================================
# NUEVAS VISTAS PARA VALIDACIONES DE UNICIDAD
# ================================================================

@method_decorator(login_required, name='dispatch')
class ConsultarExistenciaCuitView(View):
    """
    Consulta si un CUIT ya está registrado en Agilpagos (API intermedia).
    Endpoint: /maestros/api/validar-cuit-existencia/?cuit=20207882950
    """
    API_BASE_URL = 'http://186.189.231.237:8081/onboarding'
    TIMEOUT = 10

    def get(self, request, *args, **kwargs):
        cuit = request.GET.get('cuit', '').strip()
        if not cuit or not cuit.isdigit() or len(cuit) != 11:
            return JsonResponse({'success': False, 'error': 'CUIT inválido'}, status=400)

        try:
            url = f"{self.API_BASE_URL}/usuario/{cuit}"
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers, timeout=self.TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, str) and "No existe CVU asociado" in data:
                    return JsonResponse({'exists': False, 'detail': data})
                if isinstance(data, dict) and 'usuario' in data:
                    return JsonResponse({'exists': True, 'data': data})
                return JsonResponse({'exists': False, 'detail': 'No registrado'})
            else:
                return JsonResponse({'exists': False, 'detail': f'Error {response.status_code}'}, status=response.status_code)

        except requests.exceptions.Timeout:
            return JsonResponse({'success': False, 'error': 'Tiempo de espera agotado'}, status=408)
        except requests.exceptions.ConnectionError:
            return JsonResponse({'success': False, 'error': 'Error de conexión'}, status=503)
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Error interno'}, status=500)


@method_decorator(login_required, name='dispatch')
class ValidarUnicidadEmailView(View):
    """
    Verifica si un email ya está registrado en CuentaMutual.
    Query params: ?email=...&exclude= (pk a excluir en edición)
    """
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email', '').strip()
        exclude_pk = request.GET.get('exclude', '').strip()

        if not email:
            return JsonResponse({'exists': False, 'error': 'Email requerido'}, status=400)

        qs = CuentaMutual.objects.filter(email__iexact=email)
        if exclude_pk and exclude_pk.isdigit():
            qs = qs.exclude(pk=int(exclude_pk))

        return JsonResponse({'exists': qs.exists()})


@method_decorator(login_required, name='dispatch')
class ValidarUnicidadTelefonoView(View):
    """
    Verifica si un número de teléfono ya está registrado en CuentaMutual.
    Query params: ?telefono=...&exclude=... (pk a excluir en edición)
    """
    def get(self, request, *args, **kwargs):
        telefono = request.GET.get('telefono', '').strip()
        exclude_pk = request.GET.get('exclude', '').strip()

        if not telefono:
            return JsonResponse({'exists': False, 'error': 'Teléfono requerido'}, status=400)

        qs = CuentaMutual.objects.filter(numero_telefono=telefono)
        if exclude_pk and exclude_pk.isdigit():
            qs = qs.exclude(pk=int(exclude_pk))

        return JsonResponse({'exists': qs.exists()})