# homemutual/apps/maestros/models/agenda_destinatarios_models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from .base_gen_models import ModeloBaseGenerico
from .socio_models import Socio


class AgendaDestinatario(ModeloBaseGenerico):
	"""
	Agenda de destinatarios frecuentes de un socio.
	
	Guarda los datos de CVUs/CBUs de terceros a los que el socio
	transfiere habitualmente, para evitar consultar Agilpagos en cada
	transferencia (endpoint 8.1, con costo adicional en PROD).
	
	El registro se crea cuando:
	1. El socio hace una transferencia exitosa a un destinatario.
	2. El formulario tenía marcado el check "Guardar en agenda".

	Es responsabilidad de la API Intermedia persistir estos datos
	después de una transferencia exitosa.
	"""
	
	# ============================================
	# 1. IDENTIFICADORES
	# ============================================
	id_agenda_destinatario = models.AutoField(
		primary_key=True,
		verbose_name="ID Agenda Destinatario",
	)
	
	# ============================================
	# 2. RELACIONES
	# ============================================
	id_socio = models.ForeignKey(
		Socio,
		on_delete=models.CASCADE,
		related_name='agenda_destinatarios',
		verbose_name="Socio",
		help_text="Socio propietario de esta entrada de la agenda.",
	)
	
	# ============================================
	# 3. DATOS DEL DESTINATARIO
	# ============================================
	cvu_o_cbu = models.CharField(
		"CVU o CBU",
		max_length=22,
		help_text="22 dígitos. Puede ser CVU de Agilpagos o CBU bancario.",
	)
	alias = models.CharField(
		"Alias referencial",
		max_length=60,
		blank=True,
		null=True,
		help_text=(
			"Alias que el propietario de la agenda le asigna al destinatario "
			"para identificarlo fácilmente (ej: 'Cuñado Juan', 'Proveedor'). "
			"NO es el alias de la CVU en Agilpagos."
		),
	)
	cuit = models.CharField(
		"CUIT del titular",
		max_length=11,
		help_text="CUIT del titular principal de la cuenta destino.",
	)
	nombre = models.CharField(
		"Nombre del titular",
		max_length=100,
		help_text="Nombre del titular principal.",
	)
	tipo_persona = models.CharField(
		"Tipo de persona",
		max_length=10,
		blank=True,
		null=True,
		help_text="FISICA o JURIDICA. Puede ser null si se desconoce.",
	)
	
	# ============================================
	# 4. METADATA
	# ============================================
	es_favorita = models.BooleanField(
		"Favorita",
		default=False,
		help_text="Destinatario marcado como favorito (destacado en la lista).",
	)
	veces_usada = models.PositiveIntegerField(
		"Veces usada",
		default=0,
		help_text="Cantidad de transferencias exitosas a este destinatario.",
	)
	ultima_vez_usada = models.DateTimeField(
		"Última vez usada",
		blank=True,
		null=True,
		help_text="Fecha de la última transferencia exitosa.",
	)
	observaciones = models.CharField(
		"Observaciones",
		max_length=255,
		blank=True,
		null=True,
		help_text="Ej: 'Proveedor de insumos', 'Cuñado', etc.",
	)
	
	# ============================================
	# 5. MÉTODOS
	# ============================================
	def registrar_uso(self):
		"""
		Registra un uso exitoso de este destinatario.
		Incrementa el contador y actualiza la fecha de último uso.
	
		IMPORTANTE: este método NO hace `save()`. El llamador debe
		llamar a `save()` después para persistir los cambios, dentro
		de la transacción atómica correspondiente.
		"""
		self.veces_usada = (self.veces_usada or 0) + 1
		self.ultima_vez_usada = timezone.now()
	
	def clean(self):
		super().clean()
		errors = {}
		
		#-- Validar longitud de CVU/CBU.
		if self.cvu_o_cbu and len(self.cvu_o_cbu) != 22:
			errors['cvu_o_cbu'] = 'El CVU/CBU debe tener exactamente 22 dígitos.'
		
		#-- Validar que CVU/CBU sea numérico.
		if self.cvu_o_cbu and not self.cvu_o_cbu.isdigit():
			errors['cvu_o_cbu'] = 'El CVU/CBU debe contener solo dígitos numéricos.'
		
		#-- Validar longitud y formato de CUIT.
		if self.cuit:
			if len(self.cuit) != 11:
				errors['cuit'] = 'El CUIT debe tener exactamente 11 dígitos.'
			elif not self.cuit.isdigit():
				errors['cuit'] = 'El CUIT debe contener solo dígitos numéricos.'
		
		#-- Validar unicidad del par (id_socio, cvu_o_cbu).
		if self.id_socio_id and self.cvu_o_cbu:
			qs = AgendaDestinatario.objects.filter(
				id_socio_id=self.id_socio_id,
				cvu_o_cbu=self.cvu_o_cbu,
			)
			if self.pk:
				qs = qs.exclude(pk=self.pk)
			if qs.exists():
				errors['cvu_o_cbu'] = (
					'Ya existe un destinatario con ese CVU/CBU en tu agenda.'
				)
		
		if errors:
			raise ValidationError(errors)
	
	# ============================================
	# 6. META
	# ============================================
	class Meta:
		db_table = 'agenda_destinatario'
		verbose_name = 'Agenda Destinatario'
		verbose_name_plural = 'Agenda Destinatarios'
		ordering = ['-es_favorita', '-ultima_vez_usada', 'nombre']
		constraints = [
			models.UniqueConstraint(
				fields=['id_socio', 'cvu_o_cbu'],
				name='uq_agenda_destinatario_socio_cvu',
			),
		]
		indexes = [
			models.Index(fields=['id_socio', 'cvu_o_cbu'], name='ix_agenda_socio_cvu'),
			models.Index(fields=['cuit'], name='ix_agenda_cuit'),
		]
	
	def __str__(self):
		#-- Mostrar alias si está, sino el nombre.
		display = self.alias or self.nombre or self.cvu_o_cbu
		return f"{display} ({self.cvu_o_cbu})"
