import httpx
import json

client = httpx.Client()

reqUrl = "https://agilpagosapi.maasoft.com.ar/auth/login"

headersList = {
 "Accept": "application/json",
 "Content-Type": "application/json" 
}

# payload = json.dumps({
#   "username": "admin@mutual.com.ar",
#   "password": "admin123"
# })

payload = json.dumps({
  "username": "admin",
  "password": "admin54321$$"
})

data = client.post(reqUrl, data=payload, headers=headersList)

print(data.text)