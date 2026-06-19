# apps/maestros/forms/sg_estado_civil_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgEstadoCivil
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgEstadoCivilForm(CrudGenericForm):
    """Formulario para el modelo SgEstadoCivil"""
    
    class Meta:
        model = SgEstadoCivil
        fields = [
            'id_sg_estado_civil',
            'descripcion',
            'estatus_sg_estado_civil',
        ]
        widgets = {
            'id_sg_estado_civil': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos (ej: 13e36b73-183f-4575-8d18-5c94543d2e07)'
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Soltero, Casado, Divorciado, Viudo, etc.'
            }),
            'estatus_sg_estado_civil': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_estado_civil': 'ID Agilpagos',
            'descripcion': 'Descripción',
            'estatus_sg_estado_civil': 'Activo',
        }
        help_texts = {
            'id_sg_estado_civil': 'GUID de Agilpagos (ej: 13e36b73-183f-4575-8d18-5c94543d2e07)',
            'descripcion': 'Estado civil (ej: Soltero, Casado, Divorciado, Viudo, etc.)',
        }