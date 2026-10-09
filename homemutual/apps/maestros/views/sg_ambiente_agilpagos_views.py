# apps/maestros/views/sg_ambiente_agilpagos_views.py
from django.urls import reverse_lazy
from apps.maestros.views.cruds_views_generics import (
    MaestroListView,
    MaestroCreateView,
    MaestroUpdateView,
    MaestroDeleteView,
)
from apps.maestros.models.sg_catalogo_models import SgAmbienteAgilpagos
from apps.maestros.forms.sg_ambiente_agilpagos_forms import SgAmbienteAgilpagosForm
from apps.core.mixins import StaffRequiredMixin


class ConfigViews():
    model = SgAmbienteAgilpagos
    form_class = SgAmbienteAgilpagosForm
    app_label = model._meta.app_label
    model_string = "sg_ambiente_agilpagos"

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
    search_fields = ['nombre', 'url_base', 'id_entidad']
    ordering = ['nombre']
    paginate_by = 8

    table_headers = {
        'id_sg_ambiente_agilpagos': (1, 'ID'),
        'nombre': (2, 'Nombre'),
        'url_base': (4, 'URL Base'),
        'id_entidad': (3, 'ID Entidad'),
        'estatus_sg_ambiente_agilpagos': (1, 'Activo'),
        'acciones': (1, 'Acciones'),
    }

    table_data = [
        {'field_name': 'id_sg_ambiente_agilpagos', 'date_format': None},
        {'field_name': 'nombre', 'date_format': None},
        {'field_name': 'url_base', 'date_format': None},
        {'field_name': 'id_entidad', 'date_format': None},
        {'field_name': 'estatus_sg_ambiente_agilpagos', 'date_format': None},
    ]


class SgAmbienteAgilpagosListView(StaffRequiredMixin, MaestroListView):
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


class SgAmbienteAgilpagosCreateView(StaffRequiredMixin, MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_add


class SgAmbienteAgilpagosUpdateView(StaffRequiredMixin, MaestroUpdateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_change


class SgAmbienteAgilpagosDeleteView(StaffRequiredMixin, MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_delete