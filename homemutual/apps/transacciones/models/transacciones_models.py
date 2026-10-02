# homemutual\apps\transacciones\models\transacciones_models.py
from django.db import models
from django.core.exceptions import ValidationError

from apps.maestros.models.sg_catalogo_models import (
	SgEstadoTransaccion,
	SgConceptoTransaccion,
	SgTipoOperacionAviso,
	SgTipoImpuesto
)
from apps.maestros.models.cuenta_cvu_models import CuentaCvu
from apps.maestros.models.socio_models import Socio
from entorno.constantes_base import TIPO_MOVIMIENTO_CHOICES


class Movimiento(models.Model):
	
	id_movimiento = models.BigAutoField(
		primary_key=True
	)
	tipo_movimiento = models.CharField(
		max_length=20,
		choices=TIPO_MOVIMIENTO_CHOICES
	)
	#-- Identificación del socio y CVU.
	id_cuenta_cvu = models.ForeignKey(
		CuentaCvu,
		on_delete=models.PROTECT,
		db_column="id_cuenta_cvu",
		null=True,
		blank=True,
	)
	numero_cuenta_entidad = models.CharField(
		max_length=30,
		unique=True
	)
	#-- Datos de la transacción.
	importe = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00
	)
	fecha = models.DateTimeField(
		auto_now_add=True
	)
	id_estado_transaccion = models.ForeignKey(
		SgEstadoTransaccion,
		on_delete=models.PROTECT,
		db_column="id_estado_transaccion",
		null=True,
		blank=True,
	)
	conciliado = models.BooleanField(
		default=False
	)
	#-- Sincronización con VFP / contabilidad Mutual.
	sincronizado_vfp = models.BooleanField(
		default=False
	)
	sincronizado_vfp_at = models.DateTimeField(
		null=True,
		blank=True
	)
	comprobante_vfp_id = models.BigIntegerField(
		null=True,
		blank=True
	)
	
	id_transaccion_agilpagos = models.BigIntegerField(
		null=True,
		blank=True
	)
	observaciones = models.CharField(
		max_length=255
	)
	
	class Meta:
		db_table = "movimiento"
		# managed = True  # pon False si la tabla la maneja otro sistema
		verbose_name = 'Movimiento'
		verbose_name_plural = 'Movimientos'
	
	def __str__(self):
		return f"Movimiento {self.id_movimiento} - {self.tipo_movimiento}"


class CashoutRequest(models.Model):
	id_cashout_request = models.BigAutoField(
		primary_key=True
	)
	id_movimiento = models.ForeignKey(
		Movimiento,
		on_delete=models.PROTECT,
		db_column="id_movimiento"
	)
	cuit_credito = models.BigIntegerField(
		verbose_name="CUIT del beneficiario"
	)
	cbu_credito = models.CharField(
		verbose_name="CVU/CBU del beneficiario",
		max_length=22
	)
	nombre_credito = models.CharField(
		verbose_name="Nombre del beneficiario",
		max_length=40,
		null=True, blank=True
	)
	id_concepto = models.ForeignKey(
		SgConceptoTransaccion,
		on_delete=models.PROTECT,
		db_column="id_concepto",
	)
	importe = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00
	)
	descripcion = models.CharField(
		max_length=255
	)
	observaciones = models.CharField(
		max_length=255
	)
	id_transaccion_entidad = models.UUIDField()
	creado_at = models.DateTimeField(
		auto_now_add=True
	)
	
	class Meta:
		db_table = "cashout_request"
		verbose_name = 'Cashout Request'
		verbose_name_plural = 'Cashout Requests'
	
	def __str__(self):
		return f"CashoutRequest {self.id_cashout_request}"


class CashoutResponse(models.Model):
	id_cashout_response = models.BigAutoField(
		primary_key=True
	)
	id_movimiento = models.ForeignKey(
		Movimiento,
		on_delete=models.PROTECT,
		db_column="id_movimiento",
		null=True,
		blank=True,
	)
	id_debito = models.UUIDField(
		null=True,
		blank=True
	)
	id_estado_debito = models.ForeignKey(
		SgEstadoTransaccion,
		on_delete=models.PROTECT,
		db_column="id_estado_debito",
		related_name="cashout_response_debito",
		null=True,
		blank=True,
	)
	error_coelsa_debito = models.CharField(
		max_length=255,
		null=True,
		blank=True
	)
	total_debito = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00
	)
	id_credito = models.UUIDField(
		null=True,
		blank=True
	)
	id_estado_credito = models.ForeignKey(
		SgEstadoTransaccion,
		on_delete=models.PROTECT,
		db_column="id_estado_credito",
		related_name="cashout_response_credito",
		null=True,
		blank=True,
	)
	error_coelsa_credito = models.CharField(
		max_length=255,
		null=True,
		blank=True
	)
	total_credito = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00
	)
	id_coelsa = models.CharField(
		max_length=60,
		null=True,
		blank=True
	)
	
	class Meta:
		db_table = "cashout_response"
		verbose_name = 'Cashout Response'
		verbose_name_plural = 'Cashout Responses'
	
	def __str__(self):
		return f"CashoutResponse {self.id_cashout_response}"


