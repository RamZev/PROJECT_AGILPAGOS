# apps/maestros/forms/sg_concepto_transaccion_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgConceptoTransaccion
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgConceptoTransaccionForm(CrudGenericForm):
    """Formulario para el modelo SgConceptoTransaccion"""

    class Meta:
        model = SgConceptoTransaccion
        fields = [
            'id_sg_concepto_transaccion',
            'codigo',
            'descripcion',
            'guid',
            'estatus_sg_concepto_transaccion',
        ]
        widgets = {
            'id_sg_concepto_transaccion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos (ej: 45D4F58B-46A2-4754-BBFA-FECB8CF88BFC)'
            }),
            'codigo': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: VAR, ALQ, EXP, FAC, HON'
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Varios, Alquileres, Expensas, etc.'
            }),
            'guid': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID del concepto en Agilpagos'
            }),
            'estatus_sg_concepto_transaccion': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_concepto_transaccion': 'ID Agilpagos',
            'codigo': 'Código',
            'descripcion': 'Descripción',
            'guid': 'GUID',
            'estatus_sg_concepto_transaccion': 'Activo',
        }
        help_texts = {
            'id_sg_concepto_transaccion': 'GUID de Agilpagos (PK del registro).',
            'codigo': 'Código del concepto (ej: VAR, ALQ, EXP, FAC, HON)',
            'descripcion': 'Descripción del concepto (ej: Varios, Alquileres, Expensas, etc.)',
            'guid': 'GUID del concepto en Agilpagos.',
            'estatus_sg_concepto_transaccion': 'Indica si el registro está activo.',
        }