# neumatic\apps\menu\models.py
from django.db import models
from django.contrib.auth.models import Group
from django.utils.text import slugify


class MenuHeading(models.Model):
	id_menu_heading = models.AutoField(
		verbose_name="ID Encabezado de Menú",
		primary_key=True
	)
	name = models.CharField(
		verbose_name="Nombre del encabezado",
		max_length=100
	)
	order = models.IntegerField(
		verbose_name="Orden de aparición",
		default=0
	)
	
	class Meta:
		ordering = ['order', 'name']
		verbose_name = "Encabezado de Menú"
		verbose_name_plural = "Encabezados de Menú"
	
	def __str__(self):
		return self.name


class MenuItem(models.Model):
	id_menu_item = models.AutoField(
		verbose_name="ID Item de Menú",
		primary_key=True
	)
	heading = models.ForeignKey(
		MenuHeading,
		on_delete=models.CASCADE,
		verbose_name="Encabezado asociado",
		null=True,
		blank=True,
	)
	parent = models.ForeignKey(
		'self',
		on_delete=models.CASCADE,
		verbose_name="Item padre",
		related_name='children',
		null=True,
		blank=True
	)
	name = models.CharField(
		verbose_name="Nombre del item",
		max_length=100
	)
	url_name = models.CharField(
		verbose_name="Nombre de la URL (para {% url %})",
		max_length=100,
		blank=True
	)
	query_params = models.CharField(
		verbose_name="Parámetros de query (ej: ?proceso=actualizar)",
		max_length=200,
		blank=True
	)
	icon = models.CharField(
		verbose_name="Clase del icono (ej: fas fa-book-open)",
		max_length=50,
		blank=True
	)
	is_collapse = models.BooleanField(
		verbose_name="¿Es colapsable? (tiene subitems)",
		default=False
	)
	order = models.IntegerField(
		verbose_name="Orden de aparición",
		blank=True,
		default=0
	)
	groups = models.ManyToManyField(
		Group,
		verbose_name="Grupos permitidos",
		blank=True
	)
	
	class Meta:
		ordering = ['order', 'name']
		verbose_name = "Item de Menú"
		verbose_name_plural = "Items de Menú"
	
	def __str__(self):
		return self.name
	
	def get_collapse_id(self):
		return f"collapse{slugify(self.name).capitalize()}"
	
	def has_access(self, user, check_children=True):
		
		#-- Superusuarios tienen acceso completo.
		if user.is_superuser:
			return True
		
		#-- Si el item tiene grupos asignados, verificar acceso directo.
		if self.groups.exists():
			user_has_group = user.groups.filter(pk__in=self.groups.values_list('pk', flat=True)).exists()
			result = user_has_group
			return result
		
		#-- Si es un item final (no colapsible) y no tiene grupos, no es accesible.
		if not self.is_collapse:
			return False
		
		#-- Si es un item colapsable (padre) y no tiene grupos, verificar si tiene hijos accesibles.
		if check_children and self.is_collapse and self.children.exists():
			#-- Verificar recursivamente si algún hijo tiene acceso.
			for child in self.children.all():
				if child.has_access(user, check_children=True):
					return True
		
		#-- Si no cumple ninguna condición, no es accesible.
		return False