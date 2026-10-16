import httpx

client = httpx.Client()

reqUrl = "https://agilpagosapi.maasoft.com.ar/consulta/destinatario/0000242600000000198390"  # <= La CVU va como path parameter.

headersList = {
 "Accept": "application/json",
 "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJGYWJpYW5hIiwidXNlcl9pZCI6IjMiLCJpZF91c3VhcmlvX2FnaWxwYWdvcyI6IjJjMDRhOWZjLWU1NDgtNDA0Yy04YmJiLTdiZWQzZDJiZjYyNSIsImlkX3NvY2lvIjoyLCJleHAiOjE3OTIxMDM0MDl9.aixyJI8zk_ZWy4tLW3_ZDwKubAb61FkyNgzUxecQojQ" 
}

payload = ""

data = client.get(reqUrl, headers=headersList)

print(data.text)