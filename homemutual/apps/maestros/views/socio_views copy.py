# apps/maestros/views/socio_views.py
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction


from .cruds_views_generics import *
from ..models.socio_models import Socio
from ..forms.socio_forms import SocioForm
from apps.core.mixins import StaffRequiredMixin
from ..services.socio_service import crear_socio_con_usuario, DEFAULT_SOCIO_PASSWORD

class ConfigViews():
    model = Socio
    form_class = SocioForm
    app_label = model._meta.app_label
    model_string = "socio"

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
        'id_socio_mutual', 'codigo_socio', 'nombre', 'apellido',
        'cuit', 'email', 'numero_documento',
    ]
    ordering = ['id_socio_mutual']
    paginate_by = 8

    table_headers = {
        'estado': (1, 'Estatus'),
        'id_socio_mutual': (1, 'ID Mutual'),
        'id_sucursal': (1, 'Sucursal'),
        'codigo_socio': (1, 'Código'),
        'nombre_completo': (3, 'Socio'),
        'cuit': (2, 'CUIT'),
        'id_usuario_agilpagos': (2, 'ID Agilpagos'),
        'acciones': (1, 'Acciones'),
    }

    table_data = [
        {'field_name': 'estado', 'date_format': None},
        {'field_name': 'id_socio_mutual', 'date_format': None},
        {'field_name': 'id_sucursal', 'date_format': None},
        {'field_name': 'codigo_socio', 'date_format': None},
        {'field_name': 'nombre_completo', 'date_format': None},
        {'field_name': 'cuit', 'date_format': None},
        {'field_name': 'id_usuario_agilpagos', 'date_format': None},
    ]


class SocioListView(StaffRequiredMixin, MaestroListView):
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


class SocioCreateView(StaffRequiredMixin, MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_add


class SocioUpdateView(StaffRequiredMixin, MaestroUpdateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_change


class SocioDeleteView(StaffRequiredMixin, MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_delete