# homemutual/apps/transacciones/models/transacciones_models.py
from django.db import models
from django.core.exceptions import ValidationError

from apps.maestros.models.sg_catalogo_models import (
	SgEstadoTransaccion,
	SgConceptoTransaccion,
	SgTipoOperacionAviso,
	SgTipoImpuesto,
)
from apps.maestros.models.cuenta_cvu_models import CuentaCvu
from apps.maestros.models.socio_models import Socio
from entorno.constantes_base import TIPO_MOVIMIENTO_CHOICES


# ============================================================================
# MOVIMIENTO
# ----------------------------------------------------------------------------
# Tabla única donde se asientan todos los movimientos que afectan el saldo
# de una CVU: CASH_OUT, CASH_IN, REVERSA, IMPUESTO, AJUSTE.
#
# El eje de agrupación de una transacción completa es id_transaccion_entidad
# (UUID v7 generado por la API Intermedia). Todos los movimientos derivados
# de una misma solicitud comparten ese valor.
# ============================================================================
class Movimiento(models.Model):
	id_movimiento = models.BigAutoField(
		primary_key=True
	)
	
	#-- Eje de la transacción (UUID v7 generado por la API Intermedia).
	id_transaccion_entidad = models.UUIDField(
		db_index=True,
		help_text="UUID v7 generado por la API Intermedia. Agrupa todos los "
				"movimientos de una misma transacción.",
	)
	
	tipo_movimiento = models.CharField(
		max_length=20,
		choices=TIPO_MOVIMIENTO_CHOICES,
	)
	
	#-- Relación con la CVU y el socio.
	id_cuenta_cvu = models.ForeignKey(
		CuentaCvu,
		on_delete=models.PROTECT,
		db_column="id_cuenta_cvu",
		null=True,
		blank=True,
		related_name="movimientos",
	)
	id_socio = models.ForeignKey(
		Socio,
		on_delete=models.PROTECT,
		db_column="id_socio",
		null=True,
		blank=True,
		related_name="movimientos",
	)
	#-- Denormalizado para consultas rápidas y conciliación.
	numero_cuenta_entidad = models.CharField(
		max_length=30,
		db_index=True,
		help_text="numeroCuentaEntidad de la CVU afectada.",
	)
	
	#-- Datos de la transacción.
	importe = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00,
	)
	fecha = models.DateTimeField(auto_now_add=True)
	id_estado_transaccion = models.ForeignKey(
		SgEstadoTransaccion,
		on_delete=models.PROTECT,
		db_column="id_estado_transaccion",
		null=True,
		blank=True,
	)
	
	#-- Conciliación.
	conciliado = models.BooleanField(
		default=False
	)
	conciliado_at = models.DateTimeField(
		null=True,
		blank=True
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
	
	#-- Identificadores externos.
	id_transaccion_agilpagos = models.CharField(
		max_length=36,
		null=True,
		blank=True,
		db_index=True,
		help_text="GUID 'id' devuelto por Agilpagos en la respuesta de la transacción.",
	)
	id_transaccion_coelsa = models.CharField(
		max_length=60,
		null=True,
		blank=True,
		db_index=True,
	)
	
	observaciones = models.CharField(
		max_length=255,
		blank=True,
		default="",
	)
	
	class Meta:
		db_table = "movimiento"
		verbose_name = "Movimiento"
		verbose_name_plural = "Movimientos"
		ordering = ["-fecha"]
		indexes = [
			models.Index(fields=["id_transaccion_entidad"], name="ix_mov_trx_entidad"),
			models.Index(fields=["numero_cuenta_entidad"], name="ix_mov_nro_cta"),
			models.Index(fields=["fecha"], name="ix_mov_fecha"),
			models.Index(fields=["tipo_movimiento"], name="ix_mov_tipo"),
			models.Index(fields=["conciliado"], name="ix_mov_conciliado"),
		]
	
	def __str__(self):
		return f"Movimiento {self.id_movimiento} - {self.tipo_movimiento} - {self.importe}"


# ============================================================================
# CASHOUT REQUEST
# ----------------------------------------------------------------------------
# Datos de entrada de una solicitud de transferencia (CashOut) hacia
# Agilpagos. Se persiste ANTES de llamar a la API, para tener trazabilidad.
# El id_transaccion_entidad es el UUID v7 que también se envía a Agilpagos
# como IdTransaccionEntidad.
# ============================================================================
# Modelo base de Transferencias
class CashoutRequest(models.Model):
	id_cashout_request = models.BigAutoField(
		primary_key=True
	)
	
	#-- Eje de la transacción.
	# este lo genera la API (no en plantilla)
	id_transaccion_entidad = models.UUIDField(
		unique=True,
		db_index=True,
		help_text="UUID v7 generado por la API Intermedia.",
	)
	
	#-- Cuenta origen.
	# Aqui hay validaciones
	# Estado activo
	# Sin fecha de baja
	# No bloquedao por compliance
	# Que haya saldo para el importe solicitado
	cvu_debito = models.CharField(
		max_length=22,
		db_index=True,
		help_text="CVU de la cuenta origen.",
	)
 
	# No va en la plantilla
	numero_cuenta_entidad = models.CharField(
		max_length=30,
		db_index=True,
		help_text="numeroCuentaEntidad de la CVU origen.",
	)
	
	#-- Datos de la contraparte. (quien recibe)
	# Mostrar readonly y viene de la consulta el cvu
	cuit_credito = models.BigIntegerField(
		verbose_name="CUIT del beneficiario",
	)
	# Se introduce en la plantilla, pero no se persiste. Se obtiene de la consulta a Agilpagos.
	cbu_credito = models.CharField(
		verbose_name="CVU/CBU del beneficiario",
		max_length=22,
	)
	# Mostrar readonly y viene de la consulta el cvu
	nombre_credito = models.CharField(
		verbose_name="Nombre del beneficiario",
		max_length=40,
		null=True,
		blank=True,
	)
	
	#-- Datos de la operación.
	# Se selecciona
	id_concepto = models.ForeignKey(
		SgConceptoTransaccion,
		on_delete=models.PROTECT,
		db_column="id_concepto",
	)
	# Mayor a 0, con 2 decimales y menor o igual al saldo
	importe = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00,
	)
	# Obligatorio
	descripcion = models.CharField(
		max_length=50
	)
	# Obligatorio
	observaciones = models.CharField(
		max_length=50,
		blank=True,
		default="",
	)
	
	#-- Timestamps.
	creado_at = models.DateTimeField(
		auto_now_add=True
	)
	
	class Meta:
		db_table = "cashout_request"
		verbose_name = "Cashout Request"
		verbose_name_plural = "Cashout Requests"
		ordering = ["-creado_at"]
		indexes = [
			models.Index(fields=["id_transaccion_entidad"], name="ix_coutreq_trx"),
			models.Index(fields=["cvu_debito"], name="ix_coutreq_cvu"),
		]
	
	def __str__(self):
		return f"CashoutRequest {self.id_transaccion_entidad} - ${self.importe}"


