# homemutual\apps\maestros\views\cuenta_mutual_views.py

from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.db import transaction

from .cruds_views_generics import *
from ..models.cuenta_mutual_models import CuentaMutual
from ..forms.cuenta_mutual_forms import CuentaMutualForm
from apps.core.mixins import StaffRequiredMixin  # <-- ajustado a tu import real
# Mantengo tus helpers SG que devuelven TUPLAS
from apps.core.services.sg import (resolve_sg_for_cuenta, create_sg_account_from_obj)  # ajustá el path si difiere


class ConfigViews():
	# Modelo
	model = CuentaMutual
	
	# Formulario asociado al modelo
	form_class = CuentaMutualForm
	
	# Aplicación asociada al modelo
	app_label = model._meta.app_label
	
	#-- Deshabilitado por redundancia:
	# # Título del listado del modelo
	# master_title = model._meta.verbose_name_plural
	
	#-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	# model_string = model.__name__.lower()  #-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	
	#-- Usar esta forma cuando el modelo esté compuesto por más de una palabra: Ej. TipoCambio colocar "tipo_cambio".
	model_string = "cuenta_mutual"
	
	# Permisos
	permission_add = f"{app_label}.add_{model.__name__.lower()}"
	permission_change = f"{app_label}.change_{model.__name__.lower()}"
	permission_delete = f"{app_label}.delete_{model.__name__.lower()}"
	
	# Vistas del CRUD del modelo
	list_view_name = f"{model_string}_list"
	create_view_name = f"{model_string}_create"
	update_view_name = f"{model_string}_update"
	delete_view_name = f"{model_string}_delete"
	
	# Plantilla para crear o actualizar el modelo
	template_form = f"{app_label}/{model_string}_form.html"
	
	# Plantilla para confirmar eliminación de un registro
	template_delete = "base_confirm_delete.html"
	
	# Plantilla de la lista del CRUD
	template_list = f'{app_label}/maestro_list.html'
	
	# Contexto de los datos de la lista
	context_object_name	= 'objetos'
	
	# Vista del home del proyecto
	home_view_name = "home"
	
	# Nombre de la url 
	success_url = reverse_lazy(list_view_name)


class DataViewList():
	search_fields = ['id_socio', 'id_user__username', 'id_user__last_name', 'id_user__first_name']
	ordering = ['id_socio']
	paginate_by = 8
	  
	table_headers = {
		'estatus_cuenta_mutual': (1, 'Estatus'),
		'id_user': (1, 'Usuario'),
		'id_socio': (1, 'ID Socio'),
		'usuario_nombre': (1, 'Apellido'),
		'id_sucursal': (1, 'Sucursal'),
		'acciones': (1, 'Acciones'),
	}
	
	table_data = [
		{'field_name': 'estatus_cuenta_mutual', 'date_format': None},
		{'field_name': 'id_user', 'date_format': None},
		{'field_name': 'id_socio', 'date_format': None},
		{'field_name': 'usuario_nombre', 'date_format': None},
		{'field_name': 'id_sucursal', 'date_format': None},
	]


# CuentaMutualListView - Inicio
class CuentaMutualListView(StaffRequiredMixin, MaestroListView):
	model = ConfigViews.model
	template_name = ConfigViews.template_list
	context_object_name = ConfigViews.context_object_name
	
	search_fields = DataViewList.search_fields
	ordering = DataViewList.ordering
	
	extra_context = {
		"master_title": ConfigViews.model._meta.verbose_name_plural,
		"home_view_name": ConfigViews.home_view_name,
		"list_view_name": ConfigViews.list_view_name,
		"create_view_name": ConfigViews.create_view_name,
		"update_view_name": ConfigViews.update_view_name,
		"delete_view_name": ConfigViews.delete_view_name,
		"table_headers": DataViewList.table_headers,
		"table_data": DataViewList.table_data,
	}


# -------- Helpers locales para actualizar campos SG en un solo save --------
def _aplicar_sg_en_obj(obj, idu=None, idcta=None, cvu=None, alias=None):
	changed_fields = []
	if idu and not obj.id_sg_usuario:
		obj.id_sg_usuario = idu
		changed_fields.append("id_sg_usuario")
	if idcta and not obj.id_sg_cuenta:
		obj.id_sg_cuenta = idcta
		changed_fields.append("id_sg_cuenta")
	if cvu and not (obj.cvu or "").strip():
		obj.cvu = cvu
		changed_fields.append("cvu")
	if alias and not (obj.alias or "").strip():
		obj.alias = alias
		changed_fields.append("alias")
	if changed_fields:
		obj.save(update_fields=changed_fields)
	return changed_fields


