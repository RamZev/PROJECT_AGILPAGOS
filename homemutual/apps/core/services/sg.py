# homemutual/core/services/sg.py
from __future__ import annotations
import logging
from typing import Any, Dict, Optional, Tuple
import requests
import re
from django.conf import settings
from datetime import date, datetime

log = logging.getLogger(__name__)

class SGError(Exception):
    pass

def _digits(s) -> str:
    return re.sub(r"\D+", "", str(s or ""))

def _dni8(s) -> str:
    d = _digits(s)
    # SG exige exactamente 8 dígitos; si tiene menos, completar con ceros a la izquierda
    return d.zfill(8) if d else d

def _iso(dt):
    if not dt:
        return None
    if isinstance(dt, (date, datetime)):
        return dt.isoformat()
    try:
        d, m, y = str(dt).split("/")
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
    except Exception:
        return str(dt)
   
def _clean(d: dict) -> dict:
    return {k: v for k, v in d.items() if v not in (None, "", [], {})}

class SGClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self.base_url = (base_url or settings.SG_CONNECTOR_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.SG_CONNECTOR_API_KEY
        self.timeout = timeout or settings.SG_CONNECTOR_TIMEOUT

    def _headers(self) -> Dict[str, str]:
        # Si tu wrapper usa otro header, cambialo acá.
        return {
            "Accept": "application/json",
            "X-API-Key": self.api_key,
        }

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            r = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        except requests.RequestException as ex:
            log.exception("SG GET %s error: %s", url, ex)
            raise SGError("No se pudo conectar con el conector SG.") from ex

        if r.status_code == 404:
            return {"_not_found": True, "_status": 404}
        if not r.ok:
            log.error("SG GET %s -> %s %s", url, r.status_code, r.text[:400])
            raise SGError(f"Error SG GET {r.status_code}")
        return r.json()

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}{path}"
        try:
            r = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
        except requests.RequestException as ex:
            log.exception("SG POST %s error: %s", url, ex)
            raise SGError("No se pudo conectar con el conector SG.") from ex

        if not r.ok:
            # >>> incluye el cuerpo del error para ver 'validation errors' en los mensajes
            raise SGError(f"Error SG POST {r.status_code}: {r.text}")
        return r.json()

    def usuario_by_cuit(self, cuit: str) -> dict:
        # antes: return self._get("/sg/usuario_by_cuit", params={"cuit": cuit})
        return self._get(f"/sg/usuarios/{cuit}/by-cuit")

    def crear_usuario(self, payload: dict) -> dict:
        # antes: return self._post("/sg/usuario", payload)
        return self._post("/sg/usuarios", payload)


def _get_ci(d: dict, key: str, default=None):
    """dict.get() case-insensitive"""
    if not isinstance(d, dict):
        return default
    low = key.lower()
    for k, v in d.items():
        if k.lower() == low:
            return v
    return default

def _first_account_like(cuentas: list, nro_cuenta_entidad: str):
    if not isinstance(cuentas, list):
        return None
    # match por nroCuentaEntidad o numeroCuentaEntidad (tolerante)
    for x in cuentas:
        nce = _get_ci(x, "nroCuentaEntidad") or _get_ci(x, "numeroCuentaEntidad")
        if str(nce or "") == str(nro_cuenta_entidad):
            return x
    return cuentas[0] if cuentas else None

def _parse_usuario_payload(resp: dict):
    """
    Devuelve (idUsuario, cuentas:list|None) desde las posibles formas de tu wrapper.
    Acepta:
      - { "usuario": { "idUsuario": "...", "cuentas": [...] } }
      - { "idUsuario": "...", "cuentas": [...] }
      - { "data": { ...igual... } }
    """
    if not isinstance(resp, dict):
        return None, None

    root = resp
    # fallback en data/usuario
    if _get_ci(root, "usuario"):
        root = _get_ci(root, "usuario")
    elif _get_ci(root, "data"):
        data = _get_ci(root, "data")
        root = _get_ci(data, "usuario") or data

    id_usuario = _get_ci(root, "idUsuario") or _get_ci(root, "id_usuario") or _get_ci(root, "id")
    cuentas = _get_ci(root, "cuentas") or _get_ci(root, "accounts") or []
    return (str(id_usuario) if id_usuario else None, cuentas)

