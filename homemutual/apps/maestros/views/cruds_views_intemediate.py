# neumatic\apps\maestros\views\cruds_views_intemediate.py
from django.urls import reverse_lazy
from ..views.cruds_views_generics import *


class BaseConfigViews():
	# Modelo
	model = None
	
	# Formulario asociado al modelo
	form_class = None
	
	# Aplicación asociada al modelo
	# app_label = model._meta.app_label
	@property
	def app_label(self):
		return self.model._meta.app_label
	
	#-- Deshabilitado por redundancia:
	# # Título del listado del modelo
	# master_title = model._meta.verbose_name_plural
	
	#-- Usar esta forma cuando el modelo esté compuesto de una sola palabra: Ej. Color.
	# model_string = model.__name__.lower()
	@property
	def model_string(self):
		return self.model.__name__.lower()
 	
	# Permisos
	# permission_add = f"{app_label}.add_{model_string}"
	# permission_change = f"{app_label}.change_{model_string}"
	# permission_delete = f"{app_label}.delete_{model_string}"
 
	@property
	def permission_add(self):
		return f"{self.app_label}.add_{self.model_string}"
	
	@property
	def permission_change(self):
		return f"{self.app_label}.change_{self.model_string}"
	
	@property
	def permission_delete(self):
		return f"{self.app_label}.delete_{self.model_string}"
	
	# Vistas del CRUD del modelo
	# list_view_name = f"{model_string}_list"
	# create_view_name = f"{model_string}_create"
	# update_view_name = f"{model_string}_update"
	# delete_view_name = f"{model_string}_delete"
 
	@property
	def list_view_name(self):
		return f"{self.model_string}_list"
	
	@property
	def create_view_name(self):
		return f"{self.model_string}_create"
	
	@property
	def update_view_name(self):
		return f"{self.model_string}_update"
	
	@property
	def delete_view_name(self):
		return f"{self.model_string}_delete"
	
	# Plantilla para crear o actualizar el modelo
	# template_form = f"{app_label}/{model_string}_form.html"
	
	@property
	def template_form(self):
		return f"{self.app_label}/{self.model_string}_form.html"
	
	
	# Plantilla para confirmar eliminación de un registro
	# template_delete = "base_confirm_delete.html"
 
	@property
	def template_delete(self):
		return "base_confirm_delete.html"
	
	# Plantilla de la lista del CRUD
	# template_list = f'{app_label}/maestro_list.html'
	
	@property
	def template_list(self):
		return f'{self.app_label}/maestro_list.html'
	
	# Contexto de los datos de la lista
	# context_object_name	= 'objetos'
 
	@property
	def context_object_name(self):
		return 'objetos'
	
	# Vista del home del proyecto
	# home_view_name = "home"
 
	@property
	def home_view_name(self):
		return "home"
	
	# Nombre de la url 
	# success_url = reverse_lazy(list_view_name)
	
	@property
	def success_url(self):
		return reverse_lazy(self.list_view_name)


class BaseDataViewList():
	search_fields = []
	
	ordering = []
	
	paginate_by = 8
	  
	table_headers = {}
	
	table_data = []

# BaseListView - Inicio
class BaseListView(MaestroListView):
	model = BaseConfigViews.model
	template_name = BaseConfigViews.template_list
	context_object_name = BaseConfigViews.context_object_name
	
	search_fields = BaseDataViewList.search_fields
	ordering = BaseDataViewList.ordering
	
	# extra_context = {
	# 	"master_title": BaseConfigViews.model._meta.verbose_name_plural,
	# 	"home_view_name": BaseConfigViews.home_view_name,
	# 	"list_view_name": BaseConfigViews.list_view_name,
	# 	"create_view_name": BaseConfigViews.create_view_name,
	# 	"update_view_name": BaseConfigViews.update_view_name,
	# 	"delete_view_name": BaseConfigViews.delete_view_name,
	# 	"table_headers": BaseDataViewList.table_headers,
	# 	"table_data": BaseDataViewList.table_data,
	# }
 
	def get_extra_context(self, **kwargs):
		extra_context = super().get_extra_context(**kwargs)
		extra_context.update({
			"master_title": self.model._meta.verbose_name_plural,
			"home_view_name": BaseConfigViews.home_view_name,
			"list_view_name": BaseConfigViews.list_view_name,
			"create_view_name": BaseConfigViews.create_view_name,
			"update_view_name": BaseConfigViews.update_view_name,
			"delete_view_name": BaseConfigViews.delete_view_name,
			"table_headers": BaseDataViewList.table_headers,
			"table_data": BaseDataViewList.table_data,
		})
		return extra_context

# BaseCreateView - Inicio
class BaseCreateView(MaestroCreateView):
	model = BaseConfigViews.model
	list_view_name = BaseConfigViews.list_view_name
	form_class = BaseConfigViews.form_class
	template_name = BaseConfigViews.template_form
	success_url = BaseConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	# (revisar de donde lo copiaste que tienes asignado permission_change en vez de permission_add)
	permission_required = BaseConfigViews.permission_add
	
	# extra_context = {
	# 	"accion": f"Editar {BaseConfigViews.model._meta.verbose_name}",
	# 	"list_view_name" : BaseConfigViews.list_view_name
	# }

	def get_extra_context(self, **kwargs):
			extra_context = super().get_extra_context(**kwargs)
			extra_context.update({
				"accion": f"Crear {self.model._meta.verbose_name}",
				"list_view_name": self.list_view_name,
			})
			return extra_context	

# BaseUpdateView
class BaseUpdateView(MaestroUpdateView):
	model = BaseConfigViews.model
	list_view_name = BaseConfigViews.list_view_name
	form_class = BaseConfigViews.form_class
	template_name = BaseConfigViews.template_form
	success_url = BaseConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = BaseConfigViews.permission_change
	
	# extra_context = {
	# 	"accion": f"Editar {BaseConfigViews.model._meta.verbose_name}",
	# 	"list_view_name" : BaseConfigViews.list_view_name
	# }

	def get_extra_context(self, **kwargs):
		extra_context = super().get_extra_context(**kwargs)
		extra_context.update({
            "accion": f"Editar {self.model._meta.verbose_name}",
            "list_view_name": self.list_view_name,
        })
		return extra_context

# BaseDeleteView
class BaseDeleteView (MaestroDeleteView):
	model = BaseConfigViews.model
	list_view_name = BaseConfigViews.list_view_name
	template_name = BaseConfigViews.template_delete
	success_url = BaseConfigViews.success_url
	
	#-- Indicar el permiso que requiere para ejecutar la acción.
	permission_required = BaseConfigViews.permission_delete
	
	# extra_context = {
	# 	"accion": f"Eliminar {BaseConfigViews.model._meta.verbose_name}",
	# 	"list_view_name" : BaseConfigViews.list_view_name,
	# 	"mensaje": "Estás seguro de eliminar el Registro"
	# }

	def get_extra_context(self, **kwargs):
		extra_context = super().get_extra_context(**kwargs)
		extra_context.update({
            "accion": f"Eliminar {self.model._meta.verbose_name}",
            "list_view_name": self.list_view_name,
            "mensaje": "Estás seguro de eliminar el Registro",
        })
		return extra_context