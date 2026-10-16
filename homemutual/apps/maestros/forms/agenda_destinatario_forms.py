# apps/maestros/forms/agenda_destinatario_forms.py
import re
from django import forms
from django.core.exceptions import ValidationError

from .crud_forms_generics import CrudGenericForm
from ..models.agenda_destinatarios_models import AgendaDestinatario
from ..models.socio_models import Socio
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class AgendaDestinatarioForm(CrudGenericForm):
    """Formulario para el modelo AgendaDestinatario"""

    # ---- Socio: dropdown ----
    id_socio = forms.ModelChoiceField(
        queryset=Socio.objects.filter(estado=True).order_by('id_socio_mutual'),
        required=True,
        empty_label="-- Seleccionar Socio --",
        label="Socio",
        widget=forms.Select(attrs={**formclassselect}),
    )

    # ---- Tipo de persona ----
    tipo_persona = forms.ChoiceField(
        choices=(
            ('', '-- Seleccionar --'),
            ('FISICA', 'Física'),
            ('JURIDICA', 'Jurídica'),
        ),
        required=False,
        label="Tipo de Persona",
        widget=forms.Select(attrs={**formclassselect}),
    )

    # ---- Frecuente: select SI/NO ----
    frecuente = forms.ChoiceField(
        choices=((True, 'SI'), (False, 'NO')),
        required=True,
        initial=False,
        label="Frecuente",
        widget=forms.Select(attrs={**formclassselect}),
    )

    class Meta:
        model = AgendaDestinatario
        fields = [
            'id_socio',
            'cvu_o_cbu',
            'alias',
            'cuit',
            'nombre',
            'tipo_persona',
            'frecuente',
            'observaciones',
        ]
        widgets = {
            'cvu_o_cbu': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': '22 dígitos (CVU o CBU)',
                'inputmode': 'numeric',
            }),
            'alias': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Ej: Cuñado Juan, Proveedor',
            }),
            'cuit': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': '11 dígitos',
                'inputmode': 'numeric',
            }),
            'nombre': forms.TextInput(attrs={
                **formclasstext,
                'placeholder': 'Nombre del titular',
            }),
            'observaciones': forms.Textarea(attrs={
                **formclasstext,
                'rows': 2,
                'placeholder': 'Notas opcionales',
            }),
        }
        labels = {
            'id_socio': 'Socio',
            'cvu_o_cbu': 'CVU o CBU',
            'alias': 'Alias referencial',
            'cuit': 'CUIT del titular',
            'nombre': 'Nombre del titular',
            'tipo_persona': 'Tipo de Persona',
            'frecuente': 'Frecuente',
            'observaciones': 'Observaciones',
        }
        help_texts = {
            'cvu_o_cbu': '22 dígitos. Puede ser CVU de Agilpagos o CBU bancario.',
            'alias': 'Alias que le asignás para identificarlo (NO es el alias de Agilpagos).',
            'cuit': 'CUIT del titular principal.',
            'nombre': 'Nombre del titular principal.',
            'tipo_persona': 'FISICA o JURIDICA (opcional).',
            'frecuente': 'Si lo marcás, se destaca en la lista.',
            'observaciones': 'Notas sobre el destinatario.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Label del socio
        self.fields['id_socio'].label_from_instance = lambda o: (
            f"{o.id_socio_mutual} - {o.nombre_completo} (CUIT: {o.cuit or '-'})"
        )

    # ============================================
    # Validaciones
    # ============================================
    def clean_cvu_o_cbu(self):
        cvu = self.cleaned_data.get('cvu_o_cbu')
        if cvu:
            cvu = re.sub(r'\D', '', str(cvu))
            if len(cvu) != 22:
                raise ValidationError('El CVU/CBU debe tener exactamente 22 dígitos.')
        return cvu

    def clean_cuit(self):
        cuit = self.cleaned_data.get('cuit')
        if cuit:
            cuit = re.sub(r'\D', '', str(cuit))
            if len(cuit) != 11:
                raise ValidationError('El CUIT debe tener exactamente 11 dígitos.')
        return cuit

    def clean(self):
        cleaned = super().clean()

        # Validar unicidad del par (id_socio, cvu_o_cbu)
        socio = cleaned.get('id_socio')
        cvu = cleaned.get('cvu_o_cbu')
        if socio and cvu:
            qs = AgendaDestinatario.objects.filter(
                id_socio=socio,
                cvu_o_cbu=cvu,
            )
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError({
                    'cvu_o_cbu': 'Ya existe un destinatario con ese CVU/CBU para este socio.'
                })

        return cleaned