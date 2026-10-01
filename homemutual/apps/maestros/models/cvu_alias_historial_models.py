# apps/maestros/models/cvu_alias_historial_models.py
from django.db import models
from django.utils import timezone

from .base_gen_models import ModeloBaseGenerico
from .cuenta_cvu_models import CuentaCvu


# ============================================
# CHOICES: Origen del cambio de alias
# ============================================
ORIGEN_ALIAS_CHOICES = (
    ('MUTUAL', 'Mutual'),
    ('COELSA_AUTOMATICO', 'Coelsa (Automático)'),
)


class CvuAliasHistorial(ModeloBaseGenerico):
    """
    Historial de cambios de alias de una CVU.
    Permite auditar cambios y validar la regla de "1 cambio cada 24hs"
    sin depender solo del campo `alias_actualizado_at` de CuentaCvu.
    """

    # ============================================
    # 1. IDENTIFICADORES INTERNOS
    # ============================================
    id_cvu_alias_historial = models.AutoField(
        primary_key=True,
        verbose_name="ID CVU Alias Historial",
    )

    # ============================================
    # 2. RELACIÓN CON LA CVU
    # ============================================
    id_cvu = models.ForeignKey(
        CuentaCvu,
        on_delete=models.CASCADE,  # Si se borra la CVU, se borra su historial
        related_name='alias_historial',
        verbose_name="CVU",
    )

    # ============================================
    # 3. DATOS DEL CAMBIO
    # ============================================
    alias_anterior = models.CharField(
        "Alias Anterior",
        max_length=20,
        blank=True, null=True,
        help_text="Puede ser nulo si es el primer alias asignado.",
    )
    alias_nuevo = models.CharField(
        "Alias Nuevo",
        max_length=20,
        help_text="Alias asignado en este cambio.",
    )
    origen = models.CharField(
        "Origen",
        max_length=20,
        choices=ORIGEN_ALIAS_CHOICES,
        default='MUTUAL',
        help_text="Quién originó el cambio: la Mutual o Coelsa automáticamente.",
    )
    fecha_cambio = models.DateTimeField(
        "Fecha de Cambio",
        default=timezone.now,
        help_text="Momento en que se registró el cambio de alias.",
    )

    # ============================================
    # 4. META
    # ============================================
    class Meta:
        db_table = 'cvu_alias_historial'
        verbose_name = 'CVU Alias Historial'
        verbose_name_plural = 'CVU Alias Historiales'
        ordering = ['-fecha_cambio', '-id_cvu_alias_historial']
        indexes = [
            models.Index(fields=['id_cvu'], name='ix_cvu_alias_hist_cvu'),
            models.Index(fields=['fecha_cambio'], name='ix_cvu_alias_hist_fecha'),
        ]

    def __str__(self):
        return (
            f"CVU {self.id_cvu_id}: "
            f"{self.alias_anterior or '(vacío)'} → {self.alias_nuevo} "
            f"({self.origen})"
        )