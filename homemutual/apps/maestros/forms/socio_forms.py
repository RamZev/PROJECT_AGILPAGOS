# apps/maestros/forms/socio_forms.py
import re
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from .crud_forms_generics import CrudGenericForm
from ..models.socio_models import Socio
from ..models.sucursal_models import Sucursal
from ..models.sg_catalogo_models import (
    SgEntidadTipoDocumento,
    SgTipoPersona,
    SgNacionalidad,
    SgProvincia,
    SgCondicionFiscal,
    SgEstadoCivil,
    SgOcupacion,
    SgMotivoPEP,
)
from apps.usuarios.models import User
from diseno_base.diseno_bootstrap import (
    formclasstext, formclassselect, formclassdate,
)


GUID_TIPO_PERSONA_FISICA = '20EB9127-7CA8-49E0-9E0B-CA8293218ACA'  # ✅ CORREGIDO
GUID_PAIS_ARGENTINA = '76b19e61-b8dc-40f4-bfab-422cbffe5002'


class SocioForm(CrudGenericForm):

    # ---- Catálogos SG ----
    id_entidad_tipo_documento = forms.ModelChoiceField(
        queryset=SgEntidadTipoDocumento.objects.all().order_by('nombre'),
        required=False, 
        empty_label="-- Seleccionar --",
        label="Tipo Documento",
        widget=forms.Select(attrs={**formclassselect}),
    )
    id_tipo_persona = forms.ModelChoiceField(
        queryset=SgTipoPersona.objects.all().order_by('tipo_persona'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect}),
    )
    id_nacionalidad = forms.ModelChoiceField(
        queryset=SgNacionalidad.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect}),
    )
    id_pais_nacimiento = forms.ModelChoiceField(
        queryset=SgNacionalidad.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect}),
    )
    id_provincia = forms.ModelChoiceField(
        queryset=SgProvincia.objects.all().order_by('nombre_provincia'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect}),
    )
    id_condicion_fiscal = forms.ModelChoiceField(
        queryset=SgCondicionFiscal.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect}),
    )
    id_estado_civil = forms.ModelChoiceField(
        queryset=SgEstadoCivil.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect}),
    )
    id_ocupacion = forms.ModelChoiceField(
        queryset=SgOcupacion.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect}),
    )
    id_motivo_pep = forms.ModelChoiceField(
        queryset=SgMotivoPEP.objects.all().order_by('descripcion'),
        required=False, empty_label="-- Seleccionar --",
        widget=forms.Select(attrs={**formclassselect}),
    )

    # ---- Booleanos como Select SI/NO ----
    es_pep = forms.ChoiceField(
        choices=((True, 'SI'), (False, 'NO')),
        required=True, initial=False, label="PEP",
        widget=forms.Select(attrs={**formclassselect}),
    )
    es_uif = forms.ChoiceField(
        choices=((True, 'SI'), (False, 'NO')),
        required=True, initial=False, label="UIF",
        widget=forms.Select(attrs={**formclassselect}),
    )
    ley_fatca = forms.ChoiceField(
        choices=((True, 'SI'), (False, 'NO')),
        required=True, initial=False, label="FATCA",
        widget=forms.Select(attrs={**formclassselect}),
    )
    estado = forms.ChoiceField(
        choices=((True, 'Activo'), (False, 'Inactivo')),
        required=True, initial=True, label="Estatus",
        widget=forms.Select(attrs={**formclassselect}),
    )

    class Meta:
        model = Socio
        fields = '__all__'   # ← Django excluye id_socio_mutual por editable=False
        widgets = {
            'id_sucursal': forms.Select(attrs={**formclassselect}),
            'codigo_socio': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'id_socio_mutual': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'id_user': forms.Select(attrs={**formclassselect}),
            'id_usuario_agilpagos': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'estado': forms.Select(attrs={**formclassselect}),

            'nombre': forms.TextInput(attrs={**formclasstext}),
            'apellido': forms.TextInput(attrs={**formclasstext}),
            'razon_social': forms.TextInput(attrs={**formclasstext}),
            'genero': forms.Select(attrs={**formclassselect}),
            'fecha_nacimiento': forms.TextInput(attrs={'type': 'date', **formclassdate}),

            'numero_documento': forms.TextInput(attrs={**formclasstext}),
            'numero_tramite_documento': forms.TextInput(attrs={**formclasstext}),
            'cuit': forms.TextInput(attrs={**formclasstext}),

            'email': forms.EmailInput(attrs={**formclasstext}),
            'caracteristica_pais': forms.TextInput(attrs={**formclasstext}),
            'codigo_area': forms.TextInput(attrs={**formclasstext}),
            'numero_telefono': forms.TextInput(attrs={**formclasstext}),

            'id_pais_domicilio': forms.TextInput(attrs={**formclasstext, 'readonly': True}),
            'localidad': forms.TextInput(attrs={**formclasstext}),
            'calle': forms.TextInput(attrs={**formclasstext}),
            'altura': forms.TextInput(attrs={**formclasstext}),
            'cp': forms.TextInput(attrs={**formclasstext}),
            'piso': forms.TextInput(attrs={**formclasstext}),
            'departamento': forms.TextInput(attrs={**formclasstext}),
            'observaciones_domicilio': forms.Textarea(attrs={**formclasstext, 'rows': 2}),

            'fecha_alta_agilpagos': forms.TextInput(attrs={'type': 'date', **formclassdate}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Usuarios sin socio
        base_user = User.objects.filter(is_staff=False)
        if self.instance and self.instance.pk and self.instance.id_user_id:
            self.fields['id_user'].queryset = base_user.filter(
                Q(socio__isnull=True) | Q(pk=self.instance.id_user_id)
            )
        else:
            self.fields['id_user'].queryset = base_user.filter(socio__isnull=True)

        # Sucursal por defecto
        if not self.instance or not self.instance.pk:
            suc = Sucursal.objects.filter(id_sucursal=1).first()
            if suc:
                self.fields['id_sucursal'].initial = suc.pk

        # País de domicilio fijo
        if 'id_pais_domicilio' in self.fields:
            self.fields['id_pais_domicilio'].initial = GUID_PAIS_ARGENTINA

        # id_usuario_agilpagos readonly si ya está asignado
        if self.instance and self.instance.pk and self.instance.id_usuario_agilpagos:
            self.fields['id_usuario_agilpagos'].disabled = True

        # Labels
        self.fields['id_entidad_tipo_documento'].label_from_instance = lambda o: o.nombre
        self.fields['id_tipo_persona'].label_from_instance = lambda o: o.tipo_persona
        self.fields['id_nacionalidad'].label_from_instance = lambda o: o.descripcion
        self.fields['id_pais_nacimiento'].label_from_instance = lambda o: o.descripcion
        self.fields['id_provincia'].label_from_instance = lambda o: o.nombre_provincia
        self.fields['id_condicion_fiscal'].label_from_instance = lambda o: o.descripcion
        self.fields['id_estado_civil'].label_from_instance = lambda o: o.descripcion
        self.fields['id_ocupacion'].label_from_instance = lambda o: o.descripcion
        self.fields['id_motivo_pep'].label_from_instance = lambda o: o.descripcion

    # ============================================
    # Validaciones
    # ============================================
    def clean_cuit(self):
        cuit = self.cleaned_data.get('cuit')
        if cuit is None:
            return None
        cuit_str = re.sub(r'\D', '', str(cuit))
        if len(cuit_str) != 11:
            raise ValidationError('El CUIT debe tener 11 dígitos.')
        cuit_int = int(cuit_str)
        qs = Socio.objects.filter(cuit=cuit_int)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Este CUIT ya está registrado en otro socio.')
        return cuit_int

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
        email = email.strip().lower()
        qs = Socio.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Este email ya está registrado en otro socio.')
        return email

    def clean_numero_documento(self):
        doc = self.cleaned_data.get('numero_documento')
        if not doc:
            return doc
        doc = re.sub(r'\D', '', str(doc)).zfill(8)
        qs = Socio.objects.filter(numero_documento=doc)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Este número de documento ya está registrado en otro socio.')
        return doc

    def clean(self):
        cleaned = super().clean()

        # if cleaned.get('es_pep') and not cleaned.get('id_motivo_pep'):
        if str(cleaned.get('es_pep')).lower() == 'true' and not cleaned.get('id_motivo_pep'):
            raise ValidationError({
                'id_motivo_pep': 'Es obligatorio cuando es PEP.'
            })

        tipo_persona = cleaned.get('id_tipo_persona')
        if tipo_persona:
            if str(tipo_persona.id_sg_tipo_persona).upper() == GUID_TIPO_PERSONA_FISICA.upper():
                if not cleaned.get('nombre') or not cleaned.get('apellido'):
                    raise ValidationError({
                        'nombre': 'Nombre y apellido son obligatorios para Persona Física.',
                        'apellido': 'Nombre y apellido son obligatorios para Persona Física.',
                    })

        if self.instance and self.instance.pk:
            if self.instance.id_usuario_agilpagos:
                cleaned['id_usuario_agilpagos'] = self.instance.id_usuario_agilpagos

        return cleaned