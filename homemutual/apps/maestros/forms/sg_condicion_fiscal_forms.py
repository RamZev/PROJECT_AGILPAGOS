# apps/maestros/forms/sg_condicion_fiscal_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgCondicionFiscal
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgCondicionFiscalForm(CrudGenericForm):
    """Formulario para el modelo SgCondicionFiscal"""
    
    class Meta:
        model = SgCondicionFiscal
        fields = [
            'id_sg_condicion_fiscal',
            'descripcion',
            'estatus_sg_condicion_fiscal',
        ]
        widgets = {
            'id_sg_condicion_fiscal': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos (ej: ba933f3f-d18e-4aed-8585-dfa73e27da11)'
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Consumidor Final, Responsable Inscripto, Monotributista, etc.'
            }),
            'estatus_sg_condicion_fiscal': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_condicion_fiscal': 'ID Agilpagos',
            'descripcion': 'Descripción',
            'estatus_sg_condicion_fiscal': 'Activo',
        }
        help_texts = {
            'id_sg_condicion_fiscal': 'GUID de Agilpagos (ej: ba933f3f-d18e-4aed-8585-dfa73e27da11)',
            'descripcion': 'Condición fiscal (ej: Consumidor Final, Responsable Inscripto, Monotributista, etc.)',
        }