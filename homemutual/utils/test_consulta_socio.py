# utils/test_consulta_socio.py
import httpx
import json

# 1. Autenticarse
print("=" * 60)
print("PASO 1: Autenticación")
print("=" * 60)

auth = httpx.post(
    "https://agilpagosapi.maasoft.com.ar/auth/login",
    json={"username": "admin@mutual.com.ar", "password": "admin123"},
    timeout=10,
)
print(f"Status: {auth.status_code}")

if auth.status_code != 200:
    print(f"Error en auth: {auth.text}")
    exit(1)

auth_data = auth.json()
token = auth_data.get("access_token")
print(f"Token (primeros 50): {token[:50]}...")
print(f"Expira en: {auth_data.get('expires_in')} segundos")

# 2. Consultar socio
print()
print("=" * 60)
print("PASO 2: Consulta de socio")
print("=" * 60)

cuit = "20207882950"  # ← CAMBIAR POR UN CUIT REAL SI HACE FALTA
url = f"https://agilpagosapi.maasoft.com.ar/onboarding/usuario/consulta/{cuit}"
print(f"URL: {url}")

response = httpx.get(
    url,
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    },
    timeout=10,
)

print(f"Status: {response.status_code}")
print()
print("Respuesta completa:")
print("=" * 60)
try:
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception:
    print(response.text)