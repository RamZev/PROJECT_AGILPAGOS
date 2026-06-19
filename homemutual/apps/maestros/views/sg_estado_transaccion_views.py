# apps/maestros/views/sg_estado_transaccion_views.py
from django.urls import reverse_lazy
from apps.maestros.views.cruds_views_generics import (
    MaestroListView,
    MaestroCreateView,
    MaestroUpdateView,
    MaestroDeleteView,
)
from apps.maestros.models.sg_catalogo_models import SgEstadoTransaccion
from apps.maestros.forms.sg_estado_transaccion_forms import SgEstadoTransaccionForm
from apps.core.mixins import StaffRequiredMixin


class ConfigViews():
    model = SgEstadoTransaccion
    form_class = SgEstadoTransaccionForm
    app_label = model._meta.app_label
    model_string = "sg_estado_transaccion"
    
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
    search_fields = ['codigo', 'descripcion']
    ordering = ['codigo']
    paginate_by = 8
    
    table_headers = {
        'id_sg_estado_transaccion': (3, 'ID Agilpagos'),
        'codigo': (2, 'Código'),
        'descripcion': (3, 'Descripción'),
        'es_final': (1, 'Es Final'),
        'estatus_sg_estado_transaccion': (1, 'Activo'),
        'acciones': (1, 'Acciones'),
    }
    
    table_data = [
        {'field_name': 'id_sg_estado_transaccion', 'date_format': None},
        {'field_name': 'codigo', 'date_format': None},
        {'field_name': 'descripcion', 'date_format': None},
        {'field_name': 'es_final', 'date_format': None},
        {'field_name': 'estatus_sg_estado_transaccion', 'date_format': None},
    ]


class SgEstadoTransaccionListView(StaffRequiredMixin, MaestroListView):
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


class SgEstadoTransaccionCreateView(StaffRequiredMixin, MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_add


class SgEstadoTransaccionUpdateView(StaffRequiredMixin, MaestroUpdateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_change


class SgEstadoTransaccionDeleteView(StaffRequiredMixin, MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_delete