# neumatic\utils\utils.py
import re, locale, unicodedata
from datetime import date, datetime
from decimal import Decimal
from django.forms.models import model_to_dict


def es_numero_valido(valor):
	"""Verifica si un string es un número decimal válido."""
	
	return bool(re.fullmatch(r"-?\d+(\.\d+)?", valor))  #-- Acepta "10", "-5.5", "3.14".


def serializar_datos(datos):
	"""Convierte datos no serializables a formatos compatibles con JSON para guardarlos en la sesión."""
	
	if isinstance(datos, Decimal):
		return str(datos)  # Convertir Decimal a str
	elif isinstance(datos, (date, datetime)):
		return datos.isoformat()  # Convertir date/datetime a str
	elif isinstance(datos, list):
		return [serializar_datos(item) for item in datos]  # Recursivo para listas
	elif isinstance(datos, dict):
		return {k: serializar_datos(v) for k, v in datos.items()}  # Recursivo para dicts
	return datos  # Si no es un tipo especial, devolver el valor tal cual


def deserializar_datos(datos):
	"""Restaura los datos serializados desde la sesión a sus tipos originales."""
	
	if isinstance(datos, str):
		#-- EXCEPCIÓN: Si el string tiene ceros a la izquierda, preservarlo como string (es probablemente un código).
		if (datos.startswith('0') and len(datos) > 1 and datos != '0' and'.' not in datos):  #-- NUEVA CONDICIÓN: excluir decimales.
			return datos  # Preservar como string (ej: "00021")
		
		if es_numero_valido(datos):  #-- Verifica si es un número válido antes de convertir.
			return Decimal(datos)
		try:
			return datetime.fromisoformat(datos)  #-- Intentar convertir a datetime.
		except ValueError:
			try:
				return date.fromisoformat(datos)  #-- Intentar convertir a date.
			except ValueError:
				return datos  #-- Si falla todo, devolver como string.
	elif isinstance(datos, list):
		return [deserializar_datos(item) for item in datos]
	elif isinstance(datos, dict):
		return {k: deserializar_datos(v) for k, v in datos.items()}
	return datos


def serializar_queryset(queryset):
	"""Convierte un queryset a una lista de diccionarios para su almacenamiento en la sesión."""
	
	return [model_to_dict(obj) for obj in queryset]


def raw_to_dict(instance):
	"""Convierte una instancia de ModelProxy (namedtuple) o modelo a un diccionario."""
	
	if hasattr(instance, '_asdict'):  #-- Para namedtuple (ModelProxy).
		return instance._asdict()
	elif hasattr(instance, '__dict__'):  #-- Para modelos normales.
		data = instance.__dict__.copy()
		data.pop('_state', None)
		return data
	else:
		#-- Si no es ninguno de los anteriores, intentamos convertir a dict directamente.
		return dict(instance)


def formato_argentino(valor):
	"""Formatea un número decimal con separadores de miles y coma como separador decimal, según el formato argentino."""
	
	return locale.format_string('%.2f', valor, grouping=True)


def formato_argentino_entero(valor):
	"""Formatea un número entero con separadores de miles según el formato argentino."""
	
	return locale.format_string('%d', valor, grouping=True)


def format_date(date_value):
	"""Helper para formatear fechas en formato dd/mm/yyyy."""
	
	if not date_value:
		return ""
	
	if isinstance(date_value, str):
		try:
			return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d/%m/%Y")
			# return datetime.strptime(date_value, "%Y-%m-%d").strftime("%d-%m-%Y")
		except ValueError:
			return date_value
	else:
		return date_value.strftime("%d/%m/%Y")
		# return date_value.strftime("%d-%m-%Y")


def normalizar(nombre):
	"""
	Normalize a string by removing Unicode diacritics and unsafe characters to produce
	a filesystem/identifier-friendly name.
	Parameters
	----------
	nombre : str
		The input string to normalize. Expected to be a Unicode/text string.
	Returns
	-------
	str
		A normalized string where:
		- Unicode characters are decomposed using NFKD and diacritical marks (e.g. accents, dieresis)
		  are removed.
		- Specific replacements are applied: 'ñ' -> 'n', 'Ñ' -> 'N', and spaces -> '_'.
		- Any remaining characters that are not word characters, hyphens or dots (i.e. not matching
		  the regular expression class [^\w\-.]) are removed.
	Raises
	------
	TypeError
		If `nombre` is not an instance of `str`.
	Notes
	-----
	- Implementation relies on `unicodedata.normalize('NFKD', ...)` to separate base characters
	  from combining diacritical marks, and then filters out combining characters.
	- A final regular-expression pass removes characters that could be problematic in filenames
	  or identifiers, preserving alphanumeric characters, underscore, hyphen and dot.
	- This function is suitable for generating safe filenames, URL slugs for simple use-cases,
	  or other identifiers where accents and special punctuation should be stripped.
	"""
	
	#-- Normaliza los caracteres Unicode (descompone acentos en caracteres base + acento).
	nombre_normalizado = unicodedata.normalize('NFKD', nombre)
	
	#-- Elimina los caracteres diacríticos (acentos, diéresis, etc.).
	nombre_sin_acentos = ''.join([c for c in nombre_normalizado if not unicodedata.combining(c)])
	
	#-- Reemplaza caracteres específicos que pueden causar problemas.
	reemplazos = {
		'ñ': 'n',
		'Ñ': 'N',
		' ': '_',  #-- Opcional: reemplazar espacios por guiones bajos.
	}
	
	#-- Aplica los reemplazos personalizados.
	for original, reemplazo in reemplazos.items():
		nombre_sin_acentos = nombre_sin_acentos.replace(original, reemplazo)
	
	#-- Elimina cualquier otro carácter que no sea alfanumérico, guión o punto.
	nombre_limpio = re.sub(r'[^\w\-.]', '', nombre_sin_acentos)
	
	return nombre_limpio


