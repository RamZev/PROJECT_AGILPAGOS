from django.core.exceptions import ValidationError
from django.http import JsonResponse
import re

from django.apps import apps


#-------------------------------------------------------------------- 
#  Funciones.
#-------------------------------------------------------------------- 

#-- Función que verifica si el CUIT es válido (bien escrito).
def calcular_digito_verificador(cuit_base):
	''' Función que comprueba el dígito verificador.
	 	Retorna True si es correcto de lo contrario False. '''
	coeficientes = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
	cuit_digits = [int(digit) for digit in str(cuit_base)]
	suma = sum(cuit_digits[i] * coeficientes[i] for i in range(len(coeficientes)))
	resto = suma % 11
	
	if resto == 0:
		return 0
	elif resto == 1:
		return 9 if cuit_digits[0] in [2, 3] else 4
	else:
		return 11 - resto

def validar_cuit(cuit):
	''' Función que verifica si el CUIT es válido (bien escrito). '''
	cuit_str = str(cuit)
	
	#-- Validar que comience con los prefijos específicos y tenga 11 dígitos en total.
	if not re.match(r'^(20|23|24|25|26|27|30|33|34)\d{9}$', cuit_str):
		raise ValidationError("El CUIT debe comenzar con 20, 23, 24, 25, 26, 27, 30, 33 o 34, y tener 11 dígitos.")
	
	#-- Separar los primeros 10 dígitos y el dígito verificador.
	cuit_base = int(cuit_str[:-1])
	digito_verificador = int(cuit_str[-1])
	
	#-- Calcular el dígito verificador.
	digito_calculado = calcular_digito_verificador(cuit_base)
	
	#-- Validar el dígito verificador.
	if digito_verificador != digito_calculado:
		raise ValidationError("El CUIT no es válido.")

#-- Función que busca un cliente por el id suministrado.
def buscar_cliente_id(id):
	Cliente = apps.get_model("maestros", "Cliente")
	return Cliente.objects.filter(id_cliente=id).first()


#-------------------------------------------------------------------- 
#  Vistas.
#-------------------------------------------------------------------- 

#-- Vista que comprueba si existe más de un cliente con el mismo CUIT.
def buscar_cuit_view(request):
	''' Vista que busca si existen otros clientes con el mismo CUIT.'''
	#-- Dos opciones para evitar la Importación Circular:
	#-- Opción 1: Hacer el import dentro de la función.
	# from apps.maestros.models.cliente_models import Cliente
	
	#-- Opción 2: Usar Dependencia Indirecta.
	Cliente = apps.get_model("maestros", "Cliente")
	
	cuit = request.GET.get('cuit', None)
	if cuit:
		clientes = Cliente.objects.filter(cuit=cuit).values('id_cliente', 'nombre_cliente')
		if clientes.exists():
			data = {
				'existe': True,
				'clientes': list(clientes),
			}
		else:
			data = {'existe': False}
	else:
		data = {'existe': False, 'error': 'CUIT no proporcionado.'}
	return JsonResponse(data)

#-- Vista que busca cliente por el id suministrado.
def buscar_cliente_id_view(request):
	id_cliente = request.GET.get('id_cliente', None)
	
	if id_cliente and id_cliente.isdigit():
		cliente = buscar_cliente_id(id_cliente)
		print(f"{cliente = }")
		if cliente:
			data = {
				'existe': True,
				'cliente': cliente.nombre_cliente,
			}
		else:
			data = {'existe': False}
	elif id_cliente and not id_cliente.isdigit():
		data = {'existe': False, 'error': 'Id (Sub Cuenta) del cliente no es válido.'}
	else:
		data = {}
	
	return JsonResponse(data)
	
