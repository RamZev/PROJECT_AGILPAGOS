from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from apps.usuarios.models import User
from .base_gen_models import ModeloBaseGenerico
from .sucursal_models import Sucursal
from .sg_catalogo_models import (
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
from entorno.constantes_base import ESTATUS_GEN

SEXO_CHOICES = (
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('X', 'No binario'),
)


class CuentaMutual(ModeloBaseGenerico):
    # ============================================
    # 1. CAMPOS INTERNOS DE LA MUTUAL
    # ============================================
    id_cuenta_mutual = models.AutoField(primary_key=True)
    estatus_cuenta_mutual = models.BooleanField("Estatus*", default=True, choices=ESTATUS_GEN)

    # Relaciones
    id_user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='cuenta'
    )
    id_sucursal = models.ForeignKey(
        Sucursal, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name="Sucursal*"
    )

    # Identificadores internos Mutual
    id_socio = models.IntegerField("ID Socio*", null=True, blank=True)
    cuenta = models.BigIntegerField(editable=True, unique=True, db_index=True, blank=True)

    # ============================================
    # 2. DATOS DE PERSONA PARA SG (POST /Usuarios)
    # ============================================
    
    # ---- 2.1 Datos Personales Básicos ----
    nombre = models.CharField("Nombre", max_length=40, blank=True, null=True)
    apellido = models.CharField("Apellido", max_length=40, blank=True, null=True)
    razon_social = models.CharField("Razón Social", max_length=80, blank=True, null=True)  # Para PJ
    genero = models.CharField("Género", max_length=1, choices=SEXO_CHOICES, blank=True, null=True)
    fecha_nacimiento = models.DateField("Fecha Nacimiento", blank=True, null=True)

    # ---- 2.2 Documento de Identidad ----
    numero_documento = models.CharField("Número de Documento", max_length=20, blank=True, null=True)
    numero_tramite_documento = models.CharField("Número de Trámite", max_length=20, blank=True, null=True)
    cuit = models.CharField("CUIT", max_length=11, blank=True, null=True)

    # ---- 2.3 Contacto ----
    email = models.EmailField("Email", max_length=100, blank=True, null=True)
    caracteristica_pais_telefono = models.CharField(
        "Característica País", 
        max_length=2, 
        blank=True, 
        null=True, 
        default="54"
    )
    codigo_area_telefono = models.CharField("Código Área", max_length=4, blank=True, null=True)
    numero_telefono = models.CharField("Número Teléfono", max_length=10, blank=True, null=True)

    # ---- 2.4 Nacionalidad ----
    id_nacionalidad = models.ForeignKey(
        SgNacionalidad,
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Nacionalidad",
        related_name='cuentas_nacionalidad'
    )
    id_pais_nacimiento = models.ForeignKey(
        SgNacionalidad,
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="País de Nacimiento",
        related_name='cuentas_pais_nacimiento'
    )

    # ---- 2.5 Domicilio ----
    # País de domicilio: solo Argentina (GUID fijo: 76B19E61-B8DC-40F4-BFAB-422CBFFE5002)
    id_pais_domicilio = models.CharField(
        "País de Domicilio", 
        max_length=36, 
        blank=True, 
        null=True,
        default="76B19E61-B8DC-40F4-BFAB-422CBFFE5002",
        help_text="GUID de Argentina (fijo)"
    )
    id_provincia = models.ForeignKey(
        SgProvincia,
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Provincia",
        related_name='cuentas_provincia'
    )
    localidad = models.CharField("Localidad", max_length=100, blank=True, null=True)
    calle = models.CharField("Calle", max_length=100, blank=True, null=True)
    altura = models.CharField("Altura", max_length=10, blank=True, null=True)
    cp = models.CharField("Código Postal", max_length=20, blank=True, null=True)
    piso = models.CharField("Piso", max_length=5, blank=True, null=True)
    departamento = models.CharField("Departamento", max_length=10, blank=True, null=True)
    observaciones_domicilio = models.TextField("Observaciones Domicilio", blank=True, null=True)

    # ---- 2.6 Situación Fiscal y Legal ----
    id_condicion_fiscal = models.ForeignKey(
        SgCondicionFiscal,
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Condición Fiscal",
        related_name='cuentas_condicion_fiscal'
    )
    id_estado_civil = models.ForeignKey(
        SgEstadoCivil,
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Estado Civil",
        related_name='cuentas_estado_civil'
    )
    id_ocupacion = models.ForeignKey(
        SgOcupacion,
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Ocupación",
        related_name='cuentas_ocupacion'
    )

    # ---- 2.7 Cumplimiento Normativo ----
    es_pep = models.BooleanField(
        "PEP", 
        default=False, 
        help_text="Persona Expuesta Políticamente"
    )
    id_motivo_pep = models.ForeignKey(
        SgMotivoPEP,
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name="Motivo PEP",
        related_name='cuentas_motivo_pep'
    )
    es_uif = models.BooleanField(
        "Sujeto UIF", 
        default=False, 
        help_text="Sujeto Obligado ante UIF"
    )
    ley_fatca = models.BooleanField(
        "Ley FATCA", 
        default=False, 
        help_text="Sujeto a Ley FATCA"
    )

    # ---- 2.8 Datos Técnicos ----
    fecha_alta = models.DateField("Fecha de Alta", 
                                  auto_now_add=True,
                                  blank=True, null=True
    )
    numero_cuenta_entidad = models.CharField(
        "Número de Cuenta Entidad", 
        max_length=50, 
        unique=True,
        blank=True, 
        null=True,
        help_text="Identificador único asignado por la Entidad (NO reutilizable)"
    )

    # ---- 2.9 Catálogos SG ----
    id_entidad_tipo_documento = models.ForeignKey(
        SgEntidadTipoDocumento,
        to_field='id_sg_entidad_tipo_documento',
        on_delete=models.PROTECT,
        null=True, blank=True,
    )

    id_tipo_persona = models.ForeignKey(
        SgTipoPersona,
        to_field='id_sg_tipo_persona', 
        on_delete=models.PROTECT,
        null=True, blank=True,
    )

    id_tipo_cuenta = models.ForeignKey(
        SgTipoCuenta,
        to_field='id_sg_tipo_cuenta', 
        on_delete=models.PROTECT,
        null=True, blank=True,
    )

    # ---- 2.10 Identificadores SG (Respuesta) ----
    id_sg_usuario = models.CharField(
        "ID SG Usuario", 
        max_length=36, 
        unique=True, 
        blank=True, 
        null=True,
        help_text="idUsuario devuelto por Agilpagos (¡GUARDAR!)"
    )  
    id_sg_cuenta = models.CharField(
        "ID SG Cuenta", 
        max_length=36, 
        unique=True, 
        blank=True, 
        null=True,
        help_text="idUsuarioEntidadLineasCuentas devuelto por Agilpagos"
    )  
    cvu = models.CharField("CVU", max_length=22, unique=True, blank=True, null=True)
    alias = models.CharField("Alias", max_length=60, unique=True, blank=True, null=True)

    # ============================================
    # 3. MÉTODOS
    # ============================================

    def compute_cuenta(self):
        suc = self.id_sucursal_id
        socio = self.id_socio if isinstance(self.id_socio, int) else None
        if suc and socio:
            return suc * 1_000_000 + int(socio)
        return self.cuenta

    def clean(self):
        super().clean()
        
        # Validar usuario staff
        if self.id_user and self.id_user.is_staff:
            raise ValidationError({"id_user": "No se puede asignar una cuenta a un usuario staff."})

        # Validar fórmula de cuenta
        expected = self.compute_cuenta()
        if expected and self.cuenta and self.cuenta != expected:
            raise ValidationError({
                'cuenta': 'El valor no coincide con la fórmula id_sucursal*1000000 + id_socio.'
            })

        # Validar PEP: si es PEP, debe tener motivo
        if self.es_pep and not self.id_motivo_pep:
            raise ValidationError({
                'id_motivo_pep': 'Es obligatorio cuando es Persona Expuesta Políticamente (PEP)'
            })

        # Validar que si es Persona Física, tenga nombre y apellido
        if self.id_tipo_persona:
            # Asumiendo que el GUID de Persona Física es: 20EB917-7CA8-49E0-9E0B-CA8293218ACA
            if str(self.id_tipo_persona.id_sg_tipo_persona).upper() == '20EB917-7CA8-49E0-9E0B-CA8293218ACA':
                if not self.nombre or not self.apellido:
                    raise ValidationError({
                        'nombre': 'Nombre y apellido son obligatorios para Persona Física',
                        'apellido': 'Nombre y apellido son obligatorios para Persona Física'
                    })

        # Bloquear edición de campos SG una vez asignados
        if self.pk:
            original = type(self).objects.get(pk=self.pk)
            locked_fields = ['id_sg_usuario', 'id_sg_cuenta', 'cvu', 'alias']
            for f in locked_fields:
                old = getattr(original, f)
                new = getattr(self, f)
                if old and new != old:
                    raise ValidationError({f: 'Este campo no puede modificarse una vez asignado.'})

    def save(self, *args, **kwargs):
        # Asegurar el cálculo SIEMPRE del lado del servidor
        self.cuenta = self.compute_cuenta()
        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        """Retorna el nombre completo para Persona Física."""
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.razon_social or ""

    @property
    def telefono_completo(self):
        """Retorna el teléfono completo para Agilpagos."""
        if all([self.caracteristica_pais_telefono, self.codigo_area_telefono, self.numero_telefono]):
            return f"{self.caracteristica_pais_telefono}{self.codigo_area_telefono}{self.numero_telefono}"
        return ""

    @property
    def es_persona_fisica(self):
        """Indica si es Persona Física."""
        if self.id_tipo_persona:
            return str(self.id_tipo_persona.id_sg_tipo_persona).upper() == '20EB917-7CA8-49E0-9E0B-CA8293218ACA'
        return False

    @property
    def es_persona_juridica(self):
        """Indica si es Persona Jurídica."""
        return not self.es_persona_fisica

    class Meta:
        db_table = 'cuenta_mutual'
        verbose_name = 'Cuenta Mutual'
        verbose_name_plural = 'Cuentas Mutuales'
        ordering = ['id_cuenta_mutual']
        constraints = [
            models.UniqueConstraint(
                fields=['id_sg_usuario'],
                name='uniq_id_sg_usuario_not_null',
                condition=Q(id_sg_usuario__isnull=False),
            ),
            models.UniqueConstraint(
                fields=['id_sg_cuenta'],
                name='uniq_id_sg_cuenta_not_null',
                condition=Q(id_sg_cuenta__isnull=False),
            ),
            models.UniqueConstraint(
                fields=['cvu'],
                name='uniq_cvu_not_null',
                condition=Q(cvu__isnull=False),
            ),
            models.UniqueConstraint(
                fields=['email'],
                name='uniq_email_not_null',
                condition=Q(email__isnull=False),
            ),
            models.UniqueConstraint(
                fields=['numero_cuenta_entidad'],
                name='uniq_numero_cuenta_entidad_not_null',
                condition=Q(numero_cuenta_entidad__isnull=False),
            ),
        ]      

    def __str__(self):
        u = self.id_user
        return f"{self.cuenta} / {u.username if u else 'sin usuario'}"

    @property
    def usuario_nombre(self):
        u = self.id_user
        full = f"{u.first_name} {u.last_name}".strip() if u else ''
        return full or (u.username if u else '')