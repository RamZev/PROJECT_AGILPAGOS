# neumatic\apps\maestros\models\empresa_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re
import os

from utils.validator.validaciones import validar_cuit
from .base_gen_models import ModeloBaseGenerico
# from .base_models import Localidad, Provincia, TipoIva
from entorno.constantes_base import ESTATUS_GEN


def logo_upload_path(instance, filename):
	"""Genera la ruta donde se guardará el logo preservando el nombre original"""
	
	#-- Obtener el nombre base y extensión.
	name, ext = os.path.splitext(filename)
	
	#-- Limpiar el nombre: solo letras, números, guiones y guiones bajos.
	clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
	
	#-- Si el nombre quedó vacío, usar un nombre por defecto.
	if not clean_name:
		clean_name = 'logo'
	
	#-- Usar el id de la empresa si existe.
	empresa_id = instance.id_empresa if instance.id_empresa else 'temp'
	
	#-- Preservar el nombre original con el ID de la empresa.
	new_filename = f'logo_{empresa_id}_{clean_name}{ext}'
	
	#-- Guardar en: media/empresas/logos/
	return os.path.join('empresas', 'logos', new_filename)


class Empresa(ModeloBaseGenerico):
	id_empresa = models.AutoField(
		primary_key=True
	)
	estatus_empresa = models.BooleanField(
		verbose_name="Estatus*",
		default=True,
		choices=ESTATUS_GEN
	)
	nombre_fiscal = models.CharField(
		verbose_name="Nombre Fiscal*",
		max_length=50
	)
	nombre_comercial = models.CharField(
		verbose_name="Nombre Comercial*",
		max_length=50
	)
	domicilio_empresa = models.CharField(
		verbose_name="Domicilio*",
		max_length=50
	)
	codigo_postal = models.CharField(
		verbose_name="Código postal*",
		max_length=4
	)
	cuit = models.BigIntegerField(
		verbose_name="C.U.I.T.*"
	)
	ingresos_bruto = models.CharField(
		verbose_name="Ing. Bruto*",
		max_length=15
	)
	inicio_actividad = models.DateField(
		verbose_name="Inicio de actividad*"
	)
	telefono = models.CharField(
		verbose_name="Teléfono*",
		max_length=20
	)
	email_empresa = models.EmailField(
		verbose_name="Correo*",
		max_length=50
	)
	web_empresa = models.CharField(
		verbose_name="Web",
		max_length=50,
		null=True,
		blank=True
	)
	logo_empresa = models.ImageField(
		verbose_name="Logo",
		upload_to=logo_upload_path,
		null=True,
		blank=True,
		max_length=255,
		help_text="Formatos permitidos: JPG, PNG, GIF. Tamaño máximo: 2MB"
	)
	
	
	class Meta:
		db_table = 'empresa'
		verbose_name = 'Empresa'
		verbose_name_plural = 'Empresas'
		ordering = ['nombre_fiscal']
	
	def __str__(self):
		return self.nombre_fiscal
	
	@property
	def logo_url_safe(self):
		"""
		Retorna la URL del logo de forma segura.
		Verifica que el campo tenga valor y que el archivo exista físicamente.
		"""
		
		if not self.logo_empresa:
			return None
		
		try:
			#-- Verificar que el archivo existe en el sistema de archivos
			if hasattr(self.logo_empresa, 'path') and os.path.isfile(self.logo_empresa.path):
				return self.logo_empresa.url
			else:
				return None
		except (ValueError, OSError, AttributeError):
			return None
	
	@property
	def logo_path_safe(self):
		"""
		Retorna la ruta física del logo de forma segura.
		Verifica que el campo tenga valor y que el archivo exista físicamente.
		"""
		
		if not self.logo_empresa:
			return None
		
		try:
			#-- Verificar que el archivo existe en el sistema de archivos.
			if hasattr(self.logo_empresa, 'path') and os.path.isfile(self.logo_empresa.path):
				return self.logo_empresa.path
			else:
				return None
		except (ValueError, OSError, AttributeError):
			return None
	
	@property
	def logo_name_safe(self):
		"""
		Retorna el nombre del archivo del logo de forma segura.
		"""
		
		if not self.logo_empresa:
			return None
		
		try:
			#-- Reutilizar la validación.
			if self.logo_url_safe:
				return self.logo_empresa.name
			else:
				return None
		except (ValueError, OSError, AttributeError):
			return None
		
	@property
	def has_logo(self):
		"""
		Indica si la empresa tiene un logo válido.
		"""
		
		return self.logo_url_safe is not None
	
	def clean(self):
		super().clean()
		
		errors = {}
		
		interes_str = str(self.interes) if self.interes is not None else ""
		interes_dolar_str = str(self.interes_dolar) if self.interes_dolar is not None else ""
		cotizacion_dolar_str = str(self.cotizacion_dolar) if self.cotizacion_dolar is not None else ""
		dias_vencimiento_str = str(self.dias_vencimiento) if self.dias_vencimiento is not None else ""
		descuento_maximo_str = str(self.descuento_maximo) if self.descuento_maximo is not None else ""
		
		try:
			validar_cuit(self.cuit)
		except ValidationError as e:
			errors['cuit'] = e.messages
		
		if not re.match(r'^\d{1,22}$', str(self.cbu)):
			errors.update({'cbu': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 22.'})
		
		if not re.match(r'^\+?\d[\d ]{0,19}$', str(self.telefono)):
			errors.update({'telefono': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 20, el signo + y espacios.'})
		
		if not re.match(r'^-?(0|[1-9]\d{0,1})(\.\d{1,2})?$', interes_str):
			errors.update({'interes': 'El valor debe ser un número negativo o positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^-?(0|[1-9]\d{0,1})(\.\d{1,2})?$', interes_dolar_str):
			errors.update({'interes_dolar': 'El valor debe ser un número negativo o positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^(0|[1-9]\d{0,13})(\.\d{1,2})?$', cotizacion_dolar_str):
			errors.update({'cotizacion_dolar': 'El valor debe ser positivo, con hasta 13 dígitos enteros y hasta 2 decimales o cero.'})
		
		if not re.match(r'^[1-9]\d{0,2}$|^0$', dias_vencimiento_str):
			errors.update({'dias_vencimiento': 'El valor debe ser un número entero positivo, con hasta 3 dígitos o cero.'})
		
		if not re.match(r'^-?(0|[1-9]\d{0,1})(\.\d{1,2})?$', descuento_maximo_str):
			errors.update({'descuento_maximo': 'El valor debe ser un número negativo o positivo, con hasta 2 dígitos enteros y hasta 2 decimales o cero.'})
		
		if errors:
			raise ValidationError(errors)
	
	@property
	def cuit_formateado(self):
		cuit = str(self.cuit)
		return f"{cuit[:2]}-{cuit[2:-1]}-{cuit[-1:]}"
	
	def save(self, *args, **kwargs):
		"""Sobrescribir save para manejar el logo"""
		
		#-- Si es un nuevo registro, guardar temporalmente.
		is_new = self.pk is None
		
		#-- Si es un registro existente y el logo ha cambiado, eliminar el anterior
		if not is_new and hasattr(self, '_old_logo'):
			old_logo = self._old_logo
			if old_logo and old_logo != self.logo_empresa:
				if os.path.isfile(old_logo.path):
					try:
						os.remove(old_logo.path)
					except Exception as e:
						print(f"Error al eliminar logo antiguo: {e}")
		
		#-- Guardar el objeto.
		super().save(*args, **kwargs)
		
		#-- Si es nuevo y hay logo, actualizar la ruta con el ID correcto.
		if is_new and self.logo_empresa:
			try:
				old_path = self.logo_empresa.path
				#-- Obtener la extensión del archivo.
				ext = self.logo_empresa.name.split('.')[-1]
				new_name = f'empresas/logos/logo_{self.pk}.{ext}'
				
				#-- Si el archivo existe y no está en la ubicación correcta.
				if os.path.exists(old_path):
					#-- Crear la nueva ruta.
					new_path = os.path.join(os.path.dirname(old_path), f'logo_{self.pk}.{ext}')
					#-- Renombrar el archivo.
					os.rename(old_path, new_path)
					#-- Actualizar el nombre en la base de datos.
					self.logo_empresa.name = new_name
					#-- Guardar sin recursión infinita.
					super().save(update_fields=['logo_empresa'])
			except Exception as e:
				print(f"Error al renombrar logo: {e}")

	def __init__(self, *args, **kwargs):
		"""Sobrescribir init para guardar el logo antiguo"""
		
		super().__init__(*args, **kwargs)
		#-- Guardar una referencia al logo actual para poder comparar después.
		if self.pk:
			self._old_logo = self.logo_empresa
		else:
			self._old_logo = None