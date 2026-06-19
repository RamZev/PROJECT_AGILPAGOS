# homemutual\apps\maestros\views\cuenta_mutual_views.py

from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.db import transaction

from .cruds_views_generics import *
from ..models.cuenta_mutual_models import CuentaMutual
from ..forms.cuenta_mutual_forms import CuentaMutualForm
from apps.core.mixins import StaffRequiredMixin
from apps.core.services.sg import (resolve_sg_for_cuenta, create_sg_account_from_obj)


class ConfigViews():
    model = CuentaMutual
    form_class = CuentaMutualForm
    app_label = model._meta.app_label
    model_string = "cuenta_mutual"
    
    permission_add = f"{app_label}.add_{model.__name__.lower()}"
    permission_change = f"{app_label}.change_{model.__name__.lower()}"
    permission_delete = f"{app_label}.delete_{model.__name__.lower()}"
    
    list_view_name = f"{model_string}_list"
    create_view_name = f"{model_string}_create"
    update_view_name = f"{model_string}_update"
    delete_view_name = f"{model_string}_delete"
    
    template_form = f"{app_label}/{model_string}_form.html"
    template_delete = "base_confirm_delete.html"
    template_list = f'{app_label}/maestro_list.html'
    
    context_object_name = 'objetos'
    home_view_name = "home"
    success_url = reverse_lazy(list_view_name)


class DataViewList():
    search_fields = ['id_socio', 'id_user__username', 'id_user__last_name', 'id_user__first_name', 
                     'nombre', 'apellido', 'razon_social', 'cuit', 'numero_documento']
    ordering = ['id_socio']
    paginate_by = 8
    
    table_headers = {
        'estatus_cuenta_mutual': (1, 'Estatus'),
        'id_user': (1, 'Usuario'),
        'id_socio': (1, 'ID Socio'),
        'usuario_nombre': (1, 'Nombre'),
        'cuit': (1, 'CUIT'),
        'id_sucursal': (1, 'Sucursal'),
        'cvu': (1, 'CVU'),
        'acciones': (1, 'Acciones'),
    }
    
    table_data = [
        {'field_name': 'estatus_cuenta_mutual', 'date_format': None},
        {'field_name': 'id_user', 'date_format': None},
        {'field_name': 'id_socio', 'date_format': None},
        {'field_name': 'usuario_nombre', 'date_format': None},
        {'field_name': 'cuit', 'date_format': None},
        {'field_name': 'id_sucursal', 'date_format': None},
        {'field_name': 'cvu', 'date_format': None},
    ]


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


def _validar_campos_obligatorios(obj):
    """Valida que los campos obligatorios estén completos antes de crear en SG."""
    errores = []
    
    # Persona Física: nombre y apellido
    if obj.id_tipo_persona:
        if str(obj.id_tipo_persona.id_sg_tipo_persona).upper() == '20EB917-7CA8-49E0-9E0B-CA8293218ACA':
            if not obj.nombre or not obj.apellido:
                errores.append("Nombre y Apellido son obligatorios para Persona Física")
    
    # Campos obligatorios generales
    if not obj.cuit:
        errores.append("CUIT es obligatorio")
    if not obj.numero_documento:
        errores.append("Número de Documento es obligatorio")
    if not obj.email:
        errores.append("Email es obligatorio")
    if not obj.numero_telefono:
        errores.append("Teléfono es obligatorio")
    if not obj.id_nacionalidad:
        errores.append("Nacionalidad es obligatoria")
    if not obj.id_provincia:
        errores.append("Provincia es obligatoria")
    if not obj.localidad:
        errores.append("Localidad es obligatoria")
    if not obj.calle:
        errores.append("Calle es obligatoria")
    if not obj.altura:
        errores.append("Altura es obligatoria")
    if not obj.cp:
        errores.append("Código Postal es obligatorio")
    if not obj.id_condicion_fiscal:
        errores.append("Condición Fiscal es obligatoria")
    if not obj.id_estado_civil:
        errores.append("Estado Civil es obligatorio")
    if not obj.id_ocupacion:
        errores.append("Ocupación es obligatoria")
    
    return errores


class CuentaMutualCreateView(StaffRequiredMixin, MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_add
    
    def form_valid(self, form):
        response = super().form_valid(form)
        obj = self.object

        # ---- Validar campos obligatorios ----
        errores = _validar_campos_obligatorios(obj)
        if errores:
            for error in errores:
                messages.warning(self.request, f"⚠️ {error}")
            return response

        cuit = (obj.cuit or "").strip()
        nro = (str(obj.cuenta or "")).strip()
        if not (cuit and nro):
            messages.info(self.request, "Guardado local. Falta CUIT o Nº Cuenta para integrar con SG.")
            return response

        def _post_sg():
            # Crear en SG
            idu, idcta, cvu, alias, estado, reason = create_sg_account_from_obj(obj)

            # Fallback: GET si no vino CVU/alias
            if not cvu or not alias:
                nombre = obj.nombre or (obj.razon_social or "") or "N/D"
                apellido = obj.apellido or "N/D"
                email = obj.email or None
                telefono = str(obj.numero_telefono or "") or None
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

            changed = _aplicar_sg_en_obj(obj, idu=idu, idcta=idcta, cvu=cvu, alias=alias)

            if idu or cvu or alias:
                extras = []
                if idu: extras.append(f"idUsuario={idu}")
                if idcta: extras.append(f"idCuenta={idcta}")
                if cvu: extras.append(f"CVU={cvu}")
                if alias: extras.append(f"Alias={alias}")
                msg = "✅ Crear en SG OK. " + ", ".join(extras)
                if changed:
                    messages.success(self.request, msg)
                else:
                    messages.info(self.request, msg + " (ya estaban cargados).")
            else:
                messages.warning(self.request, f"⚠️ Crear en SG no pudo completarse. Motivo: {reason or 'desconocido'}.")

        transaction.on_commit(_post_sg)
        return response


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
        nro = (str(obj.cuenta or "")).strip()
        force = bool(self.request.POST.get("crear_sg"))

        if not (cuit and nro):
            messages.info(self.request, "Guardado local. Falta CUIT o Nº Cuenta para integrar con SG.")
            return response

        def _post_sg():
            nombre = obj.nombre or (obj.razon_social or "") or "N/D"
            apellido = obj.apellido or "N/D"
            email = obj.email or None
            telefono = str(obj.numero_telefono or "") or None

            if force or not (obj.id_sg_usuario and obj.cvu):
                idu, idcta, cvu, alias, estado, reason = create_sg_account_from_obj(obj)
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

            changed = _aplicar_sg_en_obj(obj, idu=idu, idcta=idcta, cvu=cvu, alias=alias)

            if idu or cvu or alias:
                base = "Crear en SG" if (force or idcta) else "Integración SG"
                extras = []
                if idu: extras.append(f"idUsuario={idu}")
                if idcta: extras.append(f"idCuenta={idcta}")
                if cvu: extras.append(f"CVU={cvu}")
                if alias: extras.append(f"Alias={alias}")
                msg = f"✅ {base} OK. " + ", ".join(extras)
                if changed:
                    messages.success(self.request, msg)
                else:
                    messages.info(self.request, msg + " (ya estaban cargados).")
            else:
                base = "Crear en SG" if (force or idcta) else "Integración SG"
                messages.warning(self.request, f"⚠️ {base} no pudo completarse. Motivo: {reason or 'desconocido'}.")

        transaction.on_commit(_post_sg)
        return response


class CuentaMutualDeleteView(StaffRequiredMixin, MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_delete