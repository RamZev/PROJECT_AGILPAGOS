# neumatic\apps\maestros\models\valida_models.py
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import time
from django.utils import timezone

from .base_gen_models import ModeloBaseGenerico
from .sucursal_models import Sucursal
from entorno.constantes_base import ESTATUS_GEN

class Valida(ModeloBaseGenerico):
	id_valida = models.AutoField(primary_key=True)
	estatus_valida = models.BooleanField(
		verbose_name="Estatus",
		default=True,
		choices=ESTATUS_GEN
	)
	id_sucursal = models.ForeignKey(
		Sucursal,
		on_delete=models.CASCADE,
		null=True, 
		blank=True,
		verbose_name="Sucursal*"
	)
	fecha_valida = models.DateField(
		'Fecha',
		blank=True,
		null=True
	)
	hora_valida = models.TimeField(
		'Hora',
		blank=True,
		null=True
	)
	solicitado = models.CharField(
		'Solicitado por',
		max_length=20
	)
	hs = models.TimeField(
		'Hora Aplicación',
		null=True,
		blank=True
	)
	validacion = models.CharField(
		verbose_name='Validación',
		max_length=4,
		blank=True,
		null=True
	)
	
	class Meta:
		verbose_name = 'Validación'
		verbose_name_plural = 'Validaciones'
		db_table = 'valida'
	
	def __str__(self):
		return f"({self.fecha_valida})"  # Corregido
	
	def save(self, *args, **kwargs):
		#-- Asigna fecha y hora actual solo si no tienen valor (o siempre, según tu necesidad).
		if not self.fecha_valida:
			self.fecha_valida = timezone.now().date()
		if not self.hora_valida:
			self.hora_valida = timezone.now().time()
		
		#-- Llama al método save() de la clase padre para guardar el objeto.
		super().save(*args, **kwargs)