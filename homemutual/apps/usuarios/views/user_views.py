# neumatic\apps\usuarios\views\user_views.py
from django.urls import reverse_lazy

#from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
#from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate
from django.contrib import messages

from .user_views_generics import *
from apps.usuarios.forms.user_form import *

#from apps.usuarios.models.user_models import User
from apps.usuarios.models import User


#-- Indicar las aplicaciones del proyecto para poder filtrar los modelos de las mismas.
# project_app_labels = ['usuarios', 'maestros', 'ventas']
project_app_labels = ['usuarios', 'maestros']

#-- Vista Login. 
class CustomLoginView(GenericLoginView):
	template_name = 'usuarios/sesion_iniciar.html'
	
	def form_valid(self, form):
		#-- Llama al método original para autenticar al usuario.
		response = super().form_valid(form)
		
		#-- Obtener el usuario autenticado.
		user = form.get_user()
		
		#-- Guardar los datos del usuario en la sesión.
		self.request.session['username'] = user.username
		self.request.session['first_name'] = user.first_name
		self.request.session['last_name'] = user.last_name
		self.request.session['is_superuser'] = user.is_superuser
		self.request.session['is_staff'] = user.is_staff
		
		return response
	
	def form_invalid(self, form):
		#-- Obtiene el nombre de usuario y contraseña enviados.
		username = form.data.get("username")
		password = form.data.get("password")
		
		#-- Verifica si el campo de usuario está vacío.
		if not username:
			messages.error(self.request, "El campo de usuario es obligatorio.")
		elif not password:
			messages.error(self.request, "El campo de contraseña es obligatorio.")
		else:
			#-- Verifica si el usuario existe en la base de datos.
			try:
				user = User.objects.get(username=username)
				#-- Verifica si el usuario está activo.
				if not user.is_active:
					messages.error(self.request, "El usuario no está activo.")
				else:
					#-- Si el usuario está activo, intenta autenticar.
					user = authenticate(username=username, password=password)
					if not user:
						messages.error(self.request, "Contraseña incorrecta.")
			except User.DoesNotExist:
				messages.error(self.request, "El usuario no existe.")
		
		#-- Llama a form_invalid para manejar el error.
		return super().form_invalid(form)


#-- Vista Logout. 
class CustomLogoutView(GenericLogoutView):
	template_name = 'usuarios/sesion_cerrar.html'
	http_method_names = ["get", "post", "options"]  # He tenido que incluir el método GET para que funcione. NO DEBERÍA SER!!!
	
	def dispatch(self, request, *args, **kwargs):
		
		#-- Verificar si la solicitud proviene de una confirmación de logout.
		if request.method == "POST" and request.POST.get("confirm_logout") == "true":		
			#-- Limpiar los datos del usuario de la sesión.
			request.session.pop('username', None)
			request.session.pop('first_name', None)
			request.session.pop('last_name', None)
			request.session.pop('is_superuser', None)
			request.session.pop('is_staff', None)
		 
		#-- Llama al método original para cerrar la sesión.
		return super().dispatch(request, *args, **kwargs)

#-- Vistas de Grupos de usuarios. 
#@method_decorator(login_required, name='dispatch')
class GrupoListView(GenericListView):
	model = Group
	context_object_name = 'grupos'
	template_name = "usuarios/grupo_list.html"
	cadena_filtro = "Q(name__icontains=text)"
	extra_context = {
		"home_view_name": "home",
	}


#@method_decorator(login_required, name='dispatch')
class GrupoCreateView(GenericCreateView):
	model = Group
	form_class = GroupForm
	template_name = "usuarios/grupo_form.html"
	success_url = reverse_lazy("grupo_listar") # Nombre de la url.
	extra_context = {
		"accion": "Nuevo Grupo",
		"list_view_name": "grupo_listar"
	}


