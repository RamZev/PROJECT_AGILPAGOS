# neumatic\apps\maestros\templatetags\custom_tags.py
from django import template
from decimal import Decimal
import locale
# from ..models.base_models import ProductoEstado

register = template.Library()


@register.filter(name='get_attribute')
def get_attribute(value, arg):
	"""
	Obtiene el valor de un atributo de un objeto.
	"""
	try:
		return getattr(value, arg)
	except AttributeError:
		return None


@register.filter(name='get_item')
def get_item(dictionary, key):
	"""
	Obtiene un valor de un diccionario dada una clave.
	
	Args:
		dictionary (dict): El diccionario del cual se quiere obtener el valor.
		key (str): La clave a buscar en el diccionario.
	
	Returns:
		any: El valor asociado con la clave en el diccionario, o None si la clave no se encuentra.
	"""
	return dictionary.get(key, None)


@register.filter(name='get_columna')
def get_columna(field, field_name):
	"""
		Obtiene el valor de la columna definida en los atributos extra de un campo de formulario.
		
		Este filtro busca en el diccionario 'extra_attrs' del widget del campo el valor de la clave 'columna'.
		Si la clave 'columna' no se encuentra en 'extra_attrs', devuelve un valor por defecto de 12.
		
		Args:
			field: El campo del formulario del cual se quiere obtener el valor de la columna.
			field_name: El nombre del campo (no se utiliza en la función, pero se incluye para mantener la compatibilidad con la etiqueta de plantilla).
		
		Returns:
			int: El valor de la columna definido en los atributos extra del campo, o 12 si no se encuentra.
	"""
	extra_attrs = field.widget.attrs.get('extra_attrs', {})
	return extra_attrs.get('columna', 12)  #-- Si no se encuentra, se devuelve 12 por defecto.


@register.filter
def get_type(value):
	""" Devuelve el tipo de valor en formato string."""
	# print(f"🔍 Valor: {repr(value)} | Tipo: {type(value).__name__} | Clase: {type(value)}")
	return type(value).__name__

@register.filter
def in_list(value, arg_list):
	"""
	Verifica si un valor está en una lista.
	Maneja casos donde arg_list es None o no es una lista.
	"""
	if arg_list is None:
		return False
	if not isinstance(arg_list, (list, tuple, set)):
		#-- Si no es una lista, convertir a lista o tratar como lista de un elemento.
		try:
			arg_list = list(arg_list)
		except TypeError:
			#-- Si no se puede iterar, asumir que es un solo valor.
			return value == arg_list
	return value in arg_list

@register.filter
def formato_es_ar(value):
	"""
	Formatea un número con el formato de Argentina:
	Separador de miles: punto (.)
	Separador decimal: coma (,)
	Compatible con float y Decimal.
	"""
	try:
		#-- Configura el locale para números en es_AR.
		locale.setlocale(locale.LC_NUMERIC, 'es_AR.UTF-8')
		
		#-- Convierte a float si el valor es Decimal.
		if isinstance(value, Decimal):
			value = float(value)
		
		#-- Formatea con separadores de miles y 2 decimales.
		return locale.format_string('%.2f', value, grouping=True)
	except (ValueError, TypeError):
		#-- Devuelve el valor sin formatear si no es un número válido.
		return value


@register.filter
def formato_es_ar_entero(value):
	"""
	Formatea un número entero con el formato de Argentina:
	- Separador de miles: punto (.)
	- Sin decimales
	- Compatible con int, float y Decimal.
	"""
	try:
		#-- Configura el locale para números en es_AR.
		locale.setlocale(locale.LC_NUMERIC, 'es_AR.UTF-8')
		
		#-- Convierte a float si es Decimal y luego a int.
		if isinstance(value, Decimal):
			value = int(float(value))
		elif isinstance(value, float):
			value = int(value)
			
		#-- Formatea con separadores de miles y sin decimales.
		return locale.format_string('%d', value, grouping=True)
	except (ValueError, TypeError):
		#-- Devuelve el valor sin formatear si no es un número válido.
		return value


# @register.simple_tag
# def get_color_estado(nombre_estado):
# 	"""
# 	Devuelve el color del Estado de Producto según el nombre del Estado si lo consigue,
# 	de lo contrario devuelve color blanco.
# 	"""
# 	try:
# 		return ProductoEstado.objects.get(nombre_producto_estado=nombre_estado).color
# 	except ProductoEstado.DoesNotExist:
# 		return '#FFFFFF'  #-- Color por defecto si no existe.


@register.filter
def get_estatus(estatus):
	return "Activo" if estatus else "Inactivo"


@register.filter
def get_si_no(estatus):
	return "Si" if estatus else "No"


@register.filter
def vacio_si_cero(value):
	"""
	Retorna vacío si el valor es 0, sino retorna el valor.
	Compatible con int, float, Decimal y string.
	"""
	try:
		#-- Convertir a float para hacer la comparación.
		valor_numerico = float(value)
		
		#-- Si es exactamente 0, retornar vacío.
		if valor_numerico == 0.0:
			return ""
	except (ValueError, TypeError):
		#-- Si no se puede convertir a número, retornar el valor original.
		pass
	
	return value


@register.filter
def formatear_caja(numero_caja):
	"""
	Formatea el número de caja con el formato XX-XXXXXX
	Completa con ceros a la izquierda hasta tener 8 dígitos.
	
	Args:
		numero_caja (int/str): El número de caja a formatear
		
	Returns:
		str: El número formateado como XX-XXXXXX
	"""
	try:
		#-- Convertir a string y rellenar con ceros a la izquierda hasta 8 dígitos.
		numero_formateado = str(numero_caja).zfill(8)
		#-- Retornar con el formato XX-XXXXXX.
		return f"{numero_formateado[:2]}-{numero_formateado[2:]}"
	except (ValueError, TypeError, AttributeError):
		#-- Devuelve el valor sin formatear si hay error.
		return numero_caja


@register.filter
def null_to_na(value):
	if value is None or str(value).lower() == 'null':
		return 'N/A'
	return value