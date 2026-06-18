# homemutual\apps\maestros\models\sucursal_models.py
from django.db import models
from django.core.exceptions import ValidationError
import re
from .base_gen_models import ModeloBaseGenerico
from entorno.constantes_base import ESTATUS_GEN


class Sucursal(ModeloBaseGenerico):
	id_sucursal = models.AutoField(primary_key=True)
	estatus_sucursal = models.BooleanField("Estatus", default=True,
										   choices=ESTATUS_GEN)
	nombre_sucursal = models.CharField("Nombre sucursal", max_length=50)
	domicilio_sucursal = models.CharField("Domicilio", max_length=50)
	telefono_sucursal = models.CharField("Teléfono", max_length=15)
	email_sucursal = models.EmailField("Correo", max_length=50)
	ws_url = models.CharField("WebService URL", max_length=50)
	ws_token_acceso = models.CharField("Token Acceso", max_length=50)

	class Meta:
		db_table = 'sucursal'
		verbose_name = ('Sucursal')
		verbose_name_plural = ('Sucursales')
		ordering = ['nombre_sucursal']

	def __str__(self):
		return self.nombre_sucursal
	
	def clean(self):
		super().clean()
		
		errors = {}
				
		if not re.match(r'^\+?\d[\d ]{0,14}$', str(self.telefono_sucursal)):
			errors.update({'telefono_sucursal': 'Debe indicar sólo dígitos numéricos positivos, mínimo 1 y máximo 15, el signo + y espacios.'})
		
		if errors:
			raise ValidationError(errors)
