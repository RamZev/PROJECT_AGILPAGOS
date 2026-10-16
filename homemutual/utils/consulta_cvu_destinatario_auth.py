# homemutual/utils/consulta_cvu_destinatario_auth.py
"""
Consulta los datos de un CVU/CBU destinatario en Agilpagos.
Endpoint: GET /consulta/destinatario/{cvu}
Requiere autenticación previa (JWT).
"""
import httpx
import json


# ============================================================
# CREDENCIALES (HARDCODEADAS PARA PRUEBAS)
# ============================================================
AGILPAGOS_AUTH_URL = "https://agilpagosapi.maasoft.com.ar/auth/login"

USERNAME = "admin"
PASSWORD = "admin54321$$"

# CVU a consultar (modificalo según lo que necesites)
# CVU = "0000242600000000198390"
# GERARDO LUCAS BANDINI
CVU = "0000242600000000206576"


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


def consultar_cvu_destinatario(token, cvu):
    """Consulta los datos de un CVU/CBU destinatario en Agilpagos."""
    print("=" * 60)
    print(f"PASO 2: Consulta de CVU Destinatario {cvu}")
    print("=" * 60)

    url = f"https://agilpagosapi.maasoft.com.ar/consulta/destinatario/{cvu}"
    print(f"URL: {url}")
    print()

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    with httpx.Client(timeout=30) as client:
        response = client.get(url, headers=headers)

    print(f"Status: {response.status_code}")
    print()
    print("Response:")
    print("=" * 60)

    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print(response.text)

    print("=" * 60)
    return response


if __name__ == "__main__":
    try:
        token = obtener_token()
        response = consultar_cvu_destinatario(token, CVU)

        if response.status_code == 200:
            print()
            print("🎉 Consulta exitosa.")
        else:
            print()
            print(f"⚠️ Consulta con status {response.status_code}.")
    except Exception as e:
        print(f"❌ Error: {e}")