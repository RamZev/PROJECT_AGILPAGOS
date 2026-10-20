# homemutual/apps/maestros/models/agenda_general_models.py
from django.db import models
from django.core.exceptions import ValidationError


class AgendaGeneral(models.Model):
	"""
	Agenda general de destinatarios conocidos (Caché).
	
	Almacena datos de CVUs/CBUs consultados a través de Agilpagos (COELSA).
	Se utiliza como caché para evitar consultas costosas y lentas al
	endpoint 8.1 cada vez que un socio ingresa una CVU destino.
	
	Es única y global para toda la mutual (no está atada a un socio).
	"""
	
	# ============================================
	# 1. IDENTIFICADORES
	# ============================================
	id_agenda_general = models.AutoField(
		primary_key=True,
		verbose_name="ID Agenda General",
	)
	
	# ============================================
	# 2. DATOS DEL DESTINATARIO
	# ============================================
	cvu_o_cbu = models.CharField(
		"CVU o CBU",
		max_length=22,
		unique=True,
		db_index=True,
		help_text="22 dígitos. Puede ser CVU de Agilpagos o CBU bancario.",
	)
	alias_cvu = models.CharField(
		"Alias de la CVU",
		max_length=20,
		blank=True,
		null=True,
		help_text="Alias de la CVU en Agilpagos/Coelsa.",
	)
	cuit_titular = models.CharField(
		"CUIT del titular",
		max_length=11,
		help_text="CUIT del titular principal de la cuenta.",
	)
	nombre_titular = models.CharField(
		"Nombre del titular",
		max_length=100,
		help_text="Nombre o Razón Social del titular principal.",
	)
	tipo_persona_titular = models.CharField(
		"Tipo de persona",
		max_length=10,
		blank=True,
		null=True,
		help_text="FISICA o JURIDICA.",
	)
	
	# ============================================
	# 3. MÉTODOS
	# ============================================
	def clean(self):
		super().clean()
		errors = {}
		
		if self.cvu_o_cbu and len(self.cvu_o_cbu) != 22:
			errors['cvu_o_cbu'] = 'El CVU/CBU debe tener exactamente 22 dígitos.'
		
		if self.cvu_o_cbu and not self.cvu_o_cbu.isdigit():
			errors['cvu_o_cbu'] = 'El CVU/CBU debe contener solo dígitos numéricos.'
		
		if self.cuit_titular:
			if len(self.cuit_titular) != 11:
				errors['cuit_titular'] = 'El CUIT debe tener exactamente 11 dígitos.'
			elif not self.cuit_titular.isdigit():
				errors['cuit_titular'] = 'El CUIT debe contener solo dígitos numéricos.'
		
		if errors:
			raise ValidationError(errors)
	
	# ============================================
	# 4. META
	# ============================================
	class Meta:
		db_table = 'agenda_general'
		verbose_name = 'Agenda General'
		verbose_name_plural = 'Agenda General'
		ordering = ['nombre_titular']
		indexes = [
			models.Index(fields=['cvu_o_cbu'], name='ix_agenda_gral_cvu'),
			models.Index(fields=['alias_cvu'], name='ix_agenda_gral_alias'),
			models.Index(fields=['cuit_titular'], name='ix_agenda_gral_cuit'),
		]
	
	def __str__(self):
		display = self.alias_cvu or self.nombre_titular
		return f"{display} ({self.cvu_o_cbu})"