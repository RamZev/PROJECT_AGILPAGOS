# apps/transacciones/forms/transferencia_forms.py
"""
Formulario de transferencia (CashOut).

NO persiste en la BD: solo recopila los datos para enviarlos
a la API Intermedia vía AJAX desde el template.

La vista `TransferenciaCreateView` NO llama a `form.save()`.
"""
from django import forms

from apps.maestros.models.socio_models import Socio
from apps.maestros.models.cuenta_cvu_models import CuentaCvu
from apps.maestros.models.agenda_destinatarios_models import AgendaDestinatario
from apps.maestros.models.sg_catalogo_models import SgConceptoTransaccion
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class TransferenciaForm(forms.Form):
	"""
	Formulario de transferencia.

	Los campos que se llenan dinámicamente (cvu_debito, agenda_destinatario_pk)
	tienen choices vacías al inicio; el JavaScript las popula desde
	los endpoints API.
	"""
	
	# ========================================================================
	# SECCIÓN 1: CVU ORIGEN
	# ========================================================================
	cvu_debito = forms.ChoiceField(
		required=True,
		label="CVU Origen",
		choices=[],  # se llena por JS
		widget=forms.Select(attrs={**formclassselect}),
	)
	
	# ========================================================================
	# SECCIÓN 2: CVU DESTINO
	# ========================================================================
	buscar_cvu_credito = forms.CharField(
		required=False,
		max_length=22,
		label="CVU destino",
		widget=forms.TextInput(attrs={
			**formclasstext,
			'placeholder': 'Ingrese CVU/CBU del beneficiario',
			'inputmode': 'numeric',
		}),
	)
	
	agenda_destinatario_pk = forms.ChoiceField(
		required=False,
		label="Agenda de destinatarios",
		choices=[],  # se llena por JS
		widget=forms.Select(attrs={**formclassselect}),
	)
	
	cuit_credito = forms.CharField(
		required=False,
		max_length=11,
		label="CUIT del beneficiario",
		widget=forms.TextInput(attrs={**formclasstext, 'readonly': True}),
	)
	
	nombre_credito = forms.CharField(
		required=False,
		max_length=100,
		label="Nombre del beneficiario",
		widget=forms.TextInput(attrs={**formclasstext, 'readonly': True}),
	)
	
	cbu_credito = forms.CharField(
		required=False,
		max_length=22,
		label="CVU/CBU del beneficiario",
		widget=forms.TextInput(attrs={**formclasstext, 'readonly': True}),
	)
	
	guardar_en_agenda = forms.BooleanField(
		required=False,
		initial=True,
		label="Agregar destinatario a la agenda",
		widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
	)
	
	# ========================================================================
	# SECCIÓN 3: DATOS DE LA OPERACIÓN
	# ========================================================================
	id_concepto = forms.ModelChoiceField(
		queryset=SgConceptoTransaccion.objects.filter(
			estatus_sg_concepto_transaccion=True
		).order_by('codigo'),
		required=True,
		empty_label="-- Seleccionar Concepto --",
		label="Concepto",
		widget=forms.Select(attrs={**formclassselect}),
	)
	
	importe = forms.DecimalField(
		required=True,
		max_digits=15,
		decimal_places=2,
		min_value=0.01,
		label="Importe",
		widget=forms.NumberInput(attrs={
			**formclasstext,
			'step': '0.01',
			'min': '0.01',
		}),
	)
	
	descripcion = forms.CharField(
		required=True,
		max_length=100,
		label="Descripción",
		widget=forms.TextInput(attrs={**formclasstext}),
	)
	
	observaciones = forms.CharField(
		required=False,
		max_length=100,
		label="Observaciones",
		widget=forms.TextInput(attrs={**formclasstext}),
	)
	
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)
		
		#-- Label del concepto.
		self.fields['id_concepto'].label_from_instance = (
			lambda o: f"{o.codigo} - {o.descripcion}"
		)
		
		#-- Cargar agenda del socio (para el select inicial).
		self._cargar_agenda_del_usuario()
		
		#-- Cargar CVUs del socio (para el select inicial).
		self._cargar_cvus_del_usuario()
	
	# ========================================================================
	# CARGA DE CVUs DEL SOCIO
	# ========================================================================
	def _cargar_cvus_del_usuario(self):
		"""
		Carga las CVUs del socio desde la BD local.
		
		El detalle de saldos se obtiene vía AJAX desde la API Intermedia
		(endpoint /consulta/cvus-propias).
		"""
		
		choices = [('', '-- Seleccionar CVU --')]
		
		if not self.user:
			self.fields['cvu_debito'].choices = choices
			self._tiene_cvus = False
			return
		
		try:
			socio = self.user.socio
		except Socio.DoesNotExist:
			self.fields['cvu_debito'].choices = choices
			self._tiene_cvus = False
			return
		
		if not socio:
			self.fields['cvu_debito'].choices = choices
			self._tiene_cvus = False
			return
		
		cvus = CuentaCvu.objects.filter(
			id_socio=socio,
			estado_vcu='Activo',
			fecha_baja__isnull=True,
			bloqueada_compliance=False,
		).order_by('-favorita', 'numero_cuenta_entidad')
		
		#-- Recorrer CVUs y armar el label con alias.
		for cvu in cvus:
			label = f"{cvu.cvu}"
			if cvu.alias:
				label += f" — {cvu.alias}"
			choices.append((cvu.cvu, label))
		
		self.fields['cvu_debito'].choices = choices
		self._tiene_cvus = len(choices) > 1
	
	# ========================================================================
	# CARGA DE AGENDA
	# ========================================================================
	def _cargar_agenda_del_usuario(self):
		"""
		Carga la agenda de destinatarios del socio.
		"""
		
		choices = [('', '-- Agenda de destinatarios --')]
		self._mapa_agenda = {}
		
		if not self.user:
			self.fields['agenda_destinatario_pk'].choices = choices
			return
		
		try:
			socio = self.user.socio
		except Socio.DoesNotExist:
			self.fields['agenda_destinatario_pk'].choices = choices
			return
		
		if not socio:
			self.fields['agenda_destinatario_pk'].choices = choices
			return
		
		destinatarios = AgendaDestinatario.objects.filter(
			id_socio=socio
		).order_by('-frecuente', '-ultima_vez_usada', 'nombre')
		
		for d in destinatarios:
			#-- Usar alias_destinatario (el alias referencial del socio).
			#-- Si no tiene, usar el nombre del titular.
			display = d.alias_destinatario or d.nombre or '(sin nombre)'
			
			label = f"{display} — {d.cvu_o_cbu}"
			choices.append((str(d.pk), label))
			
			self._mapa_agenda[str(d.pk)] = {
				'cvu_o_cbu': d.cvu_o_cbu,
				'cuit': d.cuit,
				'nombre': d.nombre,
				'alias_destinatario': d.alias_destinatario or '',
				'alias_cvu': d.alias_cvu or '',
			}
		
		self.fields['agenda_destinatario_pk'].choices = choices
