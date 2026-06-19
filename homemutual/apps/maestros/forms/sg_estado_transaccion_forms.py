# apps/maestros/forms/sg_estado_transaccion_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgEstadoTransaccion
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgEstadoTransaccionForm(CrudGenericForm):
    """Formulario para el modelo SgEstadoTransaccion"""
    
    class Meta:
        model = SgEstadoTransaccion
        fields = [
            'id_sg_estado_transaccion',
            'codigo',
            'descripcion',
            'es_final',
            'estatus_sg_estado_transaccion',
        ]
        widgets = {
            'id_sg_estado_transaccion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos (ej: 5FB79B38-00ED-47B8-B7CE-B760CBEAE9D8)'
            }),
            'codigo': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Procesado, Pendiente, Error, etc.'
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Descripción del estado'
            }),
            'es_final': forms.Select(attrs={**formclassselect}),
            'estatus_sg_estado_transaccion': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_estado_transaccion': 'ID Agilpagos',
            'codigo': 'Código',
            'descripcion': 'Descripción',
            'es_final': 'Es Estado Final',
            'estatus_sg_estado_transaccion': 'Activo',
        }
        help_texts = {
            'id_sg_estado_transaccion': 'GUID de Agilpagos del estado de transacción',
            'codigo': 'Código del estado (ej: Procesado, Pendiente, Error)',
            'descripcion': 'Descripción del estado',
            'es_final': 'Indica si es un estado final (terminó el proceso)',
        }