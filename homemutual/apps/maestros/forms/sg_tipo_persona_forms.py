# homemutual\apps\integraciones\forms\sg_tipo_persona_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.sg_catalogo_models import SgTipoPersona
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)

class SgTipoPersonaForm(CrudGenericForm):

	class Meta:
		model = SgTipoPersona
		fields = '__all__'
		
		widgets = {
			'estatus_sg_tipo_persona':
				forms.Select(attrs={**formclassselect}),
			'id_sg_tipo_persona':
				forms.TextInput(attrs={**formclasstext}),
			'tipo_persona':
				forms.TextInput(attrs={**formclasstext}),
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
