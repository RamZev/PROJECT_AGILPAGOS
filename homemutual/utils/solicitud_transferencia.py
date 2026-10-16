import httpx
import json

client = httpx.Client()

reqUrl = "https://agilpagosapi.maasoft.com.ar/transferencias/solicitar?id_usuario=2c04a9fc-e548-404c-8bbb-7bed3d2bf625"

headersList = {
 "Accept": "application/json",
 "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJGYWJpYW5hIiwidXNlcl9pZCI6IjMiLCJpZF91c3VhcmlvX2FnaWxwYWdvcyI6IjJjMDRhOWZjLWU1NDgtNDA0Yy04YmJiLTdiZWQzZDJiZjYyNSIsImlkX3NvY2lvIjoyLCJleHAiOjE3OTIwOTMyOTR9.zFGb_v6nuUIEwy9NU2g37UUmXxlkWSA4gKOeGyuIYIY",
 "Content-Type": "application/json" 
}

payload = json.dumps({
  "cuitCredito": "20207882950",
  "cbuCredito": "0000242600000000150200",
  "nombreCredito": "AGENO, MARIO",
  "idConcepto": "45D4F58B-46A2-4754-BBFA-FECB8CF88BFC",
  "importe": 1800,
  "descripcion": "Física (FABIANA MEZA) a Persona Física (MARIO AGENO) misma mutual.",
  "cvuDebito": "0000242600000000198390",
  "observaciones": "(destinatario padron SIRCUPA)"
})

data = client.post(reqUrl, data=payload, headers=headersList)

print(data.text)