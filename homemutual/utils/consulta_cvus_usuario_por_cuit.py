# homemutual\utils\consulta_cvus_usuario_por_cuit.py
#-- 3.1.1 Consulta de CVU y Alias por CUIT - Manejo de Errores en creación de CVU.
import httpx

client = httpx.Client()

reqUrl = "https://agilpagosapi.maasoft.com.ar/onboarding/usuario/consulta/20207882950"

headersList = {
 "Accept": "application/json",
 "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOiI5Y2I0MTc2My1kMDMwLTRhNjYtYjY0My01OTg2ODk5ODRlOTEiLCJleHAiOjE3OTAyNjEyMDl9.woSf1WDndYZzcYUsdr6BhV9CjVMgfDguawIwx1txbSw" 
}

payload = ""

data = client.get(reqUrl, headers=headersList)

print(data.text)