# CuentaMutualCreateView - Inicio
class CuentaMutualCreateView(StaffRequiredMixin, MaestroCreateView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_form
	success_url = ConfigViews.success_url
	permission_required = ConfigViews.permission_add
	
	def form_valid(self, form):
		response = super().form_valid(form)
		obj = self.object  # ya tiene PK y 'cuenta' calculada por el modelo

		cuit = (obj.cuit or "").strip()
		nro  = (str(obj.cuenta or "")).strip()
		if not (cuit and nro):
			messages.info(self.request, "Guardado local. Falta CUIT o Nº Cuenta para integrar con SG.")
			return response

		# En ALTA: SIEMPRE crear/sincronizar en SG, pero después de commit
		def _post_sg():
			# Paso 1: Alta/actualización directa (usa obj.cuenta como numeroCuentaEntidad)
			idu, idcta, cvu, alias, estado, reason = create_sg_account_from_obj(obj)

			# Paso 2 (fallback): si no viene CVU/alias en el POST, hacemos GET inmediato
			if not cvu or not alias:
				nombre = (getattr(obj.id_user, "first_name", "") or (obj.razon_social or "") or "N/D").strip()
				apellido = (getattr(obj.id_user, "last_name", "") or "N/D").strip()
				email = (getattr(obj.id_user, "email", "") or None)
				telefono = str(getattr(obj, "numero_telefono", "") or "") or None
				_idu2, _cvu2, _alias2, _estado2, _reason2 = resolve_sg_for_cuenta(
					cuit=cuit,
					nro_cuenta_entidad=nro,
					nombre=nombre,
					apellido=apellido,
					email=email,
					telefono=telefono,
					force_create=False,
				)
				# Preferimos valores nuevos si llegaron
				cvu = cvu or _cvu2
				alias = alias or _alias2
				# id_usuario puede venir solo en GET también
				idu = idu or _idu2

			changed = _aplicar_sg_en_obj(obj, idu=idu, idcta=idcta, cvu=cvu, alias=alias)

			if idu or cvu or alias:
				extras = []
				if idu: extras.append(f"idUsuario={idu}")
				if idcta: extras.append(f"idCuenta={idcta}")
				if cvu: extras.append(f"CVU={cvu}")
				if alias: extras.append(f"Alias={alias}")
				msg = "Crear en SG OK. " + ", ".join(extras)
				if changed:
					messages.success(self.request, msg)
				else:
					messages.info(self.request, msg + " (ya estaban cargados).")
			else:
				messages.warning(self.request, f"Crear en SG no pudo completarse. Motivo: {reason or 'desconocido'}.")

		transaction.on_commit(_post_sg)
		return response


# CuentaMutualUpdateView
class CuentaMutualUpdateView(StaffRequiredMixin, MaestroUpdateView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_form
	success_url = ConfigViews.success_url
	permission_required = ConfigViews.permission_change

	def form_valid(self, form):
		response = super().form_valid(form)
		obj = self.object

		cuit = (obj.cuit or "").strip()
		nro  = (str(obj.cuenta or "")).strip()
		force = bool(self.request.POST.get("crear_sg"))

		if not (cuit and nro):
			messages.info(self.request, "Guardado local. Falta CUIT o Nº Cuenta para integrar con SG.")
			return response

		def _post_sg():
			nombre = (getattr(obj.id_user, "first_name", "") or (obj.razon_social or "") or "N/D").strip()
			apellido = (getattr(obj.id_user, "last_name", "") or "N/D").strip()
			email = (getattr(obj.id_user, "email", "") or None)
			telefono = str(getattr(obj, "numero_telefono", "") or "") or None

			if force or not (obj.id_sg_usuario and obj.cvu):
				# Alta/actualización (POST)
				idu, idcta, cvu, alias, estado, reason = create_sg_account_from_obj(obj)
				# Fallback GET si POST no devolvió CVU/alias
				if not cvu or not alias:
					_idu2, _cvu2, _alias2, _estado2, _reason2 = resolve_sg_for_cuenta(
						cuit=cuit,
						nro_cuenta_entidad=nro,
						nombre=nombre,
						apellido=apellido,
						email=email,
						telefono=telefono,
						force_create=False,
					)
					cvu = cvu or _cvu2
					alias = alias or _alias2
					idu = idu or _idu2
			else:
				# Solo sincronizar (GET)
				idu, cvu, alias, estado, reason = resolve_sg_for_cuenta(
					cuit=cuit,
					nro_cuenta_entidad=nro,
					nombre=nombre,
					apellido=apellido,
					email=email,
					telefono=telefono,
					force_create=False,
				)
				idcta = None

			changed = _aplicar_sg_en_obj(obj, idu=idu, idcta=locals().get("idcta"), cvu=cvu, alias=alias)

			if idu or cvu or alias:
				base = "Crear en SG" if (force or locals().get("idcta")) else "Integración SG"
				extras = []
				if idu: extras.append(f"idUsuario={idu}")
				if locals().get("idcta"): extras.append(f"idCuenta={idcta}")
				if cvu: extras.append(f"CVU={cvu}")
				if alias: extras.append(f"Alias={alias}")
				msg = f"{base} OK. " + ", ".join(extras)
				if changed:
					messages.success(self.request, msg)
				else:
					messages.info(self.request, msg + " (ya estaban cargados).")
			else:
				base = "Crear en SG" if (force or locals().get("idcta")) else "Integración SG"
				messages.warning(self.request, f"{base} no pudo completarse. Motivo: {reason or 'desconocido'}.")

		transaction.on_commit(_post_sg)
		return response


# CuentaMutualDeleteView
class CuentaMutualDeleteView (StaffRequiredMixin, MaestroDeleteView):
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	template_name = ConfigViews.template_delete
	success_url = ConfigViews.success_url
	permission_required = ConfigViews.permission_delete
