# apps/maestros/forms/sg_ambiente_agilpagos_forms.py
from django import forms
from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.sg_catalogo_models import SgAmbienteAgilpagos
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class SgAmbienteAgilpagosForm(CrudGenericForm):
    """Formulario para el modelo SgAmbienteAgilpagos"""

    class Meta:
        model = SgAmbienteAgilpagos
        fields = [
            'id_sg_ambiente_agilpagos',
            'nombre',
            'url_base',
            'url_onboarding',
            'url_swagger',
            'id_entidad',
            'id_entidad_tipo_documento',
            'estatus_sg_ambiente_agilpagos',
        ]
        widgets = {
            'id_sg_ambiente_agilpagos': forms.NumberInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: 1, 2'
            }),
            'nombre': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: UAT, PROD'
            }),
            'url_base': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: https://agilpagosapi.maasoft.com.ar'
            }),
            'url_onboarding': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: https://agilpagosapi.maasoft.com.ar/onboarding'
            }),
            'url_swagger': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: https://agilpagosapi.maasoft.com.ar/swagger'
            }),
            'id_entidad': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de la entidad'
            }),
            'id_entidad_tipo_documento': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'GUID de la entidad para el tipo de documento'
            }),
            'estatus_sg_ambiente_agilpagos': forms.Select(attrs={**formclassselect}),
        }
        labels = {
            'id_sg_ambiente_agilpagos': 'ID Ambiente',
            'nombre': 'Nombre',
            'url_base': 'URL Base',
            'url_onboarding': 'URL Onboarding',
            'url_swagger': 'URL Swagger',
            'id_entidad': 'ID Entidad',
            'id_entidad_tipo_documento': 'ID Entidad Tipo Documento',
            'estatus_sg_ambiente_agilpagos': 'Activo',
        }
        help_texts = {
            'id_sg_ambiente_agilpagos': 'Identificador numérico del ambiente.',
            'nombre': 'Nombre del ambiente (ej: UAT, PROD). Debe ser único.',
            'url_base': 'URL base del ambiente (ej: https://agilpagosapi.maasoft.com.ar).',
            'url_onboarding': 'URL del servicio de Onboarding.',
            'url_swagger': 'URL de la documentación Swagger.',
            'id_entidad': 'GUID de la entidad en Agilpagos.',
            'id_entidad_tipo_documento': 'GUID de la entidad para el tipo de documento.',
            'estatus_sg_ambiente_agilpagos': 'Indica si el registro está activo.',
        }