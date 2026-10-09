# apps/maestros/views/sg_tipo_cuenta_mutual_views.py
from django.urls import reverse_lazy
from apps.maestros.views.cruds_views_generics import (
    MaestroListView,
    MaestroCreateView,
    MaestroUpdateView,
    MaestroDeleteView,
)
from apps.maestros.models.sg_catalogo_models import SgTipoCuentaMutual
from apps.maestros.forms.sg_tipo_cuenta_mutual_forms import SgTipoCuentaMutualForm
from apps.core.mixins import StaffRequiredMixin


class ConfigViews():
    model = SgTipoCuentaMutual
    form_class = SgTipoCuentaMutualForm
    app_label = model._meta.app_label
    model_string = "sg_tipo_cuenta_mutual"

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
    search_fields = ['codigo_letra', 'descripcion']
    ordering = ['id_sg_tipo_cuenta_mutual']
    paginate_by = 8

    table_headers = {
        'id_sg_tipo_cuenta_mutual': (1, 'ID'),
        'codigo_letra': (1, 'Letra'),
        'descripcion': (4, 'Descripción'),
        'estatus_sg_tipo_cuenta_mutual': (1, 'Activo'),
        'acciones': (1, 'Acciones'),
    }

    table_data = [
        {'field_name': 'id_sg_tipo_cuenta_mutual', 'date_format': None},
        {'field_name': 'codigo_letra', 'date_format': None},
        {'field_name': 'descripcion', 'date_format': None},
        {'field_name': 'estatus_sg_tipo_cuenta_mutual', 'date_format': None},
    ]


class SgTipoCuentaMutualListView(StaffRequiredMixin, MaestroListView):
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


class SgTipoCuentaMutualCreateView(StaffRequiredMixin, MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_add


class SgTipoCuentaMutualUpdateView(StaffRequiredMixin, MaestroUpdateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_change


class SgTipoCuentaMutualDeleteView(StaffRequiredMixin, MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_delete