def resolve_sg_for_cuenta(
    *,
    cuit: str,
    nro_cuenta_entidad: str,
    nombre: str,
    apellido: str,
    email: Optional[str] = None,
    telefono: Optional[str] = None,
    force_create: bool = False,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    (1) Busca por CUIT en tu wrapper; si no existe -> (2) crea.
    (force_create=True) crea una cuenta si no existe una con ese numeroCuentaEntidad.
    Retorna: (idUsuario, cvu, alias, estado, reason)
    - reason: string breve para mensajes cuando falten datos.
    """
    client = SGClient()
    try:
        r = client.usuario_by_cuit(cuit)

        # Algunos wrappers devuelven 200 con "found=false" o similar
        found_flags = {
            "found": _get_ci(r, "found"),
            "exists": _get_ci(r, "exists"),
            "status": _get_ci(r, "status"),
            "_not_found": r.get("_not_found"),
        }
        not_found = (
            (found_flags["_not_found"] is True) or
            (found_flags["found"] is False) or
            (found_flags["exists"] is False) or
            (str(found_flags["status"]).startswith("404"))
        )

        if not_found:
            # No existe nada para ese CUIT -> crear usuario/cuenta
            payload = {
                "nombre": nombre, "apellido": apellido, "cuit": cuit,
                "email": email, "telefono": telefono,
                "numeroCuentaEntidad": nro_cuenta_entidad,
            }
            c = client.crear_usuario(payload)
            idu, cuentas = _parse_usuario_payload(c)
            if not idu:
                return (None, None, None, None, "POST sin idUsuario")
            m = _first_account_like(cuentas, nro_cuenta_entidad)
            if not m:
                return (idu, None, None, None, "POST sin cuentas")
            cvu   = _get_ci(m, "cvu")
            alias = _get_ci(m, "alias")
            estado= _get_ci(m, "estado")
            return (idu, cvu, alias, estado, None)

        # Existe usuario -> ver cuentas
        idu, cuentas = _parse_usuario_payload(r)
        if not idu:
            return (None, None, None, None, "GET sin idUsuario")

        match = _first_account_like(cuentas, nro_cuenta_entidad)

        # Si no hay cuenta para este nroCuentaEntidad y pediste force_create -> crearla
        if not match and force_create:
            payload = {
                "nombre": nombre, "apellido": apellido, "cuit": cuit,
                "email": email, "telefono": telefono,
                "numeroCuentaEntidad": nro_cuenta_entidad,
            }
            c = client.crear_usuario(payload)
            idu2, cuentas2 = _parse_usuario_payload(c)
            if not idu2:
                return (idu, None, None, None, "FORCE POST sin idUsuario")
            match = _first_account_like(cuentas2, nro_cuenta_entidad)

        if not match:
            # no hay cuenta para este nroCuentaEntidad
            return (idu, None, None, None, "GET sin cuenta para esa numeroCuentaEntidad")

        cvu   = _get_ci(match, "cvu")
        alias = _get_ci(match, "alias")
        estado= _get_ci(match, "estado")
        return (idu, cvu, alias, estado, None)

    except SGError as ex:
        return (None, None, None, None, f"wrapper no disponible: {ex}")

'''
def _iso(dt):
    if not dt:
        return None
    if isinstance(dt, (date, datetime)):
        return dt.isoformat()
    # Acepta "dd/mm/YYYY" -> "YYYY-mm-dd"
    try:
        d, m, y = str(dt).split("/")
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
    except Exception:
        return str(dt)

def _clean(d: dict) -> dict:
    # Saca None / vacío para evitar rechazos del wrapper
    return {k: v for k, v in d.items() if v not in (None, "", [], {})}
'''


def build_sg_payload(obj) -> dict:
    sexo = (getattr(obj, "sexo", "") or "").strip().upper()
    if sexo.startswith("M"):
        sexo = "M"
    elif sexo.startswith("F"):
        sexo = "F"
    else:
        sexo = None

    payload = {
        "nombre": (getattr(obj.id_user, "first_name", "") or getattr(obj, "razon_social", "") or "").strip(),
        "apellido": (getattr(obj.id_user, "last_name", "") or "").strip(),
        "razonSocial": getattr(obj, "razon_social", None) or None,
        "sexo": sexo,

        "idEntidadTipoDocumento": getattr(obj, "id_entidad_tipo_documento_id", None),
        "numeroDocumento": _dni8(getattr(obj, "documento", None)),  # <--- AQUÍ EL CAMBIO

        "fechaNacimiento": _iso(getattr(obj, "fecha_nacimiento", None)),
        "cuit": _digits(getattr(obj, "cuit", None)) or None,  # opcional: solo dígitos

        "email": getattr(obj.id_user, "email", None) or None,
        "caracteristicaPaisTelefono": getattr(obj, "caracteristica_pais_telefono", None) or None,
        "codigoAreaTelefono": getattr(obj, "codigo_area_telefono", None) or None,
        "numeroTelefono": getattr(obj, "numero_telefono", None) or None,

        "idTipoPersona": getattr(obj, "id_tipo_persona_id", None),
        "numeroCuentaEntidad": str(getattr(obj, "cuenta", "") or "").strip(),
        "idTipoCuenta": getattr(obj, "id_tipo_cuenta_id", None),
    }
    return _clean(payload)


def create_sg_account_from_obj(obj):
    client = SGClient()
    try:
        payload = build_sg_payload(obj)
        c = client.crear_usuario(payload)  # POST /sg/usuarios
    except SGError as ex:
        # devolvemos motivo legible a la View (que lo muestra con messages.warning)
        return (None, None, None, None, None, f"SG rechazó el alta: {ex}")

    idu = c.get("idUsuario")
    cuentas = c.get("cuentas") or []

    def _norm(v): 
        s = str(v or "")
        return s.lstrip("0") or "0"

    nce = _norm(payload.get("numeroCuentaEntidad"))
    match = next((x for x in cuentas if _norm(x.get("nroCuentaEntidad") or x.get("numeroCuentaEntidad")) == nce), None)
    if not match and cuentas:
        match = cuentas[0]

    if not (idu and match):
        return (idu, None, None, None, None, "POST /sg/usuarios sin datos suficientes")

    idcta = match.get("idCuenta") or match.get("id")
    return (idu, idcta, match.get("cvu"), match.get("alias"), match.get("estado"), None)

