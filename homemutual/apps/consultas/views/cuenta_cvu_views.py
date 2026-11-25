# homemutual\apps\consultas\views\cuenta_cvu_views.py
import logging
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from apps.maestros.models.cuenta_cvu_models import CuentaCvu
from apps.maestros.models.cvu_alias_historial_models import CvuAliasHistorial
from apps.maestros.services.agilpagos_client import agilpagos_put

logger = logging.getLogger(__name__)


class MisCuentasCvuView(LoginRequiredMixin, View):
	template_name = "consultas/mis_cuentas_cvu.html"
	
	# =========================================================================
	# GET: Renderizar la lista de CVUs y el panel de detalle.
	# =========================================================================
	def get(self, request, *args, **kwargs):
		socio = getattr(request.user, 'socio', None)
		if not socio:
			messages.error(request, "El usuario no tiene un socio asociado.")
			return redirect("home")
		
		cuentas = CuentaCvu.objects.filter(id_socio=socio).order_by("-fecha_alta")
		
		return render(request, self.template_name, {
			"cuentas": cuentas,
			"socio": socio,
		})
	
	# =========================================================================
	# POST: Procesar acciones (cambiar alias / toggle bloqueo).
	# =========================================================================
	def post(self, request, *args, **kwargs):
		socio = getattr(request.user, 'socio', None)
		if not socio:
			return redirect("home")
		
		accion = request.POST.get("accion")
		id_cuenta = request.POST.get("id_cuenta_cvu")
		cuenta = get_object_or_404(CuentaCvu, pk=id_cuenta, id_socio=socio)
		
		if accion == "cambiar_alias":
			self._procesar_cambio_alias(request, cuenta)
		elif accion == "toggle_bloqueo":
			self._procesar_toggle_bloqueo(request, cuenta)
		
		return redirect("mis_cuentas_cvu")
	
	# =========================================================================
	# Acción: Cambiar Alias (consume API Intermedia).
	# =========================================================================
	def _procesar_cambio_alias(self, request, cuenta):
		nuevo_alias = request.POST.get("nuevo_alias", "").strip()
		
		# -- Validaciones locales (además de las que hace Agilpagos).
		if not nuevo_alias:
			messages.error(request, "El alias no puede estar vacío.")
			return
		if len(nuevo_alias) > 20:
			messages.error(request, "El alias no puede superar los 20 caracteres.")
			return
		if cuenta.alias_actualizado_at:
			delta = timezone.now() - cuenta.alias_actualizado_at
			if delta.total_seconds() < 24 * 3600:
				messages.error(request, "Debe esperar 24 horas entre cambios de alias.")
				return
		
		try:
			# -- Llamar a la API Intermedia (PUT /onboarding/alias/cambiar).
			response = agilpagos_put(
				request,
				"/onboarding/alias/cambiar",
				json={
					"cvu": cuenta.cvu,
					"nuevo_alias": nuevo_alias,
				},
			)
			
			if response.status_code == 200:
				with transaction.atomic():
					# -- Registrar en historial.
					CvuAliasHistorial.objects.create(
						id_cvu=cuenta,
						alias_anterior=cuenta.alias,
						alias_nuevo=nuevo_alias,
						origen='MUTUAL',
					)
					# -- Actualizar la CVU. El .save() del modelo actualiza
					# -- alias_actualizado_at automáticamente.
					cuenta.alias = nuevo_alias
					cuenta.save()
				
				messages.success(request, f"Alias actualizado a '{nuevo_alias}' correctamente.")
			else:
				# -- API Intermedia devolvió error (400, 404, 502, etc.).
				try:
					detalle = response.json().get("detail", response.text)
				except Exception:
					detalle = response.text
				logger.warning(f"Error de API Intermedia al cambiar alias: {response.status_code} - {detalle}")
				messages.error(request, f"Error al cambiar alias: {detalle}")
		
		except Exception as e:
			logger.error(f"Error de conexión al cambiar alias: {e}", exc_info=True)
			messages.error(request, "No se pudo conectar con el servicio de pagos. Intente más tarde.")
	
	# =========================================================================
	# Acción: Toggle Bloqueo (solo a nivel local, no toca Agilpagos).
	# =========================================================================
	def _procesar_toggle_bloqueo(self, request, cuenta):
		if cuenta.bloqueada_compliance:
			messages.error(request, "No se puede desbloquear una cuenta bloqueada por Compliance.")
			return
		
		cuenta.bloqueada_usuario = not cuenta.bloqueada_usuario
		cuenta.save(update_fields=["bloqueada_usuario"])
		
		estado = "bloqueada" if cuenta.bloqueada_usuario else "desbloqueada"
		messages.success(request, f"Cuenta {estado} exitosamente.")