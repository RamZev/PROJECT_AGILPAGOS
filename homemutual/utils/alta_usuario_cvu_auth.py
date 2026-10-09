# alta_usuario_cvu_auth.py
"""
Prueba de alta de Usuario + CVU en Agilpagos.
Endpoint: POST /onboarding/usuario/alta
Requiere autenticación previa (JWT).
"""
import httpx
import json


# ============================================================
# CREDENCIALES (HARDCODEADAS PARA PRUEBAS)
# ============================================================
AGILPAGOS_AUTH_URL = "https://agilpagosapi.maasoft.com.ar/auth/login"
AGILPAGOS_ALTA_URL = "https://agilpagosapi.maasoft.com.ar/onboarding/usuario/alta"

# USERNAME = "admin@mutual.com.ar"
# PASSWORD = "admin123"

USERNAME = "admin"
PASSWORD = "admin54321$$"

def obtener_token():
    """Autenticarse en Agilpagos y obtener el JWT."""
    print("=" * 60)
    print("PASO 1: Autenticación")
    print("=" * 60)

    with httpx.Client(timeout=10) as client:
        response = client.post(
            AGILPAGOS_AUTH_URL,
            json={"username": USERNAME, "password": PASSWORD},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

    token = data.get("access_token") or data.get("token")
    if not token:
        raise ValueError(f"No se encontró token en la respuesta: {data}")

    print(f"✅ Token obtenido (primeros 50): {token[:50]}...")
    print(f"   Expira en: {data.get('expires_in', 'N/A')} segundos")
    print()
    return token


def alta_usuario_cvu(token):
    """Da de alta un Usuario + CVU en Agilpagos."""
    print("=" * 60)
    print("PASO 2: Alta de Usuario + CVU")
    print("=" * 60)

    payload = {
        # ---- Datos personales ----
        "nombre": "FABIANA ESTER",
        "apellido": "MEZA",
        "genero": "F",
        "fechaNacimiento": "1979-09-29",

        # ---- Nacionalidad ----
        "idNacionalidad": "76b19e61-b8dc-40f4-bfab-422cbffe5002",
        "idPaisNacimiento": "76b19e61-b8dc-40f4-bfab-422cbffe5002",

        # ---- Documento ----
        "idTipoDocumento": "209C1CAA-C56D-4E03-BB40-E9EF2F319A3F",
        "numeroDocumento": "27749702",
        "numeroTramiteDocumento": "27211490255",
        "cuit": "27277497021",

        # ---- Contacto ----
        "email": "silvanapaulon@gmail.com",
        "caracteristicaPais": "+54",
        "codigoArea": "3483",
        "numeroTelefono": "415820",

        # ---- Situación fiscal y legal ----
        "idEstadoCivil": "a2dc98b4-49bf-40a5-be97-e7e3e5decb2c",
        "idCondicionFiscal": "ba933f3f-d18e-4aed-8585-dfa73e27da11",
        "idOcupacion": "6864846e-a7e2-4c37-9c88-e81103e3c971",
        "esPep": False,
        "idMotivoPep": None,
        "esUIF": False,
        "leyFATCA": False,

        # ---- Domicilio ----
        "idPaisDomicilio": "76b19e61-b8dc-40f4-bfab-422cbffe5002",
        "idProvincia": "167e351c-44e0-47bb-8728-074293358cd9",
        "localidad": "Calchaqui",
        "calle": "URQUIZA 180",
        "altura": "URQUIZA 180",
        "cp": "3050",
        "piso": "",
        "departamento": "",
        "observaciones": "",

        # ---- Fechas ----
        "fechaAlta": "2022-02-22",

        # ---- Datos de la CVU ----
        "numeroCuentaEntidad": "1004060",

        # ---- Catálogos SG ----
        "idEntidadTipoDocumento": "CAE2882B-493C-4E1A-A6E7-B5E2BD25F808",
        "idTipoPersona": "20EB9127-7CA8-49E0-9E0B-CA8293218ACA",
        "idTipoCuenta": "D2483A34-78BE-40A2-B8CB-07AD4BCF6F61",
    }

    print("Request payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",   # ← ⚠️ AGREGADO
    }

    with httpx.Client(timeout=30) as client:
        response = client.post(
            AGILPAGOS_ALTA_URL,
            json=payload,
            headers=headers,
        )

    print(f"Status: {response.status_code}")
    print()
    print("Response:")
    print("=" * 60)

    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print(response.text)

    return response


if __name__ == "__main__":
    try:
        token = obtener_token()
        response = alta_usuario_cvu(token)

        if response.status_code == 200:
            print()
            print("🎉 Alta exitosa.")
        else:
            print()
            print(f"⚠️ Alta con status {response.status_code}.")
    except Exception as e:
        print(f"❌ Error: {e}")