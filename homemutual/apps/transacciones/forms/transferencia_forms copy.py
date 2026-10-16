# apps/transacciones/forms/transferencia_forms.py
import re
from django import forms
from django.core.exceptions import ValidationError

from apps.maestros.forms.crud_forms_generics import CrudGenericForm
from apps.maestros.models.cuenta_cvu_models import CuentaCvu
from apps.maestros.models.sg_catalogo_models import SgConceptoTransaccion

from ..models.transacciones_models import CashoutRequest
from diseno_base.diseno_bootstrap import formclasstext, formclassselect


class TransferenciaForm(CrudGenericForm):

    # CVU origen: input de texto
    cvu_debito = forms.CharField(
        max_length=22,
        required=True,
        label="CVU Origen",
        widget=forms.TextInput(attrs={**formclasstext, 'placeholder': '22 dígitos'}),
    )

    # Concepto: dropdown
    id_concepto = forms.ModelChoiceField(
        queryset=SgConceptoTransaccion.objects.filter(
            estatus_sg_concepto_transaccion=True
        ).order_by('codigo'),
        required=True,
        empty_label="-- Seleccionar Concepto --",
        label="Concepto",
        widget=forms.Select(attrs={**formclassselect}),
    )

    class Meta:
        model = CashoutRequest
        fields = [
            'cvu_debito',
            'cuit_credito',
            'cbu_credito',
            'nombre_credito',
            'id_concepto',
            'importe',
            'descripcion',
            'observaciones',
        ]
        widgets = {
            'cuit_credito': forms.TextInput(attrs={**formclasstext}),
            'cbu_credito': forms.TextInput(attrs={**formclasstext, 'placeholder': 'CVU/CBU del beneficiario'}),
            'nombre_credito': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'importe': forms.NumberInput(attrs={**formclasstext, 'step': '0.01', 'min': '0.01'}),
            'descripcion': forms.TextInput(attrs={**formclasstext}),
            'observaciones': forms.TextInput(attrs={**formclasstext}),
        }
        labels = {
            'cvu_debito': 'CVU Origen',
            'cuit_credito': 'CUIT del Beneficiario',
            'cbu_credito': 'CVU/CBU del Beneficiario',
            'nombre_credito': 'Nombre del Beneficiario',
            'id_concepto': 'Concepto',
            'importe': 'Importe',
            'descripcion': 'Descripción',
            'observaciones': 'Observaciones',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Label del concepto
        self.fields['id_concepto'].label_from_instance = lambda o: f"{o.codigo} - {o.descripcion}"

        # En edición, no permitir cambiar el CVU origen
        if self.instance and self.instance.pk:
            self.fields['cvu_debito'].disabled = True
            self.fields['cuit_credito'].disabled = True
            self.fields['cbu_credito'].disabled = True

        # Si ya hay un CVU cargado (edición), mostrarlo
        if self.instance and self.instance.pk and self.instance.cvu_debito:
            self.fields['cvu_debito'].initial = self.instance.cvu_debito

    # ============================================
    # Validaciones mínimas
    # ============================================
    def clean_cvu_debito(self):
        cvu = self.cleaned_data.get('cvu_debito')
        if cvu:
            cvu = re.sub(r'\D', '', str(cvu))
            if len(cvu) != 22:
                raise ValidationError('El CVU debe tener 22 dígitos.')
        return cvu

    def clean_importe(self):
        importe = self.cleaned_data.get('importe')
        if importe is None or importe <= 0:
            raise ValidationError('El importe debe ser mayor a 0.')
        return importe

    def clean_cbu_credito(self):
        cbu = self.cleaned_data.get('cbu_credito')
        if cbu:
            cbu = re.sub(r'\D', '', str(cbu))
            if len(cbu) != 22:
                raise ValidationError('El CVU/CBU debe tener 22 dígitos.')
        return cbu

    def clean_cuit_credito(self):
        cuit = self.cleaned_data.get('cuit_credito')
        if cuit is not None:
            cuit_str = re.sub(r'\D', '', str(cuit))
            if len(cuit_str) != 11:
                raise ValidationError('El CUIT debe tener 11 dígitos.')
            return int(cuit_str)
        return cuit

    def save(self, commit=True):
        obj = super().save(commit=False)

        # Completar numero_cuenta_entidad desde la CuentaCvu si existe
        if obj.cvu_debito:
            cvu_obj = CuentaCvu.objects.filter(cvu=obj.cvu_debito).first()
            if cvu_obj:
                obj.numero_cuenta_entidad = cvu_obj.numero_cuenta_entidad or ''

        if commit:
            obj.save()
        return obj