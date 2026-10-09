# apps/consultas/forms/consulta_cvu_forms.py
from django import forms
from django.core.exceptions import ValidationError
from diseno_base.diseno_bootstrap import formclasstext


class ConsultaCvuPorCuitForm(forms.Form):
    """Formulario para consultar CVUs por CUIT en Agilpagos."""

    cuit = forms.CharField(
        label="CUIT",
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={
            **formclasstext,
            'placeholder': 'Ej: 20207882950',
            'inputmode': 'numeric',
            'pattern': '[0-9]{11}',
        }),
        help_text="Ingresá el CUIT (11 dígitos, sin guiones).",
    )

    def clean_cuit(self):
        cuit = self.cleaned_data.get('cuit', '')
        cuit = ''.join(c for c in str(cuit) if c.isdigit())
        if len(cuit) != 11:
            raise ValidationError('El CUIT debe tener exactamente 11 dígitos.')
        return cuit