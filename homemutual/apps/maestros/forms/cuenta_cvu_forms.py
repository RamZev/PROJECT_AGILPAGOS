# apps/maestros/forms/cuenta_cvu_forms.py
from django import forms
from django.core.exceptions import ValidationError

from .crud_forms_generics import CrudGenericForm
from ..models.cuenta_cvu_models import CuentaCvu
from ..models.socio_models import Socio
from ..models.sg_catalogo_models import SgTipoCuentaMutual
from diseno_base.diseno_bootstrap import (
    formclasstext, formclassselect, formclassdate,
)


class CuentaCvuForm(CrudGenericForm):

    # ---- Catálogo ----
    id_tipo_cuenta_mutual = forms.ModelChoiceField(
        queryset=SgTipoCuentaMutual.objects.all().order_by('descripcion'),
        required=True,
        empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect}),
    )

    # ---- Estado ----
    estado_vcu = forms.ChoiceField(
        choices=(
            ('Activo', 'Activo'),
            ('Inactivo', 'Inactivo'),
            ('Cerrado', 'Cerrado'),
            ('Inactivo por usuario', 'Inactivo por usuario'),
        ),
        required=True,
        initial='Activo',
        widget=forms.Select(attrs={**formclassselect}),
    )

    # ---- Booleanos como Select ----
    favorita = forms.ChoiceField(
        choices=((True, 'SI'), (False, 'NO')),
        required=True, initial=False, label="Favorita",
        widget=forms.Select(attrs={**formclassselect}),
    )
    bloqueada_compliance = forms.ChoiceField(
        choices=((True, 'SI'), (False, 'NO')),
        required=True, initial=False, label="Bloqueada Compliance",
        widget=forms.Select(attrs={**formclassselect}),
    )

    class Meta:
        model = CuentaCvu
        fields = '__all__'
        widgets = {
            'id_socio': forms.Select(attrs={**formclassselect}),
            'numero_cuenta_entidad': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'cvu': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'alias': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'id_cvu': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'id_usuario_entidad_lineas_cuentas': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'fecha_alta': forms.TextInput(attrs={'type': 'date', **formclassdate}),
            'fecha_baja': forms.TextInput(attrs={'type': 'date', **formclassdate}),
            'id_motivo_baja': forms.TextInput(attrs={**formclasstext}),
            'observaciones_baja': forms.Textarea(attrs={**formclasstext, 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---- Socios activos ----
        base = Socio.objects.filter(estado=True).order_by('id_socio_mutual')
        self.fields['id_socio'].queryset = base

        # ---- Labels ----
        self.fields['id_socio'].label_from_instance = lambda o: (
            f"{o.id_socio_mutual} - {o.nombre_completo} (CUIT: {o.cuit or '-'})"
        )
        self.fields['id_tipo_cuenta_mutual'].label_from_instance = lambda o: (
            f"{o.codigo_letra} - {o.descripcion}"
        )

        # ---- numero_cuenta_entidad: readonly ----
        self.fields['numero_cuenta_entidad'].required = False
        self.fields['numero_cuenta_entidad'].disabled = True
        
        # ---- cvu y alias: readonly / disabled ----
        for field_name in ['cvu', 'alias']:
            self.fields[field_name].required = False
            self.fields[field_name].disabled = True

        if self.instance and self.instance.pk:
            self.fields['numero_cuenta_entidad'].initial = self.instance.numero_cuenta_entidad

        # ---- Bloquear GUIDs de Agilpagos si ya están asignados ----
        if self.instance and self.instance.pk:
            for f in ['id_cvu', 'id_usuario_entidad_lineas_cuentas', 'cvu']:
                if getattr(self.instance, f):
                    self.fields[f].widget.attrs['readonly'] = True
                    self.fields[f].disabled = True

    # ============================================
    # Validaciones
    # ============================================
    def clean_cvu(self):
        cvu = self.cleaned_data.get('cvu')
        if cvu:
            cvu = cvu.strip()
            if len(cvu) != 22:
                raise ValidationError('El CVU debe tener exactamente 22 caracteres.')
            qs = CuentaCvu.objects.filter(cvu=cvu)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('Este CVU ya está registrado.')
        return cvu

    def clean_alias(self):
        alias = self.cleaned_data.get('alias')
        if alias:
            alias = alias.strip()
            if len(alias) > 20:
                raise ValidationError('El alias no puede superar los 20 caracteres.')
            qs = CuentaCvu.objects.filter(alias__iexact=alias)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('Este alias ya está en uso.')
        return alias

    def clean(self):
        cleaned = super().clean()

        # Validar unicidad (id_socio, id_tipo_cuenta_mutual)
        socio = cleaned.get('id_socio')
        tipo = cleaned.get('id_tipo_cuenta_mutual')
        if socio and tipo:
            qs = CuentaCvu.objects.filter(id_socio=socio, id_tipo_cuenta_mutual=tipo)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError({
                    'id_tipo_cuenta_mutual': 'Este socio ya tiene una CVU de este tipo de cuenta.',
                })

        # Forzar originales de GUIDs de Agilpagos
        if self.instance and self.instance.pk:
            for f in ['id_cvu', 'id_usuario_entidad_lineas_cuentas']:
                if getattr(self.instance, f):
                    cleaned[f] = getattr(self.instance, f)

        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)

        # Autogenerar numero_cuenta_entidad si está vacío
        if not obj.numero_cuenta_entidad:
            obj.numero_cuenta_entidad = obj.compute_numero_cuenta_entidad()

        if commit:
            obj.save()
        return obj