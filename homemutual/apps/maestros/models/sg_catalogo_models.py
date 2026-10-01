from django.db import models
from django.core.exceptions import ValidationError
from .base_gen_models import ModeloBaseGenerico
from entorno.constantes_base import ESTATUS_GEN


# ============================================
# 1. SG ENTIDAD TIPO DOCUMENTO (Ya existente)
# ============================================
class SgEntidadTipoDocumento(ModeloBaseGenerico):
    id_sg_entidad_tipo_documento = models.CharField(primary_key=True, max_length=36)
    estatus_sg_entidad_tipo_documento = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
    nombre = models.CharField("Nombre Entidad Tipo Documento", max_length=60)

    class Meta:
        db_table = 'sg_entidad_tipo_documento'
        verbose_name = 'SG Entidad Tipo Documento'
        verbose_name_plural = 'SG Entidad Tipo Documento'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ============================================
# 2. SG TIPO PERSONA (Ya existente)
# ============================================
class SgTipoPersona(ModeloBaseGenerico):
    id_sg_tipo_persona = models.CharField(primary_key=True, max_length=36)
    estatus_sg_tipo_persona = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
    tipo_persona = models.CharField("Tipo Persona", max_length=60)

    class Meta:
        db_table = 'sg_tipo_persona'
        verbose_name = 'SG Tipo Persona'
        verbose_name_plural = 'SG Tipos Personas'
        ordering = ['tipo_persona']

    def __str__(self):
        return self.tipo_persona


# ============================================
# 3. SG TIPO CUENTA (Ya existente)
# ============================================
class SgTipoCuenta(ModeloBaseGenerico):
    id_sg_tipo_cuenta = models.CharField(primary_key=True, max_length=36)
    estatus_sg_tipo_cuenta = models.BooleanField("Estatus", default=True, choices=ESTATUS_GEN)
    tipo_cuenta = models.CharField("Tipo Cuenta", max_length=60)

    class Meta:
        db_table = 'sg_tipo_cuenta'
        verbose_name = 'SG Tipo Cuenta'
        verbose_name_plural = 'SG Tipos Cuentas'
        ordering = ['tipo_cuenta']

    def __str__(self):
        return self.tipo_cuenta


# ============================================
# 4. SG NACIONALIDAD (NUEVO)
# Endpoint: GET /OnBoarding/Nacionalidades
# Response: { "idWeb": "...", "description": "Argentina" }
# ============================================
class SgNacionalidad(ModeloBaseGenerico):
    id_sg_nacionalidad = models.CharField(
        primary_key=True, 
        max_length=36,
        verbose_name="ID SG Nacionalidad"
    )
    estatus_sg_nacionalidad = models.BooleanField(
        "Estatus", 
        default=True, 
        choices=ESTATUS_GEN
    )
    descripcion = models.CharField(
        "Descripción", 
        max_length=100,
        help_text="Nombre de la nacionalidad (ej: Argentina, Uruguaya, etc.)"
    )
    # Campo extra para el país de nacimiento (mismo GUID que nacionalidad)
    # Por eso se usa el mismo modelo

    class Meta:
        db_table = 'sg_nacionalidad'
        verbose_name = 'SG Nacionalidad'
        verbose_name_plural = 'SG Nacionalidades'
        ordering = ['descripcion']

    def __str__(self):
        return self.descripcion


