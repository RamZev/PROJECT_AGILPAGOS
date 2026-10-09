# apps/maestros/forms/sg_tipo_impuesto_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgTipoImpuesto
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgTipoImpuestoForm(CrudGenericForm):
    """Formulario para el modelo SgTipoImpuesto"""

    class Meta:
        model = SgTipoImpuesto
        fields = [
            'id_sg_tipo_impuesto',
            'descripcion',
            'estatus_sg_tipo_impuesto',
        ]
        widgets = {
            'id_sg_tipo_impuesto': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos (ej: A1254625-BA0F-474D-AD9D-15816099743C)'
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Impuesto SIRCUPA, Impuesto Ley 25.413, etc.'
            }),
            'estatus_sg_tipo_impuesto': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_tipo_impuesto': 'ID Agilpagos',
            'descripcion': 'Descripción',
            'estatus_sg_tipo_impuesto': 'Activo',
        }
        help_texts = {
            'id_sg_tipo_impuesto': 'GUID de Agilpagos (PK del registro).',
            'descripcion': 'Descripción del tipo de impuesto (ej: Impuesto SIRCUPA, Impuesto Ley 25.413, etc.)',
            'estatus_sg_tipo_impuesto': 'Indica si el registro está activo.',
        }