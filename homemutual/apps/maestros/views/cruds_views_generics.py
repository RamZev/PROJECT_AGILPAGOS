# neumatic\apps\maestros\views\cruds_views_generics.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import OneToOneField
from django.db import transaction
from django.db.models import ProtectedError


#-- Recursos necesarios para proteger las rutas.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

#-- Recursos necesarios para los permisos de usuarios sobre modelos.
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect

from django.utils import timezone


# -- Vistas Genéricas Basada en Clases -----------------------------------------------
@method_decorator(login_required, name='dispatch')
class MaestroListView(ListView):
	cadena_filtro = ""
	paginate_by = 8
	
	search_fields = []
	ordering = []
	
	table_headers = {}
	table_data = []
	pagination_options = [8, 20, 30, 40, 50]
	
	def get_queryset(self):
		#-- Acá ya determina el Modelo con el que se trabaja.
		#-- Obtiene todos los registros sin filtro.
		#-- Con lo cual no es necesario un filter.all().
		#-- luego cambiar a que por defecto no haya registros.
		queryset = super().get_queryset()
		
		#-- Obtener el valor de paginate_by de la URL, si está presente.
		paginate_by_param = self.request.GET.get('paginate_by')
		if paginate_by_param is not None:
			try:
				#-- Intentar convertir a entero, usar valor predeterminado si falla.
				paginate_by_value = int(paginate_by_param)
				self.paginate_by = paginate_by_value
			except ValueError:
				pass
		
		#-- Obtener la cadena de filtro (Propuesto y recomendado por ChatGPT).
		query = self.request.GET.get('busqueda', None)
		
		if query:
			#-- Generar filtros dinámicamente.
			search_conditions = Q()
			for field in self.search_fields:
				search_conditions |= Q(**{f"{field}__icontains": query})
			
			queryset = queryset.filter(search_conditions)
		
		return queryset.order_by(*self.ordering)
		
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		#-- Agregar valores de paginación y valor seleccionado.
		context['pagination_options'] = self.pagination_options
		context['selected_pagination'] = int(self.paginate_by)
		
		#-- Agregar los filtros actuales al contexto.
		#-- Con esto se garantiza que la paginación funcione bien con
		#-- los datos filtrados.
		query_params = self.request.GET.copy()
		if 'page' in query_params:
			#-- Remover el parámetro de paginación actual.
			query_params.pop('page')
		
		context['query_params'] = query_params.urlencode()
		
		#-- Para pasar la fecha a la lista del maestro.
		context['fecha'] = timezone.now()

		return context
	
	def get(self, request, *args, **kwargs):
		#-- Obtener el valor de paginate_by de la URL, si está presente.
		paginate_by_param = self.request.GET.get('paginate_by')
		if paginate_by_param is not None:
			try:
				#-- Intentar convertir a entero, usar valor predeterminado si falla.
				paginate_by_value = int(paginate_by_param)
				self.paginate_by = paginate_by_value
			except ValueError:
				pass
		
		#-- Mantener el valor de paginate_by en el formulario de paginación.
		self.request.GET = self.request.GET.copy()
		self.request.GET['paginate_by'] = str(self.paginate_by)
		
		return super().get(request, *args, **kwargs)
	
	def get_paginate_by(self, queryset):
		#-- Utilizar el valor actualizado de paginate_by.
		return self.paginate_by


@method_decorator(login_required, name='dispatch')
class MaestroCreateView(PermissionRequiredMixin, CreateView):
	list_view_name = None
	
	def form_valid(self, form):
		#-- Accede al usuario evaluado.
		user = self.request.user
		
		#-- Asigna el usuario directamente en el modelo.
		# form.instance.id_user = user
		# form.instance.usuario = user.username

        # Si querés loguear el operador:
		if hasattr(form.instance, 'usuario'):
			form.instance.usuario = user.username

        # Si el modelo tiene id_user y viene vacío en el form, podés completar con el request.user
        # (útil para modelos "propiedad-del-usuario"). Pero no lo hagas para CuentaMutual.
		try:
			fld = self.model._meta.get_field('id_user')
            # Si el form NO envió id_user (o viene None), recién ahí usar el request.user.
			if form.cleaned_data.get('id_user') in (None, ''):
                # Sólo para modelos que realmente deben apuntar al operador actual.
                # Para CuentaMutual NO corresponde.
				pass
		except Exception:
			pass

		from django.db import transaction
		try:
			with transaction.atomic():
				return super().form_valid(form)
		except Exception as e:
			from django.contrib import messages
			messages.error(self.request, f"Error de transacción: {e}")
			return super().form_invalid(form)
	
	def form_invalid(self, form):
		"""
		Si el formulario no es válido, renderiza el formulario con los errores.
		"""
		
		context = self.get_context_data(form=form)
		context['data_has_errors'] = True
		
		return self.render_to_response(context)
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		#-- Agregar datos comunes al contexto.
		context.update({
			"accion": f"Crear {self.model._meta.verbose_name}",
			"list_view_name": self.list_view_name,
		})		
		
		#-- Controlar mostrar o no el modal con los errors de validación.
		#-- Inicialmente, no hay errores.
		context['data_has_errors'] = False
		
		#-- Asegurarse de que el formulario en el contexto sea el mismo que se validó
		context['form'] = self.get_form()
		context['requerimientos'] = obtener_requerimientos_modelo(self.model)
		
		#-- Para pasar la fecha a la lista del maestro.
		context['fecha'] = timezone.now()
		
		return context
	
	#-- Método que agrega mensaje cuando no tiene permiso de crear.
	def handle_no_permission(self):
		messages.error(self.request, 'No tienes permiso para realizar esta acción.')
		return redirect(self.list_view_name)	


