# apps/maestros/forms/sg_tipo_cuenta_mutual_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgTipoCuentaMutual
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgTipoCuentaMutualForm(CrudGenericForm):
    """Formulario para el modelo SgTipoCuentaMutual"""

    class Meta:
        model = SgTipoCuentaMutual
        fields = [
            'id_sg_tipo_cuenta_mutual',
            'codigo_letra',
            'descripcion',
            'estatus_sg_tipo_cuenta_mutual',
        ]
        widgets = {
            'id_sg_tipo_cuenta_mutual': forms.NumberInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: 1, 2, 3'
            }),
            'codigo_letra': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: C, E, D',
                'maxlength': '1',
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Caja de Ahorro Común, Caja de Ahorro Especial, etc.'
            }),
            'estatus_sg_tipo_cuenta_mutual': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_tipo_cuenta_mutual': 'ID Tipo Cuenta',
            'codigo_letra': 'Código Letra',
            'descripcion': 'Descripción',
            'estatus_sg_tipo_cuenta_mutual': 'Activo',
        }
        help_texts = {
            'id_sg_tipo_cuenta_mutual': 'Identificador numérico del tipo de cuenta (1=Común, 2=Especial, 3=Diferencial).',
            'codigo_letra': 'Letra que identifica el tipo (C, E o D). Debe ser única.',
            'descripcion': 'Descripción del tipo de cuenta mutual (ej: Caja de Ahorro Común).',
            'estatus_sg_tipo_cuenta_mutual': 'Indica si el registro está activo.',
        }