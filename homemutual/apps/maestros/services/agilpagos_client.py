# apps/maestros/services/agilpagos_client.py
"""
Cliente HTTP para la API de Agilpagos.
Maneja la autenticación (JWT) y expone métodos para consultar la API.

La autenticación se hace con las credenciales del usuario logueado,
que se guardan en la sesión al momento del login (ver CustomLoginView).
"""
import logging
import time
import threading

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


# ============================================================
# EXCEPCIONES
# ============================================================
class CredentialsNotInSession(Exception):
    """Se levanta cuando la sesión no tiene credenciales de Agilpagos."""
    pass


# ============================================================
# CACHÉ DE TOKEN (en memoria del proceso, por usuario)
# ============================================================
class _TokenCache:
    """
    Caché de tokens por usuario.
    Estructura: { username: (token, expira_en_timestamp) }
    """
    def __init__(self):
        self._cache = {}
        self.lock = threading.Lock()

    def get(self, username, password):
        with self.lock:
            entry = self._cache.get(username)
            if entry:
                token, expira_en = entry
                # Si no expiró (con 60s de margen), devolverlo
                if time.time() < (expira_en - 60):
                    return token
            # Renovar
            token, expira_en = self._renovar(username, password)
            self._cache[username] = (token, expira_en)
            return token

    def invalidate(self, username):
        """Borra el token de un usuario."""
        with self.lock:
            self._cache.pop(username, None)

    def clear(self):
        """Borra TODOS los tokens."""
        with self.lock:
            self._cache.clear()

    def _renovar(self, username, password):
        """Pide un nuevo token JWT a Agilpagos."""
        url = settings.AGILPAGOS_AUTH_URL
        payload = {"username": username, "password": password}
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=settings.AGILPAGOS_TIMEOUT) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            logger.warning(
                f"Error autenticando en Agilpagos: {e.response.status_code} - "
                f"{e.response.text[:200]}"
            )
            raise
        except Exception as e:
            logger.error(f"Error inesperado autenticando en Agilpagos: {e}")
            raise

        token = data.get("access_token") or data.get("token")
        if not token:
            raise ValueError(f"No se encontró token en la respuesta: {data}")

        expires_in = data.get("expires_in")
        if expires_in:
            expira_en = time.time() + int(expires_in)
        else:
            expira_en = time.time() + 3600

        logger.info(f"Token de Agilpagos renovado para usuario: {username}")
        return token, expira_en


# Instancia global de la caché
_token_cache = _TokenCache()


# ============================================================
# HELPERS PARA LA SESIÓN
# ============================================================
def get_credentials_from_session(request):
    """
    Saca las credenciales de Agilpagos de la sesión del usuario.
    
    ⚠️ MODO PRUEBAS: si la sesión no tiene credenciales, usa las del .env.
    Cuando el login esté validado, eliminar este fallback.
    """
    username = request.session.get('agilpagos_username')
    password = request.session.get('agilpagos_password')

    # --- FALLBACK TEMPORAL PARA PRUEBAS ---
    if not username or not password:
        username = getattr(settings, 'AGILPAGOS_USERNAME', None)
        password = getattr(settings, 'AGILPAGOS_PASSWORD', None)
    # --------------------------------------

    if not username or not password:
        raise CredentialsNotInSession(
            "La sesión no contiene credenciales de Agilpagos. "
            "Vuelva a iniciar sesión."
        )
    return username, password

def get_token_for_session(request):
    """Devuelve un JWT válido para el usuario de la sesión."""
    username, password = get_credentials_from_session(request)
    return _token_cache.get(username, password)


# ============================================================
# CLIENTE HTTP
# ============================================================
def agilpagos_get(request, path, params=None, timeout=None):
    """Realiza un GET a la API de Agilpagos con el token del usuario de la sesión."""
    token = get_token_for_session(request)

    url = f"{settings.AGILPAGOS_API_BASE.rstrip('/')}/{path.lstrip('/')}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    with httpx.Client(timeout=timeout or settings.AGILPAGOS_TIMEOUT) as client:
        return client.get(url, headers=headers, params=params)


def agilpagos_post(request, path, json=None, timeout=None):
    """Realiza un POST a la API de Agilpagos con el token del usuario."""
    token = get_token_for_session(request)

    url = f"{settings.AGILPAGOS_API_BASE.rstrip('/')}/{path.lstrip('/')}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    with httpx.Client(timeout=timeout or settings.AGILPAGOS_TIMEOUT) as client:
        return client.post(url, headers=headers, json=json)