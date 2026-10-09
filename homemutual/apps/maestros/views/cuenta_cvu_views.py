# apps/maestros/views/cuenta_cvu_views.py
import json
import os
import logging

from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings

logger = logging.getLogger(__name__)

from .cruds_views_generics import *
from ..models.cuenta_cvu_models import CuentaCvu
from ..forms.cuenta_cvu_forms import CuentaCvuForm
from ..services.agilpagos_payload import build_alta_payload
from ..services.agilpagos_client import agilpagos_post 
from apps.core.mixins import StaffRequiredMixin


class ConfigViews():
    model = CuentaCvu
    form_class = CuentaCvuForm
    app_label = model._meta.app_label
    model_string = "cuenta_cvu"

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
    search_fields = [
        'cvu', 'alias', 'numero_cuenta_entidad',
        'id_socio__nombre', 'id_socio__apellido', 'id_socio__cuit',
    ]
    ordering = ['id_cuenta_cvu']
    paginate_by = 8

    table_headers = {
        'estado_vcu': (1, 'Estado'),
        'numero_cuenta_entidad': (2, 'N° Cuenta Entidad'),
        'cvu': (2, 'CVU'),
        'alias': (2, 'Alias'),
        'nombre_socio': (3, 'Socio'),
        'id_tipo_cuenta_mutual': (1, 'Tipo'),
        'favorita': (1, 'Favorita'),
        'acciones': (1, 'Acciones'),
    }

    table_data = [
        {'field_name': 'estado_vcu', 'date_format': None},
        {'field_name': 'numero_cuenta_entidad', 'date_format': None},
        {'field_name': 'cvu', 'date_format': None},
        {'field_name': 'alias', 'date_format': None},
        {'field_name': 'nombre_socio', 'date_format': None},
        {'field_name': 'id_tipo_cuenta_mutual', 'date_format': None},
        {'field_name': 'favorita', 'date_format': None},
    ]


class CuentaCvuListView(StaffRequiredMixin, MaestroListView):
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


class CuentaCvuCreateView(StaffRequiredMixin, MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_add

    def form_valid(self, form):
        """
        Guarda la CuentaCvu, genera el JSON y lo envía a Agilpagos.
        Si Agilpagos responde OK, actualiza la CuentaCvu con cvu/alias/etc.
        """
        response = super().form_valid(form)
        cuenta_cvu = self.object

        # 1. Construir el JSON
        try:
            payload = build_alta_payload(cuenta_cvu.id_socio, cuenta_cvu)
        except Exception as e:
            logger.exception("Error construyendo payload")
            messages.warning(
                self.request,
                f"⚠️ CuentaCvu guardada, pero no se pudo construir el JSON: {e}"
            )
            return response

        # 2. Guardar el JSON en /payloads/ (para trazabilidad)
        try:
            payloads_dir = os.path.join(settings.BASE_DIR, 'payloads')
            os.makedirs(payloads_dir, exist_ok=True)
            archivo = os.path.join(
                payloads_dir,
                f"cvu_{cuenta_cvu.numero_cuenta_entidad}.json"
            )
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            logger.info(f"Payload guardado en {archivo}")
        except Exception as e:
            logger.exception("Error guardando payload")

        # 3. ENVIAR a Agilpagos
        try:
            resp = agilpagos_post(self.request, "/onboarding/usuario/alta", json=payload)
        except Exception as e:
            logger.exception("Error enviando a Agilpagos")
            messages.error(
                self.request,
                f"❌ CuentaCvu guardada, pero falló el envío a Agilpagos: {e}"
            )
            return response

        # 4. Mostrar la respuesta en consola
        print()
        print("=" * 60)
        print(f"RESPUESTA AGILPAGOS - {resp.status_code}")
        print("=" * 60)
        try:
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        except Exception:
            print(resp.text)
        print("=" * 60)
        print()

        # 5. Procesar la respuesta
        if resp.status_code == 200:
            data = resp.json()
            # Actualizar la CuentaCvu
            cuenta_cvu.cvu = data.get('cvu') or cuenta_cvu.cvu
            cuenta_cvu.alias = data.get('alias') or cuenta_cvu.alias
            cuenta_cvu.id_usuario_entidad_lineas_cuentas = (
                data.get('idUsuarioEntidadLineasCuentas')
                or cuenta_cvu.id_usuario_entidad_lineas_cuentas
            )
            cuenta_cvu.save()

            # Actualizar el Socio con el idUsuario
            id_usuario = data.get('idUsuario')
            if id_usuario and not cuenta_cvu.id_socio.id_usuario_agilpagos:
                socio = cuenta_cvu.id_socio
                socio.id_usuario_agilpagos = id_usuario
                socio.save(update_fields=['id_usuario_agilpagos'])

            messages.success(
                self.request,
                f"✅ Alta en Agilpagos OK. "
                f"CVU: {data.get('cvu') or '-'}, Alias: {data.get('alias') or '-'}, "
                f"ID Usuario: {id_usuario or '-'}"
            )
        else:
            # Error de Agilpagos
            try:
                detalle = resp.json()
            except Exception:
                detalle = resp.text
            messages.error(
                self.request,
                f"❌ Agilpagos respondió {resp.status_code}: {detalle}"
            )

        return response

class CuentaCvuUpdateView(StaffRequiredMixin, MaestroUpdateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_change


class CuentaCvuDeleteView(StaffRequiredMixin, MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_delete