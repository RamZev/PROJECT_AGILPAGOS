import re
from django import forms
from django.db.models import Q
from .crud_forms_generics import CrudGenericForm
from ..models.cuenta_mutual_models import CuentaMutual
from diseno_base.diseno_bootstrap import (formclasstext, formclassselect, formclassdate)
from ..models.sg_catalogo_models import (SgEntidadTipoDocumento, SgTipoPersona, SgTipoCuenta)
from ...usuarios.models import User
from django.core.exceptions import ValidationError


def _pk_or_val(v):
    # v puede ser instancia de modelo, número o string numérica
    if v is None:
        return None
    # Si es instancia de modelo, tomar pk (funciona aunque la PK no se llame "id")
    if hasattr(v, 'pk'):
        return v.pk
    return v

class CuentaMutualForm(CrudGenericForm):
    id_entidad_tipo_documento = forms.ModelChoiceField(
        queryset=SgEntidadTipoDocumento.objects.all().order_by('nombre'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )
    id_tipo_persona = forms.ModelChoiceField(
        queryset=SgTipoPersona.objects.all().order_by('tipo_persona'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )
    id_tipo_cuenta = forms.ModelChoiceField(
        queryset=SgTipoCuenta.objects.all().order_by('tipo_cuenta'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )

    class Meta:
        model = CuentaMutual
        fields = '__all__'
        widgets = {
            'estatus_cuenta_mutual': forms.Select(attrs={**formclassselect}),
            'id_sucursal': forms.Select(attrs={**formclassselect}),
            'id_socio': forms.TextInput(attrs={**formclasstext}),
            'cuenta': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'documento': forms.TextInput(attrs={**formclasstext}),
            'cvu': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'alias': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'id_user': forms.Select(attrs={**formclassselect}),
            'razon_social': forms.TextInput(attrs={**formclasstext}),
            'cuit': forms.TextInput(attrs={**formclasstext}),
            'sexo': forms.Select(attrs={**formclassselect}),
            'fecha_nacimiento': forms.TextInput(attrs={'type':'date', **formclassdate}),
            'caracteristica_pais_telefono': forms.TextInput(attrs={**formclasstext}),
            'codigo_area_telefono': forms.TextInput(attrs={**formclasstext}),
            'numero_telefono': forms.TextInput(attrs={**formclasstext}),
            'id_sg_usuario': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'id_sg_cuenta': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Usuarios NO staff sin cuenta; en edición, permitir el propio usuario ya vinculado
        base = User.objects.filter(is_staff=False)
        if self.instance and self.instance.pk and self.instance.id_user_id:
            self.fields['id_user'].queryset = base.filter(
                Q(cuenta__isnull=True) | Q(pk=self.instance.id_user_id)
            )
        else:
            self.fields['id_user'].queryset = base.filter(cuenta__isnull=True)

        self.fields["id_entidad_tipo_documento"].label_from_instance = lambda o: o.nombre
        self.fields["id_tipo_persona"].label_from_instance           = lambda o: o.tipo_persona
        self.fields["id_tipo_cuenta"].label_from_instance            = lambda o: o.tipo_cuenta

        # cuenta visible, no editable y NO requerida (porque no viaja en el POST)
        if 'cuenta' in self.fields:
            self.fields['cuenta'].disabled = True
            self.fields['cuenta'].required = False 

        # mostrar valor inicial calculado (solo para UX)
        if self.instance and self.instance.pk:
            self.fields['cuenta'].initial = self.instance.compute_cuenta()
        else:
            data = self.data or self.initial
            try:
                suc = int((getattr(self.instance, 'id_sucursal_id', None) or data.get('id_sucursal') or 0))
                soc = int((getattr(self.instance, 'id_socio', None) or data.get('id_socio') or 0))
                if suc and soc:
                    self.fields['cuenta'].initial = suc * 1_000_000 + soc
            except Exception:
                pass

        # Bloqueo “una vez cargados” (UI)
        locked = ['id_sg_usuario', 'id_sg_cuenta', 'cvu', 'alias']
        if self.instance and self.instance.pk:
            for f in locked:
                if getattr(self.instance, f):
                    self.fields[f].widget.attrs['readonly'] = True
                    # Opcional: deshabilitar el campo para que ni se edite en el browser
                    self.fields[f].disabled = True

    def clean(self):
        cleaned = super().clean()

        # Tomar pk si vienen como instancias
        def _pk(v): return getattr(v, 'pk', v)

        suc = _pk(cleaned.get('id_sucursal'))
        soc = _pk(cleaned.get('id_socio'))
        if not suc or not soc:
            # si querés que sean obligatorios para calcular
            from django.core.exceptions import ValidationError
            raise ValidationError('Debe seleccionar Sucursal y Socio para calcular la cuenta.')

        cleaned['cuenta'] = int(suc) * 1_000_000 + int(soc)

        # Forzar originales de SG si ya existían
        if self.instance and self.instance.pk:
            for f in ['id_sg_usuario','id_sg_cuenta','cvu','alias']:
                if getattr(self.instance, f):
                    cleaned[f] = getattr(self.instance, f)

        return cleaned

    
    def clean_documento(self):
        doc = self.cleaned_data.get("documento", "")
        d = re.sub(r"\D+", "", str(doc or ""))
        if d:
            d = d.zfill(8)  # lo mismo que exige SG
        return d
    
    def save(self, commit=True):
        """Asegura que cuenta quede seteado antes de persistir (útil si otra lógica lo usa)."""
        obj = super().save(commit=False)

        suc = getattr(obj, 'id_sucursal_id', None) or getattr(obj.id_sucursal, 'pk', None)
        soc = obj.id_socio if isinstance(obj.id_socio, int) else getattr(obj.id_socio, 'pk', None)
        if suc and soc:
            obj.cuenta = int(suc) * 1_000_000 + int(soc)

        if commit:
            obj.save()
        return obj