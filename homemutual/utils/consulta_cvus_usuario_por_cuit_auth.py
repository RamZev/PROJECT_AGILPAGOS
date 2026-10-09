# homemutual\utils\consulta_cvus_usuario_por_cuit_auth.py
"""
Consulta las CVUs y alias de un usuario por CUIT.
Endpoint: GET /onboarding/usuario/consulta/{cuit}
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

# CUIT a consultar (modificalo según lo que necesites)
CUIT = "20207882950"
CUIT = "20207776085"

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


def consultar_cvus_usuario(token, cuit):
    """Consulta las CVUs de un usuario por CUIT."""
    print("=" * 60)
    print(f"PASO 2: Consulta de CVUs por CUIT {cuit}")
    print("=" * 60)

    url = f"https://agilpagosapi.maasoft.com.ar/onboarding/usuario/consulta/{cuit}"
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
        response = consultar_cvus_usuario(token, CUIT)

        if response.status_code == 200:
            print()
            print("🎉 Consulta exitosa.")
        else:
            print()
            print(f"⚠️ Consulta con status {response.status_code}.")
    except Exception as e:
        print(f"❌ Error: {e}")