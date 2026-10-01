import re
import requests
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
    # ---- Campo PEP como Select con opciones "Verdadero / Falso" ----
    es_pep = forms.ChoiceField(
        choices=(
            (True, 'SI'),
            (False, 'NO'),
        ),
        required=True,
        initial=False,
        label="PEP",
        widget=forms.Select(attrs={**formclassselect}),
    )
    es_uif = forms.ChoiceField(
        choices=(
            (True, 'SI'),
            (False, 'NO'),
        ),
        required=True,
        initial=False,
        label="UIF",
        widget=forms.Select(attrs={**formclassselect}),
    )
    ley_fatca = forms.ChoiceField(
        choices=(
            (True, 'SI'),
            (False, 'NO'),
        ),
        required=True,
        initial=False,
        label="FATCA",
        widget=forms.Select(attrs={**formclassselect}),
    )

    def clean_cuit(self):
        cuit = self.cleaned_data.get('cuit')
        if cuit is None:
            return ''
        cuit = cuit.strip()
        if not cuit:
            return cuit

        # 1. Limpiar y validar formato
        cuit_limpio = re.sub(r'\D', '', cuit)
        if len(cuit_limpio) != 11:
            raise ValidationError('El CUIT debe tener 11 dígitos.')

        # 2. Validación LOCAL: evitar duplicados en la base de datos
        qs = CuentaMutual.objects.filter(cuit=cuit_limpio)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Este CUIT ya está registrado en otra cuenta local.')

        # 3. Validación EXTERNA: consultar existencia en Agilpagos
        try:
            url = f'http://186.189.231.237:8081/onboarding/usuario/{cuit_limpio}'
            response = requests.get(url, headers={'Accept': 'application/json'}, timeout=5)

            if response.status_code == 200:
                data = response.json()
                # Si la API devuelve un string con "No existe CVU asociado" → no existe, permitido
                if isinstance(data, str) and "No existe CVU asociado" in data:
                    return cuit_limpio
                # Si la respuesta tiene estructura de usuario → ya existe, bloqueamos
                if isinstance(data, dict) and 'usuario' in data:
                    raise ValidationError('Este CUIT ya está registrado en Agilpagos.')
                # Cualquier otra respuesta inesperada, bloqueamos por seguridad
                raise ValidationError('No se pudo validar el CUIT. Intente nuevamente.')
            elif response.status_code == 404:
                # 404 = no existe → permitido
                return cuit_limpio
            else:
                # Otros errores (500, etc.) bloqueamos
                raise ValidationError('Error al consultar el CUIT. Intente más tarde.')
        except requests.exceptions.RequestException:
            # Error de red o timeout
            raise ValidationError('No se pudo conectar al servidor de validación. Intente más tarde.')

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email is None:
            return ''
        email = email.strip()
        if not email:
            return email

        qs = CuentaMutual.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Este email ya está registrado en otra cuenta.')
        return email

    def clean_numero_telefono(self):
        telefono = self.cleaned_data.get('numero_telefono')
        if telefono is None:
            return ''
        telefono = telefono.strip()
        if not telefono:
            return telefono

        qs = CuentaMutual.objects.filter(numero_telefono=telefono)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Este número de teléfono ya está registrado en otra cuenta.')
        return telefono


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
            
            # ---- Datos Técnicos ----
            'fecha_alta': forms.TextInput(attrs={'type': 'date', **formclassdate}),
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

        # ---- NUEVO: Establecer valor por defecto para id_sucursal ----
        # Solo si es un formulario de creación (no tiene instancia o no tiene pk)
        if not self.instance or not self.instance.pk:
            try:
                # Intentar obtener la sucursal con ID = 1
                from ..models.sucursal_models import Sucursal
                sucursal_default = Sucursal.objects.filter(id_sucursal=1).first()
                if sucursal_default:
                    self.fields['id_sucursal'].initial = sucursal_default.pk
                    self.fields['id_sucursal'].empty_label = None  # Opcional: ocultar el "-- Seleccionar --"
            except Exception as e:
                # Si no existe la sucursal o hay error, simplemente no se establece
                pass

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
        doc = self.cleaned_data.get("numero_documento")
        if doc is None:
            return ''
        doc = str(doc)
        d = re.sub(r"\D+", "", doc)
        if d:
            d = d.zfill(8)
        return d

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