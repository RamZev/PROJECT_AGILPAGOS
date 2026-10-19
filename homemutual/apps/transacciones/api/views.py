# apps/transacciones/api/views.py
"""
Endpoints JSON para el flujo de transferencias.

Actúan como proxy entre el frontend (JS) y la API Intermedia.
NO persisten nada directamente: la API Intermedia es la que
escribe en cashout_request, cashout_response, movimiento, etc.
"""
import json
import logging

import httpx
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required

from apps.maestros.services.agilpagos_client import (
	agilpagos_get,
	agilpagos_post,
	CredentialsNotInSession,
)


logger = logging.getLogger(__name__)


# ============================================================================
# HELPERS
# ============================================================================
def _error_response(message: str, status: int = 400, detail=None) -> JsonResponse:
	"""
	Devuelve una respuesta JSON de error consistente.
	"""
	
	return JsonResponse(
		{"success": False, "error": message, "detail": detail},
		status=status,
	)


def _extract_error_from_response(response: httpx.Response) -> tuple:
	"""
	Extrae el mensaje de error del body de la respuesta.
	
	Returns:
		(mensaje, status_code)
	"""
	
	try:
		data = response.json()
		message = data.get("detail") or data.get("error") or "Error en la solicitud."
		return message, response.status_code
	except Exception:
		return f"Error {response.status_code}: {response.text[:200]}", response.status_code


def _handle_agilpagos_exception(e: Exception) -> JsonResponse:
	"""
	Traduce una excepción del cliente a JsonResponse.
	"""
	
	if isinstance(e, CredentialsNotInSession):
		logger.warning(f"Credenciales no disponibles en sesión: {e}")
		return _error_response(
			"Sesión expirada. Vuelva a iniciar sesión.",
			status=401,
		)
	if isinstance(e, httpx.HTTPStatusError):
		message, status = _extract_error_from_response(e.response)
		logger.warning(f"Error de la API: {status} - {message}")
		return _error_response(message, status=status)
	if isinstance(e, httpx.TimeoutException):
		logger.error(f"Timeout al llamar a la API: {e}")
		return _error_response(
			"La API no respondió a tiempo. Intente más tarde.",
			status=504,
		)
	if isinstance(e, httpx.ConnectError):
		logger.error(f"Error de conexión con la API: {e}")
		return _error_response(
			"No se pudo conectar con la API.",
			status=502,
		)
	logger.error(f"Error inesperado en endpoint de transferencias: {e}", exc_info=True)
	return _error_response(
		"Error interno del servidor.",
		status=500,
	)


# ============================================================================
# CVUs PROPIAS
# ============================================================================
@login_required
@require_GET
def api_cvus_propias(request):
	"""
	Devuelve las CVUs propias del socio autenticado.
	
	Llama a: GET /consulta/cvus-propias
	"""
	
	try:
		response = agilpagos_get(request, "/consulta/cvus-propias")
		response.raise_for_status()
		return JsonResponse({"success": True, "data": response.json()})
	except Exception as e:
		return _handle_agilpagos_exception(e)


# ============================================================================
# BUSCAR DESTINATARIO
# ============================================================================
@login_required
@require_GET
def api_buscar_destinatario(request):
	"""
	Busca un destinatario por CVU.
	
	Query param: ?cvu=<22 dígitos>
	
	Llama a: GET /consulta/destinatario/{cvu}
	"""
	
	cvu = request.GET.get("cvu", "").strip()
	
	if not cvu or not cvu.isdigit() or len(cvu) != 22:
		return _error_response(
			"El CVU/CBU debe tener 22 dígitos numéricos.",
			status=400,
		)
	
	try:
		response = agilpagos_get(request, f"/consulta/destinatario/{cvu}")
		response.raise_for_status()
		return JsonResponse({"success": True, "data": response.json()})
	except Exception as e:
		return _handle_agilpagos_exception(e)


# ============================================================================
# SOLICITAR TRANSFERENCIA
# ============================================================================
@login_required
@require_POST
def api_solicitar_transferencia(request):
	"""
	Solicita una transferencia (CashOut).
	
	Body JSON: ver docstring del endpoint /transferencias/solicitar.
	
	Llama a: POST /transferencias/solicitar
	"""
	
	try:
		body = json.loads(request.body)
	except (json.JSONDecodeError, UnicodeDecodeError):
		return _error_response("Body JSON inválido.", status=400)
	
	#-- Validaciones básicas.
	required = [
		"cvuDebito", "cbuCredito", "cuitCredito", "idConcepto",
		"importe", "descripcion",
	]
	missing = [f for f in required if not body.get(f)]
	if missing:
		return _error_response(
			f"Faltan campos obligatorios: {', '.join(missing)}.",
			status=400,
		)
	
	try:
		response = agilpagos_post(request, "/transferencias/solicitar", json=body)
		response.raise_for_status()
		return JsonResponse({"success": True, "data": response.json()})
	except Exception as e:
		return _handle_agilpagos_exception(e)
