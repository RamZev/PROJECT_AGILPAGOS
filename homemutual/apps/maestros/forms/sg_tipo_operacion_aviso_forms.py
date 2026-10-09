# apps/maestros/forms/sg_tipo_operacion_aviso_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgTipoOperacionAviso
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgTipoOperacionAvisoForm(CrudGenericForm):
    """Formulario para el modelo SgTipoOperacionAviso"""

    class Meta:
        model = SgTipoOperacionAviso
        fields = [
            'id_sg_tipo_operacion_aviso',
            'descripcion',
            'estatus_sg_tipo_operacion_aviso',
        ]
        widgets = {
            'id_sg_tipo_operacion_aviso': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos (ej: 883E49C3-7AA2-42B7-A258-DEF8A6C6E838)'
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Transferencias, Operación con QR, etc.'
            }),
            'estatus_sg_tipo_operacion_aviso': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_tipo_operacion_aviso': 'ID Agilpagos',
            'descripcion': 'Descripción',
            'estatus_sg_tipo_operacion_aviso': 'Activo',
        }
        help_texts = {
            'id_sg_tipo_operacion_aviso': 'GUID de Agilpagos (PK del registro).',
            'descripcion': 'Descripción del tipo de operación de aviso (ej: Transferencias, Operación con QR, etc.)',
            'estatus_sg_tipo_operacion_aviso': 'Indica si el registro está activo.',
        }