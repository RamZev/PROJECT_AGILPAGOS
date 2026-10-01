# apps/maestros/models/cuenta_cvu_models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from .base_gen_models import ModeloBaseGenerico
from .socio_models import Socio
from .sg_catalogo_models import SgTipoCuentaMutual


# ============================================
# CHOICES: Estado de la CVU
# Valores documentados por Agilpagos.
# ============================================
ESTADO_CVU_CHOICES = (
    ('Activo', 'Activo'),
    ('Inactivo', 'Inactivo'),
    ('Cerrado', 'Cerrado'),
    ('Inactivo por usuario', 'Inactivo por usuario'),
)


class CuentaCvu(ModeloBaseGenerico):
    """
    Representa una CVU (Clave Virtual Uniforme) dada de alta en Agilpagos.
    Un socio puede tener varias CVU, una por tipo de caja
    (Común / Especial / Diferencial), según SgTipoCuentaMutual.
    """

    # ============================================
    # 1. IDENTIFICADORES INTERNOS
    # ============================================
    id_cvu = models.AutoField(
        primary_key=True,
        verbose_name="ID CVU",
    )

    # ============================================
    # 2. RELACIONES PRINCIPALES
    # ============================================
    id_socio = models.ForeignKey(
        Socio,
        on_delete=models.PROTECT,
        related_name='cuentas_cvu',
        verbose_name="Socio",
    )

    id_tipo_cuenta_mutual = models.ForeignKey(
        SgTipoCuentaMutual,
        on_delete=models.PROTECT,
        related_name='cuentas_cvu',
        verbose_name="Tipo de Cuenta Mutual",
        help_text="Distingue si esta CVU corresponde a la caja C, E o D del socio.",
    )

    # ============================================
    # 3. DATOS DE LA CVU
    # ============================================
    numero_cuenta_entidad = models.CharField(
        "Número de Cuenta Entidad",
        max_length=30,
        unique=True,
        blank=True,
        help_text=(
            "Definido por la Mutual. Convención: id_socio_mutual + letra de tipo "
            "de cuenta. Se autogenera si no se especifica."
        ),
    )

    cvu = models.CharField(
        "CVU",
        max_length=22,
        unique=True,
        help_text="Clave Virtual Uniforme (22 dígitos).",
    )

    alias = models.CharField(
        "Alias",
        max_length=20,
        unique=True,
        blank=True, null=True,
        help_text="Alias del CVU (máx. 20 caracteres).",
    )

    # ============================================
    # 4. IDENTIFICADORES DE AGILPAGOS
    # ============================================
    id_cvu2 = models.CharField(
        "ID CVU (Agilpagos)",
        max_length=36,
        unique=True,
        blank=True, null=True,
        help_text="GUID 'id' devuelto por GET /CVU. Usado para Saldos/Movimientos.",
    )

    id_usuario_entidad_lineas_cuentas = models.CharField(
        "ID Usuario Entidad Líneas Cuentas",
        max_length=36,
        blank=True, null=True,
        help_text="GUID devuelto en el alta. Usado en algunos endpoints.",
    )

    # ============================================
    # 5. ESTADO Y FLAGS
    # ============================================
    estado_vcu = models.CharField(
        "Estado VCU",
        max_length=30,
        choices=ESTADO_CVU_CHOICES,
        default='Activo',
    )

    favorita = models.BooleanField(
        "Favorita",
        default=False,
        help_text="Cuenta por defecto del socio.",
    )

    bloqueada_compliance = models.BooleanField(
        "Bloqueada por Compliance",
        default=False,
        help_text="Ver tabla evento_novedad_cvu.",
    )

    # ============================================
    # 6. FECHAS Y BAJA
    # ============================================
    fecha_alta = models.DateField(
        "Fecha de Alta",
        blank=True, null=True,
    )
    fecha_baja = models.DateField(
        "Fecha de Baja",
        blank=True, null=True,
    )

    id_motivo_baja = models.CharField(
        "ID Motivo de Baja",
        max_length=36,
        blank=True, null=True,
        help_text="GUID del motivo de baja (catálogo pendiente de definir).",
    )
    observaciones_baja = models.CharField(
        "Observaciones de Baja",
        max_length=255,
        blank=True, null=True,
    )

    # ============================================
    # 7. CONTROL DE ACTUALIZACIÓN
    # ============================================
    alias_actualizado_at = models.DateTimeField(
        "Alias Actualizado En",
        blank=True, null=True,
        help_text="Controla la regla de 24hs entre cambios de alias.",
    )

    # ============================================
    # 8. MÉTODOS
    # ============================================
    def compute_numero_cuenta_entidad(self):
        """
        Genera numero_cuenta_entidad = id_socio_mutual + codigo_letra.
        Ejemplo: sucursal 01 + socio 373 + cuenta Común → '1000373C'.
        """
        if not self.id_socio or not self.id_tipo_cuenta_mutual:
            return self.numero_cuenta_entidad

        id_socio_mutual = self.id_socio.compute_id_socio_mutual()
        codigo_letra = self.id_tipo_cuenta_mutual.codigo_letra
        if id_socio_mutual and codigo_letra:
            return f"{id_socio_mutual}{codigo_letra}"
        return self.numero_cuenta_entidad

    def clean(self):
        super().clean()
        errors = {}

        # Validar unicidad del par (id_socio, id_tipo_cuenta_mutual)
        if self.id_socio_id and self.id_tipo_cuenta_mutual_id:
            qs = CuentaCvu.objects.filter(
                id_socio_id=self.id_socio_id,
                id_tipo_cuenta_mutual_id=self.id_tipo_cuenta_mutual_id,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                errors['id_tipo_cuenta_mutual'] = (
                    'Este socio ya tiene una CVU de este tipo de cuenta.'
                )

        # Validar longitud del CVU
        if self.cvu and len(self.cvu) != 22:
            errors['cvu'] = 'El CVU debe tener exactamente 22 caracteres.'

        # Validar longitud del alias
        if self.alias and len(self.alias) > 20:
            errors['alias'] = 'El alias no puede superar los 20 caracteres.'

        # Validar regla de 24hs entre cambios de alias
        if self.pk and not self._state.adding:
            try:
                original = type(self).objects.get(pk=self.pk)
            except type(self).DoesNotExist:
                pass
            else:
                if original.alias != self.alias and original.alias_actualizado_at:
                    delta = timezone.now() - original.alias_actualizado_at
                    if delta.total_seconds() < 24 * 3600:
                        errors['alias'] = (
                            'Debe esperar 24 horas entre cambios de alias.'
                        )

        # Bloquear edición de identificadores de Agilpagos
        if self.pk and not self._state.adding:
            try:
                original = type(self).objects.get(pk=self.pk)
            except type(self).DoesNotExist:
                pass
            else:
                locked = [
                    'id_cvu2',
                    'id_usuario_entidad_lineas_cuentas',
                    'cvu',
                ]
                for f in locked:
                    old = getattr(original, f)
                    new = getattr(self, f)
                    if old and new != old:
                        errors[f] = 'Este campo no puede modificarse una vez asignado.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Autogenerar numero_cuenta_entidad si no viene especificado
        if not self.numero_cuenta_entidad:
            self.numero_cuenta_entidad = self.compute_numero_cuenta_entidad()

        # Registrar el timestamp del último cambio de alias
        if self.pk:
            try:
                original = type(self).objects.get(pk=self.pk)
            except type(self).DoesNotExist:
                pass
            else:
                if original.alias != self.alias:
                    self.alias_actualizado_at = timezone.now()
        else:
            # En creación, si se especifica alias, registrar el timestamp
            if self.alias:
                self.alias_actualizado_at = timezone.now()

        super().save(*args, **kwargs)

    # ============================================
    # 9. PROPIEDADES
    # ============================================
    @property
    def activa(self):
        """Indica si la CVU está activa."""
        return self.estado_vcu == 'Activo' and not self.fecha_baja

    @property
    def nombre_socio(self):
        return self.id_socio.nombre_completo if self.id_socio else ""

    # ============================================
    # 10. PAYLOAD A AGILPAGOS
    # ============================================
    def to_agilpagos_payload_cvu(self):
        """
        Construye el payload para crear una CVU en Agilpagos.
        Combina datos del socio + datos de esta CVU.
        """
        socio = self.id_socio
        if not socio:
            return {}

        return {
            "idUsuario": socio.id_usuario_agilpagos or "",
            "idTipoCuenta": self.id_tipo_cuenta_mutual_id or "",
            "numeroCuentaEntidad": self.numero_cuenta_entidad or "",
            "cvu": self.cvu or "",
            "alias": self.alias or "",
        }

    # ============================================
    # 11. META
    # ============================================
    class Meta:
        db_table = 'cuenta_cvu'
        verbose_name = 'Cuenta CVU'
        verbose_name_plural = 'Cuentas CVU'
        ordering = ['id_cvu']
        constraints = [
            # Un socio no puede tener 2 CVU del mismo tipo de caja
            models.UniqueConstraint(
                fields=['id_socio', 'id_tipo_cuenta_mutual'],
                name='uq_cvu_socio_tipo_cuenta',
            ),
        ]
        indexes = [
            models.Index(fields=['id_socio'], name='ix_cvu_socio'),
            models.Index(fields=['estado_vcu'], name='ix_cvu_estado'),
            models.Index(
                fields=['id_tipo_cuenta_mutual'],
                name='ix_cvu_tipo_cuenta',
            ),
        ]

    def __str__(self):
        return f"CVU {self.cvu or '?'} - {self.nombre_socio or 'Sin socio'}"