# ============================================
# 5. SG PROVINCIA (NUEVO)
# Endpoint: GET /OnBoarding/Provincias/Pais/AC98A1E7-CF65-4430-BF16-24439F35853B
# Response: { "idProvincia": "...", "codigolsoProvincia": "AR-K", 
#             "nombreProvincia": "Catamarca", "idPais": "...", "nombrePais": "Argentina" }
# ============================================
class SgProvincia(ModeloBaseGenerico):
    id_sg_provincia = models.CharField(
        primary_key=True, 
        max_length=36,
        verbose_name="ID SG Provincia"
    )
    estatus_sg_provincia = models.BooleanField(
        "Estatus", 
        default=True, 
        choices=ESTATUS_GEN
    )
    codigo_iso = models.CharField(
        "Código ISO", 
        max_length=10, 
        blank=True, 
        null=True,
        help_text="Código ISO de la provincia (ej: AR-K)"
    )
    nombre_provincia = models.CharField(
        "Nombre Provincia", 
        max_length=100,
        help_text="Nombre de la provincia (ej: Catamarca, Buenos Aires, etc.)"
    )
    id_pais = models.CharField(
        "ID País", 
        max_length=36,
        help_text="GUID del país (siempre Argentina: AC98A1E7-CF65-4430-BF16-24439F35853B)"
    )
    nombre_pais = models.CharField(
        "Nombre País", 
        max_length=60, 
        blank=True, 
        null=True,
        help_text="Nombre del país (ej: Argentina)"
    )

    class Meta:
        db_table = 'sg_provincia'
        verbose_name = 'SG Provincia'
        verbose_name_plural = 'SG Provincias'
        ordering = ['nombre_provincia']

    def __str__(self):
        return self.nombre_provincia


# ============================================
# 6. SG CONDICIÓN FISCAL (NUEVO)
# Endpoint: GET /OnBoarding/CondicionesFiscales
# Response: { "idWeb": "...", "descripcion": "Consumidor Final" }
# ============================================
class SgCondicionFiscal(ModeloBaseGenerico):
    id_sg_condicion_fiscal = models.CharField(
        primary_key=True, 
        max_length=36,
        verbose_name="ID SG Condición Fiscal"
    )
    estatus_sg_condicion_fiscal = models.BooleanField(
        "Estatus", 
        default=True, 
        choices=ESTATUS_GEN
    )
    descripcion = models.CharField(
        "Descripción", 
        max_length=100,
        help_text="Condición fiscal (ej: Consumidor Final, Responsable Inscripto, etc.)"
    )

    class Meta:
        db_table = 'sg_condicion_fiscal'
        verbose_name = 'SG Condición Fiscal'
        verbose_name_plural = 'SG Condiciones Fiscales'
        ordering = ['descripcion']

    def __str__(self):
        return self.descripcion


# ============================================
# 7. SG ESTADO CIVIL (NUEVO)
# Endpoint: GET /OnBoarding/EstadoCivil
# Response: { "id": "...", "description": "Casado" }
# ============================================
class SgEstadoCivil(ModeloBaseGenerico):
    id_sg_estado_civil = models.CharField(
        primary_key=True, 
        max_length=36,
        verbose_name="ID SG Estado Civil"
    )
    estatus_sg_estado_civil = models.BooleanField(
        "Estatus", 
        default=True, 
        choices=ESTATUS_GEN
    )
    descripcion = models.CharField(
        "Descripción", 
        max_length=50,
        help_text="Estado civil (ej: Soltero, Casado, Divorciado, Viudo, etc.)"
    )

    class Meta:
        db_table = 'sg_estado_civil'
        verbose_name = 'SG Estado Civil'
        verbose_name_plural = 'SG Estados Civiles'
        ordering = ['descripcion']

    def __str__(self):
        return self.descripcion


# ============================================
# 8. SG OCUPACIÓN (NUEVO)
# Endpoint: GET /OnBoarding/Ocupaciones
# Response: { "id": "...", "descripcion": "Comerciante" }
# ============================================
class SgOcupacion(ModeloBaseGenerico):
    id_sg_ocupacion = models.CharField(
        primary_key=True, 
        max_length=36,
        verbose_name="ID SG Ocupación"
    )
    estatus_sg_ocupacion = models.BooleanField(
        "Estatus", 
        default=True, 
        choices=ESTATUS_GEN
    )
    descripcion = models.CharField(
        "Descripción", 
        max_length=100,
        help_text="Ocupación (ej: Comerciante, Empleado, Profesional, etc.)"
    )

    class Meta:
        db_table = 'sg_ocupacion'
        verbose_name = 'SG Ocupación'
        verbose_name_plural = 'SG Ocupaciones'
        ordering = ['descripcion']

    def __str__(self):
        return self.descripcion


