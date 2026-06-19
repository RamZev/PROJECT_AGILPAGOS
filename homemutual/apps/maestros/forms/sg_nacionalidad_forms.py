# apps/maestros/forms/sg_nacionalidad_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgNacionalidad
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgNacionalidadForm(CrudGenericForm):
    """Formulario para el modelo SgNacionalidad"""
    
    class Meta:
        model = SgNacionalidad
        fields = [
            'id_sg_nacionalidad',
            'descripcion',
            'estatus_sg_nacionalidad',
        ]
        widgets = {
            'id_sg_nacionalidad': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos (ej: 76B19E61-B8DC-40F4-BFAB-422C8FFE5002)'
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Argentina, Uruguaya, etc.'
            }),
            'estatus_sg_nacionalidad': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_nacionalidad': 'ID Agilpagos',
            'descripcion': 'Descripción',
            'estatus_sg_nacionalidad': 'Activo',
        }
        help_texts = {
            'id_sg_nacionalidad': 'GUID de Agilpagos (ej: 76B19E61-B8DC-40F4-BFAB-422C8FFE5002)',
            'descripcion': 'Nombre de la nacionalidad (ej: Argentina, Uruguaya, etc.)',
        }