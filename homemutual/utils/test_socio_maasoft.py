# utils/test_socio_maasoft.py
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
    print(f"Error: {auth.text}")
    exit(1)

token = auth.json().get("access_token")
print(f"Token OK")

# 2. Consultar socio con el endpoint CORRECTO
print()
print("=" * 60)
print("PASO 2: Consulta de socio (endpoint CORRECTO)")
print("=" * 60)

## cuit = "27356537098"  # ← CAMBIAR POR UN CUIT REAL SI HACE FALTA
cuit = "20236887538"
url = f"https://agilpagosapi.maasoft.com.ar/maasoft/socio/{cuit}"
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

if response.status_code == 200:
    print("Respuesta completa:")
    print("=" * 60)
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print(response.text)
else:
    print(f"Respuesta: {response.text}")