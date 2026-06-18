# homemutual\apps\integraciones\forms\sg_tipo_cuenta_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.sg_catalogo_models import SgTipoCuenta
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)

class SgTipoCuentaForm(CrudGenericForm):

	class Meta:
		model = SgTipoCuenta
		fields = '__all__'
		
		widgets = {
			'estatus_sg_tipo_cuenta':
				forms.Select(attrs={**formclassselect}),
			'id_sg_tipo_cuenta':
                forms.TextInput(attrs={**formclasstext}),
			'tipo_cuenta':
				forms.TextInput(attrs={**formclasstext}),
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)