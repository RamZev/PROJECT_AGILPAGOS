# apps/maestros/models/socio_models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q

from apps.usuarios.models import User
from .base_gen_models import ModeloBaseGenerico
from .sucursal_models import Sucursal
from .sg_catalogo_models import (
    SgNacionalidad,
    SgProvincia,
    SgCondicionFiscal,
    SgEstadoCivil,
    SgOcupacion,
    SgMotivoPEP,
    SgEntidadTipoDocumento,
    SgTipoPersona,
)
from entorno.constantes_base import (
    ESTATUS_GEN, 
    SEXO_CHOICES, 
    PAIS_DOMICILIO_ARGENTINA
)


class Socio(ModeloBaseGenerico):
    """
    Espejo 1:1 del "Usuario" de Agilpagos.
    Un socio puede tener una o varias CVU (ver modelo CuentaMutual/Cvu).
    El puente con la Mutual es el par (id_sucursal, codigo_socio),
    que forma el id_socio_mutual = id_sucursal * 1_000_000 + codigo_socio.
    """

    # ============================================
    # 1. IDENTIFICADORES INTERNOS
    # ============================================
    id_socio = models.AutoField(primary_key=True)

    estado = models.BooleanField(
        "Estatus",
        default=True,
        choices=ESTATUS_GEN,
    )

    # ============================================
    # 2. RELACIONES PRINCIPALES
    # ============================================
    id_sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name='socios',
        verbose_name="Sucursal",
    )

    codigo_socio = models.IntegerField(
        "Código Socio",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(999999),
        ],
        help_text="Código de socio dentro de la sucursal (hasta 6 dígitos).",
    )

    id_socio_mutual = models.BigIntegerField(
        "ID Socio Mutual",
        unique=True,
        editable=False,
        db_index=True,
        help_text="Calculado: id_sucursal * 1.000.000 + codigo_socio.",
    )

    # Vinculación opcional con el User de Django (para autenticación)
    id_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='socio',
    )

    # ============================================
    # 3. IDENTIFICADOR EN AGILPAGOS
    # ============================================
    id_usuario_agilpagos = models.CharField(
        "ID Usuario Agilpagos",
        max_length=36,
        unique=True,
        null=True, blank=True,
        help_text="idUsuario devuelto por Agilpagos en el alta (UUID).",
    )

    # ============================================
    # 4. DATOS PERSONALES
    # ============================================
    nombre = models.CharField("Nombre", max_length=40)
    apellido = models.CharField("Apellido", max_length=40)
    razon_social = models.CharField(
        "Razón Social",
        max_length=80,
        blank=True, null=True,
        help_text="Solo para Persona Jurídica.",
    )
    genero = models.CharField(
        "Género",
        max_length=1,
        choices=SEXO_CHOICES,
        blank=True, null=True,
    )
    fecha_nacimiento = models.DateField(
        "Fecha de Nacimiento",
        blank=True, null=True,
    )

    # ============================================
    # 5. DOCUMENTO
    # ============================================
    numero_documento = models.CharField(
        "Número de Documento",
        max_length=15,
        unique=True,
        help_text="DNI, sin prefijo F/M.",
    )
    numero_tramite_documento = models.CharField(
        "Número de Trámite",
        max_length=20,
        help_text="Impreso en el DNI.",
    )
    cuit = models.BigIntegerField(
        "CUIT",
        unique=True,
    )

    # ============================================
    # 6. CONTACTO
    # ============================================
    email = models.EmailField(
        "Email",
        max_length=150,
        unique=True,
    )
    caracteristica_pais = models.CharField(
        "Característica País",
        max_length=5,
        blank=True, null=True,
        default="54",
    )
    codigo_area = models.CharField(
        "Código Área",
        max_length=10,
        blank=True, null=True,
    )
    numero_telefono = models.CharField(
        "Número de Teléfono",
        max_length=20,
        blank=True, null=True,
    )

    # ============================================
    # 7. NACIONALIDAD
    # ============================================
    id_nacionalidad = models.ForeignKey(
        SgNacionalidad,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='socios_nacionalidad',
        verbose_name="Nacionalidad",
    )
    id_pais_nacimiento = models.ForeignKey(
        SgNacionalidad,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='socios_pais_nacimiento',
        verbose_name="País de Nacimiento",
    )

    # ============================================
    # 8. SITUACIÓN FISCAL Y LEGAL
    # ============================================
    id_estado_civil = models.ForeignKey(
        SgEstadoCivil,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='socios_estado_civil',
        verbose_name="Estado Civil",
    )
    id_condicion_fiscal = models.ForeignKey(
        SgCondicionFiscal,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='socios_condicion_fiscal',
        verbose_name="Condición Fiscal",
    )
    id_ocupacion = models.ForeignKey(
        SgOcupacion,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='socios_ocupacion',
        verbose_name="Ocupación",
    )

    es_pep = models.BooleanField("PEP", default=False)
    id_motivo_pep = models.ForeignKey(
        SgMotivoPEP,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='socios_motivo_pep',
        verbose_name="Motivo PEP",
    )
    es_uif = models.BooleanField("Sujeto UIF", default=False)
    ley_fatca = models.BooleanField("Ley FATCA", default=False)

    # ============================================
    # 9. DOMICILIO
    # ============================================
    id_pais_domicilio = models.CharField(
        "País de Domicilio",
        max_length=36,
        default=PAIS_DOMICILIO_ARGENTINA,
        editable=False,
        help_text="GUID fijo de Argentina (restricción de Agilpagos).",
    )
    id_provincia = models.ForeignKey(
        SgProvincia,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='socios_provincia',
        verbose_name="Provincia",
    )
    localidad = models.CharField("Localidad", max_length=100, blank=True, null=True)
    calle = models.CharField("Calle", max_length=150, blank=True, null=True)
    altura = models.CharField("Altura", max_length=20, blank=True, null=True)
    cp = models.CharField("Código Postal", max_length=15, blank=True, null=True)
    piso = models.CharField("Piso", max_length=10, blank=True, null=True)
    departamento = models.CharField("Departamento", max_length=10, blank=True, null=True)
    observaciones_domicilio = models.CharField(
        "Observaciones Domicilio",
        max_length=255,
        blank=True, null=True,
    )

    # ============================================
    # 10. DATOS TÉCNICOS
    # ============================================
    fecha_alta_agilpagos = models.DateField(
        "Fecha Alta Agilpagos",
        blank=True, null=True,
    )

    # Catálogos SG auxiliares
    id_entidad_tipo_documento = models.ForeignKey(
        SgEntidadTipoDocumento,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='socios_entidad_tipo_documento',
        verbose_name="Entidad Tipo Documento",
    )
    id_tipo_persona = models.ForeignKey(
        SgTipoPersona,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='socios_tipo_persona',
        verbose_name="Tipo de Persona",
    )

    # ============================================
    # 11. MÉTODOS
    # ============================================
    def compute_id_socio_mutual(self):
        """Calcula id_socio_mutual = id_sucursal * 1_000_000 + codigo_socio."""
        if self.id_sucursal_id and self.codigo_socio is not None:
            return self.id_sucursal_id * 1_000_000 + int(self.codigo_socio)
        return self.id_socio_mutual

    def clean(self):
        super().clean()
        errors = {}

        # Validar rango de codigo_socio
        if self.codigo_socio is not None and not (0 <= self.codigo_socio <= 999999):
            errors['codigo_socio'] = 'Debe estar entre 0 y 999999.'

        # Validar rango de id_sucursal (por si alguien cambia el catálogo)
        if self.id_sucursal_id and not (1 <= self.id_sucursal_id <= 99):
            errors['id_sucursal'] = 'La sucursal debe estar entre 1 y 99.'

        # Validar unicidad del par (id_sucursal, codigo_socio)
        if self.id_sucursal_id and self.codigo_socio is not None:
            qs = Socio.objects.filter(
                id_sucursal_id=self.id_sucursal_id,
                codigo_socio=self.codigo_socio,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                errors['codigo_socio'] = (
                    'Ya existe un socio con ese código en esa sucursal.'
                )

        # Validar PEP
        if self.es_pep and not self.id_motivo_pep:
            errors['id_motivo_pep'] = (
                'Es obligatorio cuando es Persona Expuesta Políticamente (PEP).'
            )

        # Validar país de domicilio (restricción Agilpagos)
        if self.id_pais_domicilio != PAIS_DOMICILIO_ARGENTINA:
            errors['id_pais_domicilio'] = (
                'La API de Agilpagos solo admite Argentina como país de domicilio.'
            )

        # Bloquear id_usuario_agilpagos una vez asignado
        if self.pk and not self._state.adding:
            try:
                original = type(self).objects.get(pk=self.pk)
            except type(self).DoesNotExist:
                pass
            else:
                if original.id_usuario_agilpagos and (
                    self.id_usuario_agilpagos != original.id_usuario_agilpagos
                ):
                    errors['id_usuario_agilpagos'] = (
                        'Este campo no puede modificarse una vez asignado.'
                    )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Calcular siempre id_socio_mutual del lado del servidor
        self.id_socio_mutual = self.compute_id_socio_mutual()
        super().save(*args, **kwargs)

    # ============================================
    # 12. PROPIEDADES
    # ============================================
    @property
    def nombre_completo(self):
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.razon_social or ""

    @property
    def telefono_completo(self):
        if all([self.caracteristica_pais, self.codigo_area, self.numero_telefono]):
            return f"{self.caracteristica_pais}{self.codigo_area}{self.numero_telefono}"
        return ""

    @property
    def es_persona_fisica(self):
        if self.id_tipo_persona:
            return str(self.id_tipo_persona.id_sg_tipo_persona).upper() == (
                '20EB917-7CA8-49E0-9E0B-CA8293218ACA'
            )
        return False

    @property
    def es_persona_juridica(self):
        return not self.es_persona_fisica

    # ============================================
    # 13. PAYLOAD A AGILPAGOS
    # ============================================
    def to_agilpagos_payload_usuario(self):
        """
        Construye el payload JSON para crear el USUARIO en Agilpagos
        (POST /Onboarding/Usuario).
        """
        def _pk(field):
            return getattr(field, 'pk', None) if field else None

        caracteristica = self.caracteristica_pais or "54"
        if not caracteristica.startswith("+"):
            caracteristica = f"+{caracteristica}"

        payload = {
            # Datos personales
            "nombre": self.nombre or "",
            "apellido": self.apellido or "",
            "genero": self.genero or "",
            "fechaNacimiento": self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,

            # Nacionalidad
            "idNacionalidad": _pk(self.id_nacionalidad) or "",
            "idPaisNacimiento": _pk(self.id_pais_nacimiento) or "",

            # Documento
            "idTipoDocumento": _pk(self.id_entidad_tipo_documento) or "",
            "numeroDocumento": self.numero_documento or "",
            "numeroTramiteDocumento": self.numero_tramite_documento or "",
            "cuit": str(self.cuit) if self.cuit else "",

            # Contacto
            "email": self.email or "",
            "caracteristicaPais": caracteristica,
            "codigoArea": self.codigo_area or "",
            "numeroTelefono": self.numero_telefono or "",

            # Situación fiscal y legal
            "idEstadoCivil": _pk(self.id_estado_civil) or "",
            "idCondicionFiscal": _pk(self.id_condicion_fiscal) or "",
            "idOcupacion": _pk(self.id_ocupacion) or "",
            "esPep": self.es_pep or False,
            "idMotivoPep": _pk(self.id_motivo_pep) if self.es_pep else None,
            "esUIF": self.es_uif or False,
            "leyFATCA": self.ley_fatca or False,

            # Domicilio
            "idPaisDomicilio": self.id_pais_domicilio or PAIS_DOMICILIO_ARGENTINA,
            "idProvincia": _pk(self.id_provincia) or "",
            "localidad": self.localidad or "",
            "calle": self.calle or "",
            "altura": self.altura or "",
            "cp": self.cp or "",
            "piso": self.piso or "",
            "departamento": self.departamento or "",
            "observaciones": self.observaciones_domicilio or "",

            # Catálogos SG
            "idEntidadTipoDocumento": _pk(self.id_entidad_tipo_documento) or "",
            "idTipoPersona": _pk(self.id_tipo_persona) or "",
        }

        return {k: v for k, v in payload.items() if v is not None}

    # ============================================
    # 14. META
    # ============================================
    class Meta:
        db_table = 'socio'
        verbose_name = 'Socio'
        verbose_name_plural = 'Socios'
        ordering = ['id_socio_mutual']
        constraints = [
            # Un socio solo puede tener un código por sucursal
            models.UniqueConstraint(
                fields=['id_sucursal', 'codigo_socio'],
                name='uq_socio_sucursal_codigo',
            ),
        ]

    def __str__(self):
        return f"{self.id_socio_mutual} - {self.nombre_completo or 'Sin nombre'}"