def numero_a_letras(numero):
	"""
	Convierte un número decimal a su representación en letras con formato para céntimos.
	Ejemplos:
	 123.45 → "ciento veintitrés con 45/100"
	 79245.01 → "setenta y nueve mil doscientos cuarenta y cinco con 01/100"
	 100.00 → "cien con 00/100"
	
	Args:
		numero (float/int): Número a convertir
		
	Returns:
		str: Representación del número en letras con formato XX/100
	"""
	
	#-- Verificar si es negativo.
	if numero < 0:
		return "menos " + numero_a_letras(abs(numero))
	
	#-- Separar parte entera y decimal.
	entero = int(numero)
	decimal = int(round((numero - entero) * 100))
	
	#-- Conversión de la parte entera.
	if entero == 0:
		resultado_entero = "cero"
	elif entero < 100:
		resultado_entero = convertir_decenas(entero)
	elif entero < 1000:
		resultado_entero = convertir_centenas(entero)
	elif entero < 1000000:
		resultado_entero = convertir_miles(entero)
	elif entero < 1000000000000:
		resultado_entero = convertir_millones(entero)
	else:
		resultado_entero = "número demasiado grande"
	
	#-- Formatear siempre con dos dígitos para los decimales.
	decimal_str = f"{decimal:02d}"
	return f"{resultado_entero} con {decimal_str}/100"


def convertir_decenas(numero):
	"""Convierte números entre 1-99 a letras"""
	
	unidades = ["", "uno", "dos", "tres", "cuatro", "cinco", 
				"seis", "siete", "ocho", "nueve"]
	especiales = ["diez", "once", "doce", "trece", "catorce", "quince",
				 "dieciséis", "diecisiete", "dieciocho", "diecinueve"]
	decenas = ["", "diez", "veinte", "treinta", "cuarenta", "cincuenta",
			  "sesenta", "setenta", "ochenta", "noventa"]
	
	if numero < 10:
		return unidades[numero]
	elif 10 <= numero < 20:
		return especiales[numero - 10]
	else:
		d = numero // 10
		u = numero % 10
		if u == 0:
			return decenas[d]
		else:
			return f"{decenas[d]} y {unidades[u]}"


def convertir_centenas(numero):
	"""Convierte números entre 100-999 a letras"""
	
	if numero == 100:
		return "cien"
	centenas = ["", "ciento", "doscientos", "trescientos", "cuatrocientos",
			   "quinientos", "seiscientos", "setecientos", "ochocientos",
			   "novecientos"]
	c = numero // 100
	resto = numero % 100
	if resto == 0:
		return centenas[c]
	else:
		return f"{centenas[c]} {convertir_decenas(resto)}"


def convertir_miles(numero):
	"""Convierte números entre 1000-999999 a letras"""
	
	miles = numero // 1000
	resto = numero % 1000
	
	if miles == 1:
		resultado_mil = "mil"
	else:
		resultado_mil = f"{numero_a_letras(miles).replace(' con 00/100', '')} mil"
	
	if resto == 0:
		return resultado_mil
	else:
		return f"{resultado_mil} {convertir_decenas(resto) if resto < 100 else convertir_centenas(resto)}"


def convertir_millones(numero):
	"""Convierte números entre 1000000-999999999 a letras"""
	
	millones = numero // 1000000
	resto = numero % 1000000
	
	if millones == 1:
		resultado_millon = "un millón"
	else:
		resultado_millon = f"{numero_a_letras(millones).replace(' con 00/100', '')} millones"
	
	if resto == 0:
		return resultado_millon
	else:
		return f"{resultado_millon} {numero_a_letras(resto).replace(' con 00/100', '')}"


def obtener_logo():
	"""Método auxiliar para obtener el logo de la empresa de forma segura"""
	
	from apps.maestros.models.empresa_models import Empresa
	
	logo_url = None
	logo_path = None
	
	try:
		empresa = Empresa.objects.first()
		if empresa:
			logo_url = empresa.logo_url_safe
			logo_path = empresa.logo_path_safe
	except Exception:
		pass
	
	return logo_url, logo_path


def format_user_display(user):
	"""
	Formatea un objeto User de Django para mostrar.
	
	Args:
		user: Instancia de django.contrib.auth.models.User
	
	Returns:
		str: Usuario formateado como "[id] Nombre Apellido" o "[id] username"
	"""
	
	if not user:
		return "[0] Sin usuario"
	
	#-- Obtener nombre completo si existe.
	if user.first_name and user.last_name:
		nombre_completo = f"{user.first_name} {user.last_name}"
	elif user.first_name:
		nombre_completo = user.first_name
	else:
		nombre_completo = user.username
	
	return f"[{user.id}] {nombre_completo}"