# ============================================
# 9. SG MOTIVO PEP (NUEVO)
# Endpoint: GET /OnBoarding/MotivosPEP
# Response: { "idWeb": "...", "descripcion": "..." }
# ============================================
class SgMotivoPEP(ModeloBaseGenerico):
    id_sg_motivo_pep = models.CharField(
        primary_key=True, 
        max_length=36,
        verbose_name="ID SG Motivo PEP"
    )
    estatus_sg_motivo_pep = models.BooleanField(
        "Estatus", 
        default=True, 
        choices=ESTATUS_GEN
    )
    descripcion = models.CharField(
        "Descripción", 
        max_length=100,
        help_text="Motivo por el cual es Persona Expuesta Políticamente"
    )

    class Meta:
        db_table = 'sg_motivo_pep'
        verbose_name = 'SG Motivo PEP'
        verbose_name_plural = 'SG Motivos PEP'
        ordering = ['descripcion']

    def __str__(self):
        return self.descripcion


# ============================================
# 10. SG ESTADO TRANSACCIÓN (NUEVO)
# Para referencia de estados en el sistema
# ============================================
class SgEstadoTransaccion(ModeloBaseGenerico):
    id_sg_estado_transaccion = models.CharField(
        primary_key=True, 
        max_length=36,
        verbose_name="ID SG Estado Transacción"
    )
    estatus_sg_estado_transaccion = models.BooleanField(
        "Estatus", 
        default=True, 
        choices=ESTATUS_GEN
    )
    codigo = models.CharField(
        "Código", 
        max_length=50,
        help_text="Código del estado (ej: Procesado, Pendiente, Error)"
    )
    descripcion = models.CharField(
        "Descripción", 
        max_length=100,
        help_text="Descripción del estado"
    )
    es_final = models.BooleanField(
        "Es Estado Final", 
        default=False,
        help_text="Indica si es un estado final (terminó el proceso)"
    )
    es_exitoso = models.BooleanField(
            "Es Exitoso", 
            default=False,
            help_text="Indica si es un estado exitoso (el proceso terminó correctamente)"
        )

    class Meta:
        db_table = 'sg_estado_transaccion'
        verbose_name = 'SG Estado Transacción'
        verbose_name_plural = 'SG Estados Transacciones'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


# ============================================
# 11. SG CONCEPTO TRANSACCIÓN (NUEVO)
# Para referencia de conceptos en transferencias
# ============================================
class SgConceptoTransaccion(ModeloBaseGenerico):
    id_sg_concepto_transaccion = models.CharField(
        primary_key=True, 
        max_length=36,
        verbose_name="ID SG Concepto Transacción"
    )
    estatus_sg_concepto_transaccion = models.BooleanField(
        "Estatus", 
        default=True, 
        choices=ESTATUS_GEN
    )
    codigo = models.CharField(
        "Código", 
        max_length=10,
        help_text="Código del concepto (ej: VAR, ALQ, EXP, FAC, HON)"
    )
    descripcion = models.CharField(
        "Descripción", 
        max_length=100,
        help_text="Descripción del concepto (ej: Varios, Alquileres, Expensas, etc.)"
    )
    guid = models.CharField(
        "GUID", 
        max_length=36,
        help_text="GUID del concepto en Agilpagos"
    )

    class Meta:
        db_table = 'sg_concepto_transaccion'
        verbose_name = 'SG Concepto Transacción'
        verbose_name_plural = 'SG Conceptos Transacciones'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"
    
# ============================================
# Nuevos Modelos para SG CATALOGO
# ============================================

# CREATE TABLE tipo_impuesto
class SgTipoImpuesto(ModeloBaseGenerico):
    id_sg_tipo_impuesto = models.CharField(
            primary_key=True, 
            max_length=36,
            verbose_name="ID SG Tipo Impuesto"
        )
    estatus_sg_tipo_impuesto = models.BooleanField(
            "Estatus", 
            default=True, 
            choices=ESTATUS_GEN
        )
    descripcion = models.CharField(
            "Descripción", 
            max_length=60,
            help_text="Descripción del tipo de impuesto (ej: Impuesto SIRCUPA, Impuesto Ley 25.413, etc.)"
        )
    
    class Meta:
            db_table = 'sg_tipo_impuesto'
            verbose_name = 'SG Tipo Impuesto'
            verbose_name_plural = 'SG Tipos Impuestos'
            ordering = ['descripcion']
    
    def __str__(self):
        return self.descripcion


