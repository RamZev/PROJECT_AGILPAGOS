# D:\PROJECT_NEUMATIC\neumatic\apps\usuarios\views\user_views_generics.py
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q


#-- Vistas Genéricas Basada en Clases 

class GenericLoginView(LoginView):
	pass

class GenericLogoutView(LogoutView):
	pass

class GenericListView(ListView):
	cadena_filtro = ""
	
	def get_queryset(self):
		queryset = super().get_queryset()
		text = self.request.GET.get('buscar', '')
		if text and self.cadena_filtro:
			queryset = queryset.filter( eval(self.cadena_filtro) )
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["buscar"] = self.request.GET.get('buscar', '')
		return context

class GenericCreateView(CreateView):
	pass

class GenericUpdateView(UpdateView):
	#-- Nombre del argumento de clave primaria pasado en el url. Por defecto es pk.
	#pk_url_kwarg = "id"
	pass

class GenericDeleteView(DeleteView):
	#-- Nombre del argumento de clave primaria pasado en el url. Por defecto es pk.
	#pk_url_kwarg = "id"
	pass



