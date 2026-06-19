# apps/maestros/forms/sg_provincia_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgProvincia
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgProvinciaForm(CrudGenericForm):
    """Formulario para el modelo SgProvincia"""
    
    class Meta:
        model = SgProvincia
        fields = [
            'id_sg_provincia',
            'codigo_iso',
            'nombre_provincia',
            'id_pais',
            'nombre_pais',
            'estatus_sg_provincia',
        ]
        widgets = {
            'id_sg_provincia': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de Agilpagos (ej: 169c998a-2d9d-4077-a1a0-3e5586d31059)'
            }),
            'codigo_iso': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Código ISO (ej: AR-K)'
            }),
            'nombre_provincia': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Catamarca, Buenos Aires, etc.'
            }),
            'id_pais': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'AC98A1E7-CF65-4430-BF16-24439F35853B',
                'readonly': True,
            }),
            'nombre_pais': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Argentina',
                'readonly': True,
            }),
            'estatus_sg_provincia': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_provincia': 'ID Agilpagos',
            'codigo_iso': 'Código ISO',
            'nombre_provincia': 'Nombre Provincia',
            'id_pais': 'ID País',
            'nombre_pais': 'Nombre País',
            'estatus_sg_provincia': 'Activo',
        }
        help_texts = {
            'id_sg_provincia': 'GUID de Agilpagos (ej: 169c998a-2d9d-4077-a1a0-3e5586d31059)',
            'codigo_iso': 'Código ISO de la provincia (ej: AR-K)',
            'nombre_provincia': 'Nombre de la provincia (ej: Catamarca, Buenos Aires, etc.)',
            'id_pais': 'Siempre Argentina: AC98A1E7-CF65-4430-BF16-24439F35853B',
            'nombre_pais': 'Siempre Argentina',
        }