# CREATE TABLE tipo_operacion_aviso
class SgTipoOperacionAviso(ModeloBaseGenerico):
    id_sg_tipo_operacion_aviso = models.CharField(
            primary_key=True, 
            max_length=36,
            verbose_name="ID SG Tipo Operación Aviso"
        )
    estatus_sg_tipo_operacion_aviso = models.BooleanField(
            "Estatus", 
            default=True, 
            choices=ESTATUS_GEN
        )
    descripcion = models.CharField(
            "Descripción", 
            max_length=60,
            help_text="Descripción del tipo de Operación de Aviso"
        )
    
    class Meta:
            db_table = 'sg_tipo_operacion_aviso'
            verbose_name = 'SG Tipo Operación Aviso'
            verbose_name_plural = 'SG Tipos Operación Avisos'
            ordering = ['descripcion']
    
    def __str__(self):
        return self.descripcion


# CREATE TABLE tipo_cuenta_mutual
class SgTipoCuentaMutual(ModeloBaseGenerico):
    id_sg_tipo_cuenta_mutual = models.BigIntegerField(
            primary_key=True, 
        )
    estatus_sg_tipo_cuenta_mutual = models.BooleanField(
            "Estatus", 
            default=True, 
            choices=ESTATUS_GEN
        )
    codigo_letra = models.CharField(
            "Código Letra", 
            max_length=1, 
            unique=True
        )
    descripcion = models.CharField(
            "Descripción", 
            max_length=60, 
        )

    class Meta:
        db_table = 'sg_tipo_cuenta_mutual'
        verbose_name = 'SG Tipo Cuenta Mutual'
        verbose_name_plural = 'SG Tipos Cuentas Mutuales'
        ordering = ['descripcion']

    def __str__(self):
        return self.descripcion
    
    
# CREATE TABLE constante_agilpagos
class SgConstanteAgilpagos(ModeloBaseGenerico):
    clave = models.CharField(
            primary_key=True, 
            max_length=60,
        )
    estatus_sg_constante_agilpagos = models.BooleanField(
            "Estatus", 
            default=True, 
            choices=ESTATUS_GEN
        )    
    valor = models.CharField(
                "Valor", 
                max_length=36, 
            )
    descripcion = models.CharField(
            "Descripción", 
            max_length=200, 
        )
    
    class Meta:
            db_table = 'sg_constante_agilpagos'
            verbose_name = 'SG Constante Agilpagos'
            verbose_name_plural = 'SG Constantes Agilpagos'
            ordering = ['descripcion']
    
    def __str__(self):
        return self.descripcion


# CREATE TABLE ambiente_agilpagos
class SgAmbienteAgilpagos(ModeloBaseGenerico):
    id_sg_ambiente_agilpagos = models.BigIntegerField(
            primary_key=True, 
        )
    estatus_sg_ambiente_agilpagos = models.BooleanField(
            "Estatus", 
            default=True, 
            choices=ESTATUS_GEN
        )
    nombre = models.CharField(
            "Nombre", 
            max_length=10,
            unique=True)
    url_base = models.CharField(
            "URL Base", 
            max_length=255,
        )
    url_onboarding = models.CharField(
                "URL Onboarding", 
                max_length=255,
            )
    url_swagger = models.CharField(
                    "URL Swagger", 
                    max_length=255,
                )
    id_entidad = models.CharField(
            "ID Entidad",
            max_length=36,
        )
    id_entidad_tipo_documento = models.CharField(
            "ID Entidad Tipo Documento",
            max_length=36,
        )
    class Meta:
            db_table = 'sg_ambiente_agilpagos'
            verbose_name = 'SG Ambiente Agilpagos'
            verbose_name_plural = 'SG Ambientes Agilpagos'
            ordering = ['nombre']
        
    def __str__(self):
        return self.nombre