# ============================================================================
# CASHOUT RESPONSE
# ----------------------------------------------------------------------------
# Respuesta de Agilpagos a una solicitud de CashOut. Se persiste DESPUÉS
# de recibir la respuesta, en la misma transacción que los movimientos.
# ============================================================================
class CashoutResponse(models.Model):
	id_cashout_response = models.BigAutoField(
		primary_key=True
	)
	
	#-- Relación 1:1 con el request (por el UUID de transacción).
	id_transaccion_entidad = models.OneToOneField(
		CashoutRequest,
		on_delete=models.PROTECT,
		to_field="id_transaccion_entidad",
		db_column="id_transaccion_entidad",
		related_name="response",
	)
	
	#-- Parte débito.
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
		blank=True,
	)
	total_debito = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00,
	)
	
	#-- Parte crédito (puede ser null si la contraparte es externa).
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
		blank=True,
	)
	total_credito = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		null=True,
		blank=True,
		default=0.00,
	)
	
	#-- Referencia interbancaria.
	id_coelsa = models.CharField(
		max_length=60,
		null=True,
		blank=True,
		db_index=True,
	)
	
	creado_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		db_table = "cashout_response"
		verbose_name = "Cashout Response"
		verbose_name_plural = "Cashout Responses"
		indexes = [
			models.Index(fields=["id_transaccion_entidad"], name="ix_coutres_trx"),
			models.Index(fields=["id_coelsa"], name="ix_coutres_coelsa"),
		]
	
	def __str__(self):
		return f"CashoutResponse {self.id_transaccion_entidad}"


