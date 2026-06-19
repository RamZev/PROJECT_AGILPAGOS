import re
from django import forms
from django.db.models import Q
from .crud_forms_generics import CrudGenericForm
from ..models.cuenta_mutual_models import CuentaMutual
from diseno_base.diseno_bootstrap import (formclasstext, formclassselect, formclassdate)
from ..models.sg_catalogo_models import (
    SgEntidadTipoDocumento, 
    SgTipoPersona, 
    SgTipoCuenta,
    SgNacionalidad,
    SgProvincia,
    SgCondicionFiscal,
    SgEstadoCivil,
    SgOcupacion,
    SgMotivoPEP,
)
from ...usuarios.models import User
from django.core.exceptions import ValidationError


def _pk_or_val(v):
    if v is None:
        return None
    if hasattr(v, 'pk'):
        return v.pk
    return v


class CuentaMutualForm(CrudGenericForm):
    # ---- Catálogos SG (Nuevos) ----
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
    
    # ---- Nuevos campos de catálogos ----
    id_nacionalidad = forms.ModelChoiceField(
        queryset=SgNacionalidad.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )
    id_pais_nacimiento = forms.ModelChoiceField(
        queryset=SgNacionalidad.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )
    id_provincia = forms.ModelChoiceField(
        queryset=SgProvincia.objects.all().order_by('nombre_provincia'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )
    id_condicion_fiscal = forms.ModelChoiceField(
        queryset=SgCondicionFiscal.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )
    id_estado_civil = forms.ModelChoiceField(
        queryset=SgEstadoCivil.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )
    id_ocupacion = forms.ModelChoiceField(
        queryset=SgOcupacion.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )
    id_motivo_pep = forms.ModelChoiceField(
        queryset=SgMotivoPEP.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect})
    )

    class Meta:
        model = CuentaMutual
        fields = '__all__'
        widgets = {
            # ---- Campos existentes ----
            'estatus_cuenta_mutual': forms.Select(attrs={**formclassselect}),
            'id_sucursal': forms.Select(attrs={**formclassselect}),
            'id_socio': forms.TextInput(attrs={**formclasstext}),
            'cuenta': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'id_user': forms.Select(attrs={**formclassselect}),
            
            # ---- Datos Personales ----
            'nombre': forms.TextInput(attrs={**formclasstext}),
            'apellido': forms.TextInput(attrs={**formclasstext}),
            'razon_social': forms.TextInput(attrs={**formclasstext}),
            'genero': forms.Select(attrs={**formclassselect}),
            'fecha_nacimiento': forms.TextInput(attrs={'type': 'date', **formclassdate}),
            
            # ---- Documento ----
            'numero_documento': forms.TextInput(attrs={**formclasstext}),
            'numero_tramite_documento': forms.TextInput(attrs={**formclasstext}),
            'cuit': forms.TextInput(attrs={**formclasstext}),
            
            # ---- Contacto ----
            'email': forms.EmailInput(attrs={**formclasstext}),
            'caracteristica_pais_telefono': forms.TextInput(attrs={**formclasstext}),
            'codigo_area_telefono': forms.TextInput(attrs={**formclasstext}),
            'numero_telefono': forms.TextInput(attrs={**formclasstext}),
            
            # ---- Domicilio ----
            'id_pais_domicilio': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'localidad': forms.TextInput(attrs={**formclasstext}),
            'calle': forms.TextInput(attrs={**formclasstext}),
            'altura': forms.TextInput(attrs={**formclasstext}),
            'cp': forms.TextInput(attrs={**formclasstext}),
            'piso': forms.TextInput(attrs={**formclasstext}),
            'departamento': forms.TextInput(attrs={**formclasstext}),
            'observaciones_domicilio': forms.Textarea(attrs={**formclasstext, 'rows': 2}),
            
            # ---- Cumplimiento Normativo ----
            'es_pep': forms.Select(attrs={**formclassselect}),
            'es_uif': forms.Select(attrs={**formclassselect}),
            'ley_fatca': forms.Select(attrs={**formclassselect}),
            
            # ---- Datos Técnicos ----
            'fecha_alta': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'numero_cuenta_entidad': forms.TextInput(attrs={**formclasstext}),
            
            # ---- Identificadores SG (solo lectura) ----
            'id_sg_usuario': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'id_sg_cuenta': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'cvu': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'alias': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---- Usuarios NO staff sin cuenta ----
        base = User.objects.filter(is_staff=False)
        if self.instance and self.instance.pk and self.instance.id_user_id:
            self.fields['id_user'].queryset = base.filter(
                Q(cuenta__isnull=True) | Q(pk=self.instance.id_user_id)
            )
        else:
            self.fields['id_user'].queryset = base.filter(cuenta__isnull=True)

        # ---- Label para los ModelChoiceFields ----
        self.fields["id_entidad_tipo_documento"].label_from_instance = lambda o: o.nombre
        self.fields["id_tipo_persona"].label_from_instance = lambda o: o.tipo_persona
        self.fields["id_tipo_cuenta"].label_from_instance = lambda o: o.tipo_cuenta
        self.fields["id_nacionalidad"].label_from_instance = lambda o: o.descripcion
        self.fields["id_pais_nacimiento"].label_from_instance = lambda o: o.descripcion
        self.fields["id_provincia"].label_from_instance = lambda o: o.nombre_provincia
        self.fields["id_condicion_fiscal"].label_from_instance = lambda o: o.descripcion
        self.fields["id_estado_civil"].label_from_instance = lambda o: o.descripcion
        self.fields["id_ocupacion"].label_from_instance = lambda o: o.descripcion
        self.fields["id_motivo_pep"].label_from_instance = lambda o: o.descripcion

        # ---- Campo cuenta: no editable y NO requerido ----
        if 'cuenta' in self.fields:
            self.fields['cuenta'].disabled = True
            self.fields['cuenta'].required = False

        # ---- Valor inicial calculado para cuenta (UX) ----
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

        # ---- Bloqueo de campos SG una vez cargados ----
        locked = ['id_sg_usuario', 'id_sg_cuenta', 'cvu', 'alias']
        if self.instance and self.instance.pk:
            for f in locked:
                if getattr(self.instance, f):
                    self.fields[f].widget.attrs['readonly'] = True
                    self.fields[f].disabled = True

        # ---- Valor fijo para país de domicilio (Argentina) ----
        if 'id_pais_domicilio' in self.fields:
            self.fields['id_pais_domicilio'].initial = '76B19E61-B8DC-40F4-BFAB-422CBFFE5002'

    def clean(self):
        cleaned = super().clean()

        # ---- Tomar pk si vienen como instancias ----
        def _pk(v): return getattr(v, 'pk', v)

        suc = _pk(cleaned.get('id_sucursal'))
        soc = _pk(cleaned.get('id_socio'))
        if not suc or not soc:
            raise ValidationError('Debe seleccionar Sucursal y Socio para calcular la cuenta.')

        cleaned['cuenta'] = int(suc) * 1_000_000 + int(soc)

        # ---- Validar PEP: si es PEP, debe tener motivo ----
        if cleaned.get('es_pep') and not cleaned.get('id_motivo_pep'):
            raise ValidationError({
                'id_motivo_pep': 'Es obligatorio cuando es Persona Expuesta Políticamente (PEP)'
            })

        # ---- Validar Persona Física: debe tener nombre y apellido ----
        tipo_persona = cleaned.get('id_tipo_persona')
        if tipo_persona:
            # GUID de Persona Física: 20EB917-7CA8-49E0-9E0B-CA8293218ACA
            if str(tipo_persona.id_sg_tipo_persona).upper() == '20EB917-7CA8-49E0-9E0B-CA8293218ACA':
                if not cleaned.get('nombre') or not cleaned.get('apellido'):
                    raise ValidationError({
                        'nombre': 'Nombre y apellido son obligatorios para Persona Física',
                        'apellido': 'Nombre y apellido son obligatorios para Persona Física'
                    })

        # ---- Forzar originales de SG si ya existían ----
        if self.instance and self.instance.pk:
            for f in ['id_sg_usuario', 'id_sg_cuenta', 'cvu', 'alias']:
                if getattr(self.instance, f):
                    cleaned[f] = getattr(self.instance, f)

        return cleaned

    def clean_numero_documento(self):
        doc = self.cleaned_data.get("numero_documento", "")
        d = re.sub(r"\D+", "", str(doc or ""))
        if d:
            d = d.zfill(8)
        return d

    def clean_cuit(self):
        cuit = self.cleaned_data.get("cuit", "")
        c = re.sub(r"\D+", "", str(cuit or ""))
        return c

    def save(self, commit=True):
        """Asegura que cuenta quede seteado antes de persistir."""
        obj = super().save(commit=False)

        suc = getattr(obj, 'id_sucursal_id', None) or getattr(obj.id_sucursal, 'pk', None)
        soc = obj.id_socio if isinstance(obj.id_socio, int) else getattr(obj.id_socio, 'pk', None)
        if suc and soc:
            obj.cuenta = int(suc) * 1_000_000 + int(soc)

        if commit:
            obj.save()
        return obj