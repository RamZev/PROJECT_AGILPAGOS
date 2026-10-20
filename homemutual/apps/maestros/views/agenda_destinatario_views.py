# apps/maestros/views/agenda_destinatario_views.py
from django.urls import reverse_lazy

from .cruds_views_generics import *
from ..models.agenda_destinatarios_models import AgendaDestinatario
from ..forms.agenda_destinatario_forms import AgendaDestinatarioForm
from apps.core.mixins import StaffRequiredMixin


class ConfigViews():
    model = AgendaDestinatario
    form_class = AgendaDestinatarioForm
    app_label = model._meta.app_label
    model_string = "agenda_destinatario"

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
        'cvu_o_cbu', 'alias_destinatario', 'alias_cvu', 'cuit', 'nombre',
        'id_socio__nombre', 'id_socio__apellido', 'id_socio__cuit',
    ]
    ordering = ['-frecuente', '-ultima_vez_usada', 'nombre']
    paginate_by = 8

    table_headers = {
        'frecuente': (1, 'Frec.'),
        'id_socio': (2, 'Socio'),
        'alias_destinatario': (2, 'Alias Dest.'),
        'alias_cvu': (2, 'Alias CVU'),
        'cvu_o_cbu': (3, 'CVU/CBU'),
        'cuit': (2, 'CUIT'),
        'nombre': (3, 'Titular'),
        'veces_usada': (1, 'Usos'),
        'acciones': (1, 'Acciones'),
    }

    table_data = [
        {'field_name': 'frecuente', 'date_format': None},
        {'field_name': 'id_socio', 'date_format': None},
        {'field_name': 'alias_destinatario', 'date_format': None},
        {'field_name': 'alias_cvu', 'date_format': None},
        {'field_name': 'cvu_o_cbu', 'date_format': None},
        {'field_name': 'cuit', 'date_format': None},
        {'field_name': 'nombre', 'date_format': None},
        {'field_name': 'veces_usada', 'date_format': None},
    ]


class AgendaDestinatarioListView(StaffRequiredMixin, MaestroListView):
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


class AgendaDestinatarioCreateView(StaffRequiredMixin, MaestroCreateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_add


class AgendaDestinatarioUpdateView(StaffRequiredMixin, MaestroUpdateView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    form_class = ConfigViews.form_class
    template_name = ConfigViews.template_form
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_change


class AgendaDestinatarioDeleteView(StaffRequiredMixin, MaestroDeleteView):
    model = ConfigViews.model
    list_view_name = ConfigViews.list_view_name
    template_name = ConfigViews.template_delete
    success_url = ConfigViews.success_url
    permission_required = ConfigViews.permission_delete