class CashinRequest(models.Model):
	id_cashin_request = models.BigAutoField(
		primary_key=True
	)
	id_movimiento = models.ForeignKey(
		Movimiento,
		on_delete=models.PROTECT,
		db_column="id_movimiento",
		null=True,
		blank=True,
	)
	
	id_transaccion = models.UUIDField(
		null=True,
		blank=True
	)
	id_transaccion_anulada = models.UUIDField(
		null=True,
		blank=True
	)
	id_transaccion_originante = models.BigIntegerField(
		null=True,
		blank=True
	)
	id_transaccion_entidad = models.BigIntegerField(
		null=True,
		blank=True
	)
	id_entidad = models.UUIDField(
		null=True,
		blank=True
	)
	id_tipo_transaccion = models.SmallIntegerField(
		null=True,
		blank=True,
		help_text="1: Débito; 2: Crédito; 3: Reversa Débito; 4: Reversa Crédito",
	)
	id_web_operacion = models.ForeignKey(
		SgTipoOperacionAviso,
		on_delete=models.PROTECT,
		db_column="id_web_operacion",
		null=True,
		blank=True,
	)
	importe = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00
	)
	total = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00
	)
	id_moneda = models.SmallIntegerField(
		default=1
	)
	fecha_operacion = models.DateTimeField()
	fecha_contable = models.DateTimeField(
		null=True,
		blank=True
	)
	observaciones = models.CharField(
		max_length=255,
		null=True,
		blank=True
	)
	numero_cuenta = models.CharField(
		max_length=30
	)
	cvu = models.CharField(
		max_length=22
	)
	cuenta_bloqueada = models.BooleanField(
		default=False
	)
	id_coelsa = models.CharField(
		max_length=60,
		null=True,
		blank=True
	)
	#-- Contraparte.
	cuenta_contraparte = models.CharField(
		max_length=30,
		null=True,
		blank=True
	)
	cuit_contraparte = models.BigIntegerField(
		null=True,
		blank=True
	)
	titular_contraparte = models.CharField(
		max_length=40,
		null=True,
		blank=True
	)
	
	class Meta:
		db_table = "cashin_request"
		verbose_name = 'Cashin Request'
		verbose_name_plural = 'Cashin Requests'
	
	def __str__(self):
		return f"CashinRequest {self.id_cashin_request}"


class MovimientoImpuesto(models.Model):
	id_movimiento_impuesto = models.BigAutoField(
		primary_key=True
	)
	id_movimiento = models.ForeignKey(
		Movimiento,
		on_delete=models.PROTECT,
		db_column="id_movimiento",
		null=True,
		blank=True,
	)
	
	id_transaccion_impuesto = models.UUIDField(
		help_text="id de la retención en sí (Agilpagos)"
	)
	id_transaccion_originante = models.UUIDField(
		help_text="a qué transacción de crédito/débito se vincula"
	)
	importe = models.DecimalField(max_digits=15, decimal_places=2)
	id_tipo_transaccion = models.SmallIntegerField(
		help_text="1=Débito 2=Crédito 3=Reversa débito 4=Reversa crédito"
	)
	id_web_operacion = models.ForeignKey(
		SgTipoImpuesto,
		on_delete=models.PROTECT,
		db_column="id_web_operacion",
	)
	
	class Meta:
		db_table = "movimiento_impuesto"
		verbose_name = 'Movimiento Impuesto'
		verbose_name_plural = 'Movimientos Impuesto'
		constraints = [
			models.UniqueConstraint(
				fields=["id_transaccion_impuesto"],
				name="uniq_movimiento_impuesto_transaccion",
			)
		]
	
	def __str__(self):
		return f"MovimientoImpuesto {self.id_movimiento_impuesto}"


class SaldoCvu(models.Model):
	id_saldo_cvu = models.BigAutoField(
		primary_key=True
	)
	id_cuenta_cvu = models.ForeignKey(
		CuentaCvu,
		on_delete=models.PROTECT,
		db_column="id_cuenta_cvu",
	)
	id_socio = models.ForeignKey(
		Socio,
		on_delete=models.PROTECT,
		db_column="id_socio",
	)
	numero_cuenta_entidad = models.CharField(
		max_length=30,
		unique=True
	)
	saldo = models.DecimalField(
		max_digits=15,
		decimal_places=2
	)
	
	class Meta:
		db_table = "saldo_cvu"
		verbose_name = 'Saldo Cvu'
		verbose_name_plural = 'Saldos Cvu'
	
	def __str__(self):
		return f"SaldoCvu {self.id_saldo_cvu} - {self.numero_cuenta_entidad}"
