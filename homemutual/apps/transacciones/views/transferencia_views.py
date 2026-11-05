# apps/transacciones/views/transferencia_views.py
import json
from datetime import datetime
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q

from apps.maestros.views.cruds_views_generics import MaestroCreateView
from apps.core.mixins import StaffRequiredMixin, SocioRequiredMixin
from apps.maestros.models.cuenta_cvu_models import CuentaCvu
from ..models.transacciones_models import CashoutRequest, Movimiento
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


# class DataViewList():
# 	search_fields = [
# 		'cvu_debito', 'cuit_credito', 'nombre_credito',
# 		'descripcion', 'id_transaccion_entidad',
# 	]
# 	ordering = ['-creado_at']
# 	paginate_by = 8
# 	
# 	table_headers = {
# 		'creado_at': (2, 'Fecha'),
# 		'cvu_debito': (2, 'CVU Origen'),
# 		'nombre_credito': (3, 'Beneficiario'),
# 		'cuit_credito': (2, 'CUIT Benef.'),
# 		'importe': (2, 'Importe'),
# 		'id_concepto': (2, 'Concepto'),
# 		'acciones': (1, 'Acciones'),
# 	}
# 	
# 	table_data = [
# 		{'field_name': 'creado_at', 'date_format': 'd/m/Y H:i'},
# 		{'field_name': 'cvu_debito', 'date_format': None},
# 		{'field_name': 'nombre_credito', 'date_format': None},
# 		{'field_name': 'cuit_credito', 'date_format': None},
# 		{'field_name': 'importe', 'date_format': None},
# 		{'field_name': 'id_concepto', 'date_format': None},
# 	]


# class TransferenciaListView(SocioRequiredMixin, View):
class TransferenciaListView(StaffRequiredMixin, View):
	"""
	Vista principal de Transferencias.
	Renderiza el template con el panel de CVUs y movimientos.
	"""
	template_name = 'transacciones/transferencia_list.html'
	
	def get(self, request, *args, **kwargs):
		meses = [
			(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
			(5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
			(9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
		]
		
		anio_actual = datetime.now().year
		anios = list(range(anio_actual-1, anio_actual+1))
		
		context = {
			'meses': meses,
			'anios': anios,
			'mes_actual': datetime.now().month,
			'anio_actual': anio_actual,
			'list_view_name': 'home',
		}
		return render(request, self.template_name, context)


class TransferenciaCreateView(StaffRequiredMixin, MaestroCreateView):
	"""
	Vista de creación de transferencia.
	
	⚠️ NO persiste en la BD. Solo renderiza el formulario.
	El envío se hace vía AJAX desde el template al endpoint
	/transacciones/api/solicitar-transferencia/.
	"""
	model = ConfigViews.model
	list_view_name = ConfigViews.list_view_name
	form_class = ConfigViews.form_class
	template_name = ConfigViews.template_form
	success_url = ConfigViews.success_url
	permission_required = ConfigViews.permission_add
	
	'''
	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['user'] = self.request.user
		return kwargs
	'''	
	def get_form_kwargs(self):
		"""
		El form es un `forms.Form` normal (no ModelForm), por lo que
		NO acepta `instance`. Solo pasamos `data`, `files` y `user`.
		"""
		kwargs = {
			'user': self.request.user,
		}
		if self.request.method in ('POST', 'PUT'):
			kwargs.update({
				'data': self.request.POST,
				'files': self.request.FILES,
			})
		return kwargs
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = context['form']
		context['tiene_cvus'] = getattr(form, '_tiene_cvus', False)
		context['agenda_map_json'] = json.dumps(
			getattr(form, '_mapa_agenda', {}),
			ensure_ascii=False,
		)
		return context
	
	def form_valid(self, form):
		"""
		Anular el guardado. El template maneja el envío vía AJAX.
		Si por alguna razón se hace un POST normal (sin JS),
		redirigir a la lista sin guardar.
		"""
		#-- No guardamos nada. Redirigimos.
		return redirect(self.success_url)


# ============================================================================
# NUEVO: Endpoint Interno para consultar movimientos desde la BD de Django
# ============================================================================
@require_GET
def api_movimientos_cvu(request):
    """
    Consulta los movimientos de una CVU en la base de datos local.
    """
    cvu_str = request.GET.get('cvu')
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    busqueda = request.GET.get('busqueda', '').strip()
	
    if not cvu_str or not mes or not anio:
        return JsonResponse({'success': False, 'error': 'Faltan parámetros obligatorios'}, status=400)
	
    #-- 1. Buscamos la cuenta por su número de CVU para obtener el id_cuenta_cvu.
    try:
        cuenta = CuentaCvu.objects.get(cvu=cvu_str)
    except CuentaCvu.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'CVU no encontrada en la base de datos local'}, status=404)
	
    #-- 2. Filtramos los movimientos usando el id_cuenta_cvu (como debe ser).
    #-- Nota: Asumo que el campo en el modelo Movimiento se llama 'id_cuenta_cvu'.
    movimientos = Movimiento.objects.filter(
        id_cuenta_cvu=cuenta.id_cuenta_cvu, 
        fecha__year=anio,
        fecha__month=mes
    ).select_related('id_estado_transaccion').order_by('-fecha')
	
    #-- 3. Filtro de búsqueda (tipo, descripción, etc.).
    if busqueda:
        movimientos = movimientos.filter(
            Q(observaciones__icontains=busqueda) |
            Q(tipo_movimiento__icontains=busqueda)
        )
	
    #-- 4. Serializar.
    data = []
    for m in movimientos:
        data.append({
            'fecha': m.fecha.strftime('%d/%m/%Y %H:%M') if m.fecha else '',
            'tipo': m.tipo_movimiento,
            'descripcion': m.observaciones or '-', #-- Ajusta esto si usas otro campo para la descripción.
            'importe': float(m.importe) if m.importe else 0.0,
            'estado': m.id_estado_transaccion.codigo if m.id_estado_transaccion else '-',
        })
	
    return JsonResponse({'success': True, 'data': data})
