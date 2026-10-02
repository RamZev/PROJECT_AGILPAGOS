import json
import time
import requests

# Configuración del rango y el endpoint básico
CODIGO_INICIO = 4000
CODIGO_FIN = 4482
URL_BASE = "http://186.189.231.237:8081/maasoft/sociocodigo/"

# Columnas específicas que usamos en el Excel
COLUMNAS_DESEADAS = [
    "Codigo",
    "CUIT",
    "Nombre",
    "Tipo Documento",
    "Numero Documento",
    "Estado Civil",
    "Sexo",
    "Condicion Fiscal",
    "Fecha Nacimiento",
    "Fecha Ingreso",
    "Es PEP",
    "Nacionalidad",
    "Sujeto Obligado UIF",
    "Telefono",
    "Movil",
    "e-Mail",
    "Domicilio",
    "Codigo Postal",
]

socios_filtrados = []

print(f"Iniciando descarga de socios desde el {CODIGO_INICIO} al {CODIGO_FIN}...")

for codigo in range(CODIGO_INICIO, CODIGO_FIN + 1):
    url = f"{URL_BASE}{codigo}"

    try:
        # Hacemos la petición GET
        response = requests.get(url, headers={"accept": "application/json"})

        # Si el socio existe (Status 200)
        if response.status_code == 200:
            datos_completos = response.json()

            # Creamos un nuevo diccionario solo con las columnas deseadas
            datos_filtrados = {
                col: datos_completos.get(col, "") for col in COLUMNAS_DESEADAS
            }

            socios_filtrados.append(datos_filtrados)
            print(f"-> Socio {codigo} procesado correctamente.")

        elif response.status_code == 404:
            print(f"-> Socio {codigo} no encontrado (404). Saltando...")
        else:
            print(
                f"-> Error {response.status_code} al consultar el socio {codigo}."
            )

    except requests.exceptions.RequestException as e:
        print(f"X Error de conexión en el socio {codigo}: {e}")

    # Pausa de cortesía (0.1 segundos) para no saturar el servidor de golpe
    time.sleep(0.1)

# Guardar todos los datos recolectados en un único archivo JSON
archivo_salida = "socios_filtrados.json"
with open(archivo_salida, "w", encoding="utf-8") as f:
    json.dump(socios_filtrados, f, ensure_ascii=False, indent=2)

print(
    f"\n¡Proceso finalizado! Se guardaron {len(socios_filtrados)} socios en '{archivo_salida}'."
)