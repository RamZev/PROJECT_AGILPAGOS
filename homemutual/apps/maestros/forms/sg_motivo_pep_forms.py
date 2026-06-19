# apps/maestros/forms/sg_motivo_pep_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgMotivoPEP
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgMotivoPEPForm(CrudGenericForm):
    """Formulario para el modelo SgMotivoPEP"""
    
    class Meta:
        model = SgMotivoPEP
        fields = [
            'id_sg_motivo_pep',
            'descripcion',
            'estatus_sg_motivo_pep',
        ]
        widgets = {
            'id_sg_motivo_pep': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos'
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Funcionario Público, Familiar de Funcionario, etc.'
            }),
            'estatus_sg_motivo_pep': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_motivo_pep': 'ID Agilpagos',
            'descripcion': 'Descripción',
            'estatus_sg_motivo_pep': 'Activo',
        }
        help_texts = {
            'id_sg_motivo_pep': 'GUID de Agilpagos del motivo PEP',
            'descripcion': 'Motivo por el cual es Persona Expuesta Políticamente',
        }