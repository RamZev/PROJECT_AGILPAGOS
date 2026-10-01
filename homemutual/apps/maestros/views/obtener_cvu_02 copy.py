import httpx
import json

client = httpx.Client()

reqUrl = "http://186.189.231.237:8081/onboarding/usuario/alta"


# Token dura 5 muinutos
headersList = {
  "Accept": "application/json",
  "Content-Type": "application/json",
}


payload = json.dumps({
  "nombre": "FABIANA ESTER",
  "apellido": "MEZA",
  "genero": "F",
  "fechaNacimiento": "1979-09-29",
  "idNacionalidad": "76b19e61-b8dc-40f4-bfab-422cbffe5002",
  "idTipoDocumento": "209C1CAA-C56D-4E03-BB40-E9EF2F319A3F",
  "numeroDocumento": "27749702",
  "numeroTramiteDocumento": "27211490258",
  "cuit": "27277497021",
  "idEstadoCivil": "a2dc98b4-49bf-40a5-be97-e7e3e5decb2c",
  "email": "fabianameza@gmail.com",
  "caracteristicaPais": "+54",
  "codigoArea": "3483",
  "numeroTelefono": "455820",
  "idCondicionFiscal": "ba933f3f-d18e-4aed-8585-dfa73e27da11",
  "esPep": False,
  "idMotivoPep": None,
  "esUIF": False,
  "leyFATCA": False,
  "idPaisNacimiento": "76b19e61-b8dc-40f4-bfab-422cbffe5002",
  "idPaisDomicilio":"76b19e61-b8dc-40f4-bfab-422cbffe5002",
  "idProvincia": "167e351c-44e0-47bb-8728-074293358cd9",
  "localidad": "Calchaqui",
  "calle": "URQUIZA 180",
  "altura": "URQUIZA 180",
  "cp": "3050",
  "piso": "",
  "departamento": "",
  "observaciones": "",
  "fechaAlta": "2022-02-22",
  "idOcupacion": "6864846e-a7e2-4c37-9c88-e81103e3c971",
  "numeroCuentaEntidad": "1004060",
  "idEntidadTipoDocumento": "CAE2882B-493C-4E1A-A6E7-B5E2BD25F808",
  "idTipoPersona": "20EB9127-7CA8-49E0-9E0B-CA8293218ACA",
  "idTipoCuenta": "D2483A34-78BE-40A2-B8CB-07AD4BCF6F61"
})

data = client.post(reqUrl, data=payload, headers=headersList)

print(data.text)

'''
{
  "id_usuario":"2c04a9fc-e548-404c-8bbb-7bed3d2bf625",
  "cvu":"0000242600000000198390",
  "alias":"",
  "id_usuario_entidad_lineas_cuentas":"00000000-0000-0000-0000-000000000000",
  "numero_cuenta_entidad":"1004060"
}
'''
