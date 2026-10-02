# apps/maestros/views/cuenta_cvu_views.py
from django.urls import reverse_lazy

from .cruds_views_generics import *
from ..models.cuenta_cvu_models import CuentaCvu
from ..forms.cuenta_cvu_forms import CuentaCvuForm
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