# ============================================================================
# MOVIMIENTO IMPUESTO
# ----------------------------------------------------------------------------
# Impuestos (SIRCUPA, Ley 25.413, etc.) retenidos por Agilpagos sobre una
# transacción. Cada impuesto tiene su propio idTransaccion (GUID) y se
# vincula a la transacción originante.
# ============================================================================
class MovimientoImpuesto(models.Model):
	id_movimiento_impuesto = models.BigAutoField(
		primary_key=True
	)
	
	#-- Eje de la transacción (mismo que el CashoutRequest).
	id_transaccion_entidad = models.UUIDField(
		db_index=True,
		help_text="UUID v7 de la transacción originante (CashoutRequest).",
	)
	
	#-- Datos del impuesto.
	id_transaccion_impuesto = models.UUIDField(
		help_text="ID de la retención en sí (Agilpagos).",
	)
	id_transaccion_originante = models.UUIDField(
		help_text="A qué transacción de crédito/débito se vincula.",
	)
	importe = models.DecimalField(
		max_digits=15,
		decimal_places=2
	)
	id_tipo_transaccion = models.SmallIntegerField(
		help_text="1=Débito 2=Crédito 3=Reversa débito 4=Reversa crédito",
	)
	id_web_operacion = models.ForeignKey(
		SgTipoImpuesto,
		on_delete=models.PROTECT,
		db_column="id_web_operacion",
	)
	
	class Meta:
		db_table = "movimiento_impuesto"
		verbose_name = "Movimiento Impuesto"
		verbose_name_plural = "Movimientos Impuestos"
		ordering = ["-id_movimiento_impuesto"]
		constraints = [
			models.UniqueConstraint(
				fields=["id_transaccion_impuesto"],
				name="uniq_movimiento_impuesto_transaccion",
			),
		]
		indexes = [
			models.Index(fields=["id_transaccion_entidad"], name="ix_movimp_trx"),
		]
	
	def __str__(self):
		return f"MovimientoImpuesto {self.id_movimiento_impuesto} - ${self.importe}"


# ============================================================================
# SALDO CVU
# ----------------------------------------------------------------------------
# Saldo de una CVU. Se separa saldo contable (saldo) de importe retenido
# (saldo_retenido) para implementar la retención de saldos hasta que la
# transacción alcance un estado final (según doc Agilpagos, punto 2.4.7).
#
# Saldo disponible = saldo - saldo_retenido.
# ============================================================================
class SaldoCvu(models.Model):
	id_saldo_cvu = models.BigAutoField(
		primary_key=True
	)
	
	#-- Relación 1:1 con la CVU.
	id_cuenta_cvu = models.OneToOneField(
		CuentaCvu,
		on_delete=models.PROTECT,
		db_column="id_cuenta_cvu",
		related_name="saldo",
	)
	id_socio = models.ForeignKey(
		Socio,
		on_delete=models.PROTECT,
		db_column="id_socio",
		related_name="saldos_cvu",
	)
	numero_cuenta_entidad = models.CharField(
		max_length=30,
		unique=True,
		db_index=True,
	)
	
	#-- Saldos.
	saldo = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		default=0.00,
		help_text="Saldo contable de la CVU (ya refleja las operaciones "
				"en estado final).",
	)
	saldo_retenido = models.DecimalField(
		max_digits=15,
		decimal_places=2,
		default=0.00,
		help_text="Importe retenido por transacciones pendientes de "
				"confirmación.",
	)
	
	#-- Control de actualización.
	actualizado_at = models.DateTimeField(
		auto_now=True
	)
	
	class Meta:
		db_table = "saldo_cvu"
		verbose_name = "Saldo Cvu"
		verbose_name_plural = "Saldos Cvu"
		indexes = [
			models.Index(fields=["numero_cuenta_entidad"], name="ix_saldo_nro_cta"),
		]
	
	@property
	def saldo_disponible(self):
		"""Saldo que el socio puede usar (contable - retenido)."""
		return (self.saldo or 0) - (self.saldo_retenido or 0)
	
	def __str__(self):
		return f"SaldoCvu {self.numero_cuenta_entidad} - ${self.saldo} (ret: ${self.saldo_retenido})"