@method_decorator(login_required, name='dispatch')
class MaestroUpdateView(PermissionRequiredMixin, UpdateView):
	list_view_name = None
	
	def get_form_kwargs(self):
		"""
		Pasa los argumentos adicionales al formulario solo si son necesarios.
		"""
		kwargs = super().get_form_kwargs()
		
		#-- Verificar si el formulario soporta el argumento 'user'.
		if hasattr(self.form_class, '__ini__') and 'user' in self.form_class.__init__.__code__.co_varnames:
			kwargs['user'] = self.request.user  # Pasar el usuario autenticado al formulario
		
		return kwargs
	
	def form_valid(self, form):
		user = self.request.user
		# NO tocar id_user en ediciones de CuentaMutual u otros modelos maestros
		if hasattr(form.instance, 'usuario'):
			form.instance.usuario = user.username  # auditoría liviana
		return super().form_valid(form)

	
	def form_invalid(self, form):
		"""
		Si el formulario no es válido, renderiza el formulario con los errores.
		"""
		
		#-- Establecer el contexto con la información sobre errores.
		context = self.get_context_data(form=form)
		#-- Indicar que hay errores.
		context['data_has_errors'] = True
		
		return self.render_to_response(context)
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		#-- Obtener el objeto que se está editando.
		registro = self.get_object()
		
		#-- Agregar información personalizada al contexto.
		context.update({
			"accion": f"Editar {self.model._meta.verbose_name} - {registro.pk}",
			"list_view_name": self.list_view_name,
		})
		
		#-- Controlar mostrar o no el modal con los errors de validación.
		#-- Inicialmente, no hay errores.
		context['data_has_errors'] = False
		
		#-- Asegurarse de que el formulario en el contexto sea el mismo que se validó
		context['form'] = self.get_form()
		context['requerimientos'] = obtener_requerimientos_modelo(self.model)
		
		#-- Para pasar la fecha a la lista del maestro.
		context['fecha'] = timezone.now()
		
		return context
	
	#-- Método que agrega mensaje cuando no tiene permiso de modificar.
	def handle_no_permission(self):
		messages.error(self.request, 'No tienes permiso para realizar esta acción.')
		return redirect(self.list_view_name)


@method_decorator(login_required, name='dispatch')
class MaestroDeleteView(PermissionRequiredMixin, DeleteView):
	list_view_name = None
	
	#-- Método que agrega mensaje cuando no tiene permiso de eliminar.
	def handle_no_permission(self):
		messages.error(self.request, 'No tienes permiso para realizar esta acción.')
		return redirect(self.list_view_name)
	
	def post(self, request, *args, **kwargs):
		try:
			with transaction.atomic():
				return self.delete(request, *args, **kwargs)
		except ProtectedError:
			messages.error(request, 'No se puede eliminar el registro ya que está relacionado con otros.')
			return redirect(self.success_url)
		except Exception as e:
			messages.error(request, f'Ocurrió un error inesperado al intentar eliminar: {str(e)}')
			return redirect(self.success_url)

# ------------------------------------------------------------------------------------


@method_decorator(login_required, name='dispatch')
class GenericDetailView(DetailView):
	def get_data(self, obj):
		"""
		Este método debe ser sobreescrito en la clase hija 
		para proporcionar los datos específicos.
		"""
		return {}

	def render_to_response(self, context, **response_kwargs):
		obj = self.get_object()
		data = self.get_data(obj)
		return JsonResponse(data)
# ------------------------------------------------------------------------------------


def obtener_requerimientos_modelo(modelo):
	requerimientos = {}
	
	for field in modelo._meta.fields:
		exclud_fields = ['usuario', 'estacion', 'fcontrol']
		field_info = []
		
		if not field.primary_key and field.name not in exclud_fields:
			if not field.blank:
				field_info.append("Este campo es obligatorio")
			
			if hasattr(field, "max_length") and field.max_length is not None:
				field_info.append(f"Debe tener un máximo de {field.max_length} caracteres")
			
			if field.unique:
				field_info.append("Debe ser único")
			
			requerimientos[field.verbose_name] = field_info
	
	return requerimientos
