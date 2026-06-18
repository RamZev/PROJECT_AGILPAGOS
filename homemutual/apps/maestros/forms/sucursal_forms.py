# homemutual\apps\maestros\forms\sucursal_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.sucursal_models import Sucursal
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)


class SucursalForm(CrudGenericForm):

	class Meta:
		model = Sucursal
		fields = '__all__'
		
		widgets = {
			'estatus_sucursal':
				forms.Select(attrs={**formclassselect}),
			'nombre_sucursal':
				forms.TextInput(attrs={**formclasstext}),
			'domicilio_sucursal':
				forms.TextInput(attrs={**formclasstext}),
			'telefono_sucursal':
				forms.TextInput(attrs={**formclasstext}),
			'email_sucursal':
				forms.EmailInput(attrs={**formclasstext}),
			'ws_url':
				forms.TextInput(attrs={**formclasstext}),
			'ws_token_acceso':
				forms.TextInput(attrs={**formclasstext}),
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
