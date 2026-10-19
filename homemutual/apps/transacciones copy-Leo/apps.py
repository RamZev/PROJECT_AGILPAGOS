from django.apps import AppConfig


class TransaccionesConfig(AppConfig):
	name = 'apps.transacciones'
	
	def ready(self):
		import apps.transacciones.models.transacciones_models
		
