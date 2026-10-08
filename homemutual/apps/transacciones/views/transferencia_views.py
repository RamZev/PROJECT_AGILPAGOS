# apps/transacciones/views/transferencia_views.py
from django.urls import reverse_lazy

from apps.maestros.views.cruds_views_generics import *
from apps.core.mixins import StaffRequiredMixin

from ..models.transacciones_models import CashoutRequest
from ..forms.transferencia_forms import TransferenciaForm


class ConfigViews():
    model = CashoutRequest
    form_class = TransferenciaForm
    app_label = model._meta.app_label
    model_string = "transferencia"

    permission_add = f"{app_label}.add_{model.__name__.lower()}"
    permission_change = f"{app_label}.change_{model.__name__.lower()}"
    permission_delete = f"{app_label}.delete_{model.__name__.lower()}"

    list_view_name = f"{model_string}_list"
    create_view_name = f"{model_string}_create"
    update_view_name = f"{model_string}_update"
    delete_view_name = f"{model_string}_delete"

    template_form = f"{app_label}/{model_string}_form.html"
    template_delete = "base_confirm_delete.html"
    template_list = 'maestros/maestro_list.html' 

    context_object_name = 'objetos'
    home_view_name = "home"
    success_url = reverse_lazy(list_view_name)


class DataViewList():
    search_fields = [
        'cvu_debito', 'cuit_credito', 'nombre_credito',
        'descripcion', 'id_transaccion_entidad',
    ]
    ordering = ['-creado_at']
    paginate_by = 8

    table_headers = {
        'creado_at': (2, 'Fecha'),
        'cvu_debito': (2, 'CVU Origen'),
        'nombre_credito': (3, 'Beneficiario'),
        'cuit_credito': (2, 'CUIT Benef.'),
        'importe': (2, 'Importe'),
        'id_concepto': (2, 'Concepto'),
        'acciones': (1, 'Acciones'),
    }

    table_data = [
        {'field_name': 'creado_at', 'date_format': 'd/m/Y H:i'},
        {'field_name': 'cvu_debito', 'date_format': None},
        {'field_name': 'nombre_credito', 'date_format': None},
        {'field_name': 'cuit_credito', 'date_format': None},
        {'field_name': 'importe', 'date_format': None},
        {'field_name': 'id_concepto', 'date_format': None},
    ]


class TransferenciaListView(StaffRequiredMixin, MaestroListView):
    model = ConfigViews.model
    template_name = ConfigViews.template_list
    context_object_name = ConfigViews.context_object_name

    search_fields = DataViewList.search_fields
    ordering = DataViewList.ordering

    extra_context = {
        "master_title": "Transferencias",
        "home_view_name": ConfigViews.home_view_name,
        "list_view_name": ConfigViews.list_view_name,
        "create_view_name": ConfigViews.create_view_name,
        "update_view_name": ConfigViews.update_view_name,
        "delete_view_name": ConfigViews.delete_view_name,
        "table_headers": DataViewList.table_headers,
        "table_data": DataViewList.table_data,
    }


class TransferenciaCreateView(StaffRequiredMixin, MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_add


class TransferenciaUpdateView(StaffRequiredMixin, MaestroUpdateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_change


class TransferenciaDeleteView(StaffRequiredMixin, MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_delete