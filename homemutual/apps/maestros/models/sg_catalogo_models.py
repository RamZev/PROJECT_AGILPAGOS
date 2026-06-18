# homemutual\apps\models\sg_catalogo_models.py
from django.db import models
from django.core.exceptions import ValidationError
from .base_gen_models import ModeloBaseGenerico
from entorno.constantes_base import ESTATUS_GEN


class SgEntidadTipoDocumento(ModeloBaseGenerico):
	id_sg_entidad_tipo_documento = models.CharField(primary_key=True, max_length=36)
	estatus_sg_entidad_tipo_documento = models.BooleanField("Estatus", default=True,
										   choices=ESTATUS_GEN)
	nombre = models.CharField("Nombre Entidad Tipo Documento", max_length=60)

	class Meta:
		db_table = 'sg_entidad_tipo_documento'
		verbose_name = ('SG Entidad Tipo Documento')
		verbose_name_plural = ('SG Entidad Tipo Documento')
		ordering = ['nombre']

	def __str__(self):
		return self.nombre
	

class SgTipoPersona(ModeloBaseGenerico):
	id_sg_tipo_persona = models.CharField(primary_key=True, max_length=36)
	estatus_sg_tipo_persona = models.BooleanField("Estatus", default=True,
										   choices=ESTATUS_GEN)
	tipo_persona = models.CharField("Tipo Persona", max_length=60)

	class Meta:
		db_table = 'sg_tipo_persona'
		verbose_name = ('SG Tipo Persona')
		verbose_name_plural = ('SG Tipos Personas')
		ordering = ['tipo_persona']

	def __str__(self):
		return self.tipo_persona
	
class SgTipoCuenta(ModeloBaseGenerico):
	id_sg_tipo_cuenta = models.CharField(primary_key=True, max_length=36)
	estatus_sg_tipo_cuenta = models.BooleanField("Estatus", default=True,
										   choices=ESTATUS_GEN)
	tipo_cuenta = models.CharField("Tipo Cuenta", max_length=60)

	class Meta:
		db_table = 'sg_tipo_cuenta'
		verbose_name = ('SG Tipo Cuenta')
		verbose_name_plural = ('SG Tipos Cuentas')
		ordering = ['tipo_cuenta']

	def __str__(self):
		return self.tipo_cuenta

