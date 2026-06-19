# apps/maestros/forms/sg_ocupacion_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgOcupacion
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgOcupacionForm(CrudGenericForm):
    """Formulario para el modelo SgOcupacion"""
    
    class Meta:
        model = SgOcupacion
        fields = [
            'id_sg_ocupacion',
            'descripcion',
            'estatus_sg_ocupacion',
        ]
        widgets = {
            'id_sg_ocupacion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos (ej: d0ce590e-ab68-4044-b184-3f2063845ed5)'
            }),
            'descripcion': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Comerciante, Empleado, Profesional, Jubilado, etc.'
            }),
            'estatus_sg_ocupacion': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_ocupacion': 'ID Agilpagos',
            'descripcion': 'Descripción',
            'estatus_sg_ocupacion': 'Activo',
        }
        help_texts = {
            'id_sg_ocupacion': 'GUID de Agilpagos (ej: d0ce590e-ab68-4044-b184-3f2063845ed5)',
            'descripcion': 'Ocupación (ej: Comerciante, Empleado, Profesional, Jubilado, etc.)',
        }