#@method_decorator(login_required, name='dispatch')
class GrupoUpdateView(GenericUpdateView):
	model = Group
	form_class = GroupForm
	template_name = "usuarios/grupo_form.html"
	success_url = reverse_lazy("grupo_listar")
	extra_context = {
		"accion": "Editar Grupo",
		"list_view_name": "grupo_listar"
	}
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		#-- Instancia del grupo que se edita.
		grupo = self.get_object()
		#-- Obtener los permisos asignados al grupo.
		permisos_asignados = grupo.permissions.all()
		
		#-- Obtener permisos disponibles.
		#-- Filtrar ContentTypes para solo incluir los de las apps del proyecto.
		project_content_types = ContentType.objects.filter(app_label__in=project_app_labels)
		#-- Obtener permisos basados en los ContentTypes filtrados.
		permisos_disponibles = Permission.objects.filter(content_type__in=project_content_types)
		
		context["permisos_asignados"] = permisos_asignados
		context["permisos_disponibles"] = permisos_disponibles
		
		return context
	
	def form_valid(self, form):
		# Guarda el formulario y realiza otras operaciones necesarias
		response = super().form_valid(form)
		
		# Procesa los permisos asignados y guarda en la base de datos
		permisos_asignados = self.request.POST.getlist('permisos_asignados')
		
		grupo = self.get_object()
		grupo.permissions.set(permisos_asignados)
		return response	


#@method_decorator(login_required, name='dispatch')
class GrupoDeleteView(GenericDeleteView):
	model = Group
	template_name = "usuarios/grupo_confirm_delete.html"
	success_url = reverse_lazy("grupo_listar") # Nombre de la url.
	extra_context = {
		"accion": "Eliminar Grupo",
		"list_view_name": "grupo_listar"
	}


#-- Vistas de Usuarios.
#@method_decorator(login_required, name='dispatch')
class UsuarioListView(GenericListView):
	model = User
	context_object_name = 'usuarios'
	template_name = "usuarios/usuario_list.html"
	cadena_filtro = "Q(username__icontains=text) | Q(first_name__icontains=text) | Q(last_name__icontains=text) | Q(email__icontains=text)"
	extra_context = {
		"home_view_name": "home",
	}


#@method_decorator(login_required, name='dispatch')
class UsuarioCreateView(GenericCreateView):
	model = User
	form_class = RegistroUsuarioForm
	template_name = "usuarios/usuario_crear_form.html"
	success_url = reverse_lazy("usuario_listar") # Nombre de la url.
	extra_context = {
		"accion": "Registro de Usuario",
		"list_view_name": "usuario_listar"
	}


#@method_decorator(login_required, name='dispatch')
class UsuarioUpdateView(GenericUpdateView):
	model = User
	form_class = EditarUsuarioForm
	template_name = "usuarios/usuario_editar_form.html"
	success_url = reverse_lazy("usuario_listar") # Nombre de la url.
	extra_context = {
		"accion": "Editar Usuario",
		"list_view_name": "usuario_listar"
	}
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		#-- Instancia del grupo que se edita.
		usuario = self.get_object()
		#-- Obtener los permisos asignados al grupo.
		permisos_asignados = usuario.user_permissions.all()
		
		#-- Obtener permisos disponibles.
		#-- Filtrar ContentTypes para solo incluir los de las apps del proyecto.
		project_content_types = ContentType.objects.filter(app_label__in=project_app_labels)
		#-- Obtener permisos basados en los ContentTypes filtrados.
		permisos_disponibles = Permission.objects.filter(content_type__in=project_content_types)
		
		#-- Obtener grupos asignados.
		grupos_asignados = usuario.groups.all()
		#-- Obtener grupos disponibles.
		grupos_disponibles = Group.objects.all()
		
		context["grupos_asignados"] = grupos_asignados
		context["grupos_disponibles"] = grupos_disponibles
		context["permisos_asignados"] = permisos_asignados
		context["permisos_disponibles"] = permisos_disponibles
		
		return context
	
	def form_valid(self, form):
		# Guarda el formulario y realiza otras operaciones necesarias
		response = super().form_valid(form)
		
		# Procesa los grupos y/o permisos asignados y guarda en la base de datos
		grupos_asignados = self.request.POST.getlist('grupos_asignados')
		permisos_asignados = self.request.POST.getlist('permisos_asignados')
		
		usuario = self.get_object()
		usuario.groups.set(grupos_asignados)
		usuario.user_permissions.set(permisos_asignados)
		
		return response	
	
#@method_decorator(login_required, name='dispatch')
class UsuarioDeleteView(GenericDeleteView):
	model = User
	template_name = "usuarios/usuario_confirm_delete.html"
	success_url = reverse_lazy("usuario_listar") # Nombre de la url.
	extra_context = {
		"accion": "Eliminar Usuario",
		"list_view_name": "usuario_listar"
	}

