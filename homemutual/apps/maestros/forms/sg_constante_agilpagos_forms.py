# apps/maestros/forms/sg_constante_agilpagos_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgConstanteAgilpagos
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgConstanteAgilpagosForm(CrudGenericForm):
    """Formulario para el modelo SgConstanteAgilpagos"""

    class Meta:
        model = SgConstanteAgilpagos
        fields = [
            'clave',
            'valor',
            'descripcion',
            'estatus_sg_constante_agilpagos',
        ]
        widgets = {
            'clave': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: ID_TIPO_DOCUMENTO_DNI'
            }),
            'valor': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: 209C1CAA-C56D-4E03-BB40-E9EF2F319A3F'
            }),
            'descripcion': forms.Textarea(attrs={
                **formclasstext,
                'rows': 3,
                'placeholder': 'Descripción de la constante.'
            }),
            'estatus_sg_constante_agilpagos': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'clave': 'Clave',
            'valor': 'Valor',
            'descripcion': 'Descripción',
            'estatus_sg_constante_agilpagos': 'Activo',
        }
        help_texts = {
            'clave': 'Clave de la constante (ej: ID_TIPO_DOCUMENTO_DNI). Es la PK.',
            'valor': 'Valor de la constante (ej: GUID o número).',
            'descripcion': 'Descripción del uso de la constante.',
            'estatus_sg_constante_agilpagos': 'Indica si el registro está activo.',
        }