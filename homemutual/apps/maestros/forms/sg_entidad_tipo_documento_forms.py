# homemutual\apps\integraciones\forms\sg_entidad_tipo_documento_forms.py
from django import forms
from .crud_forms_generics import CrudGenericForm
from ..models.sg_catalogo_models import SgEntidadTipoDocumento
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect)

class SgEntidadTipoDocumentoForm(CrudGenericForm):

	class Meta:
		model = SgEntidadTipoDocumento
		fields = '__all__'
		
		widgets = {
			'estatus_sg_entidad_tipo_documento':
				forms.Select(attrs={**formclassselect}),
			'id_sg_entidad_tipo_documento':
				forms.TextInput(attrs={**formclasstext}),
			'nombre':
				forms.TextInput(attrs={**formclasstext}),
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
