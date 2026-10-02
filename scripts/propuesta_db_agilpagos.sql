-- =====================================================================
-- HOME MUTUAL — Integración API Billetera Agilpagos (SG Fintech)
-- Esquema de base de datos (PostgreSQL)
-- Basado en: API Billetera - Especificaciones v3.0 (Agosto 2026)
-- =====================================================================
--
-- Organización del esquema:
--   1) Catálogos / constantes de Agilpagos
--   2) Maestro de Usuarios y CVU (espejo de Onboarding)
--   3) Transacciones salientes (las que origina la Mutual)
--   4) Impuestos / retenciones (multi-gravamen)
--   5) Eventos entrantes (webhooks que expone la Mutual)
--   6) Conciliación / sincronización con VFP
--
-- CONVENCIÓN DE NOMBRES:
--   - Tablas: singular, snake_case. Los catálogos NO llevan prefijo
--     (estado_civil, no cat_estado_civil).
--   - Campos: snake_case, compuestos separados por guión bajo.
--   - Todo identificador empieza con "id_": la PK de una tabla es
--     id_<nombre_tabla> (ej. estado_civil.id_estado_civil), y una FK
--     que referencia otra tabla local usa id_<entidad> (ej.
--     cvu.id_usuario en vez de usuario_id).
--   - EXCEPCIÓN deliberada: los campos que replican literalmente un
--     campo del JSON de Agilpagos (idWebOperacion, idTransaccion,
--     idCoelsa, idConcepto, idEstado, etc.) conservan ese nombre tal
--     cual figura en la documentación, aunque el catálogo que
--     referencian tenga su PK nombrada distinto. Esto mantiene el
--     mapeo Request/Response <-> columna directo y evita traducir
--     nombres en cada integración.
-- =====================================================================

-- Esto ya no se debe hacer. Primero se debe crear la base de datos (calchaqui_agilpagos) desde PGAdmin 
-- como una BD independiente, luego conectar con la BD y ejecutar este script.

--CREATE SCHEMA IF NOT EXISTS calchaqui_agilpagos;
--SET search_path TO calchaqui;

-- =====================================================================
-- 1) CATÁLOGOS DE AGILPAGOS
-- =====================================================================
-- Estos valores rara vez cambian, pero conviene tenerlos en tabla (y no
-- hardcodeados en el código) porque se consultan por GET y se pueden
-- resincronizar. Sección 3.0 del documento.

-- OK
CREATE TABLE pais (
    id_pais         UUID PRIMARY KEY,
    nombre_pais     VARCHAR(100) NOT NULL,
    actualizado_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- OJO — "Conflicto de Mapping" señalado por la propia doc (3.0):
-- Agilpagos usa DOS GUID distintos para "Argentina" según el contexto:
--   - AC98A1E7-CF65-4430-BF16-24439F35853B: "idPaisWeb" que se usa para
--     consultar GET /OnBoarding/Provincias/Pais/{idPaisWeb}. Es el valor
--     que efectivamente aparece como id_pais en cada fila de provincia,
--     por eso es el que se guarda acá.
--   - 76B19E61-B8DC-40F4-BFAB-422CBFFE5002: id de "Argentina" dentro del
--     catálogo de Nacionalidades, y es el mismo valor que exige el campo
--     idPaisDomicilio. Se guarda como constante en constante_agilpagos,
--     NO en esta tabla, porque pertenece a otro namespace de IDs.
INSERT INTO pais (id_pais, nombre_pais) VALUES
    ('AC98A1E7-CF65-4430-BF16-24439F35853B', 'Argentina');

-- OK
CREATE TABLE provincia (
    id_provincia         UUID PRIMARY KEY,
    codigo_iso_provincia VARCHAR(10),
    nombre_provincia     VARCHAR(100) NOT NULL,
    id_pais              UUID NOT NULL REFERENCES pais(id_pais),
    actualizado_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- OK
CREATE TABLE nacionalidad (
    id_nacionalidad UUID PRIMARY KEY,
    descripcion     VARCHAR(100) NOT NULL,
    actualizado_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- OK
CREATE TABLE estado_civil (
    id_estado_civil UUID PRIMARY KEY,
    descripcion     VARCHAR(50) NOT NULL,
    actualizado_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- OK
CREATE TABLE condicion_fiscal (
    id_condicion_fiscal UUID PRIMARY KEY,
    descripcion          VARCHAR(100) NOT NULL,
    actualizado_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- OK
CREATE TABLE ocupacion (
    id_ocupacion   UUID PRIMARY KEY,
    descripcion    VARCHAR(100) NOT NULL,
    actualizado_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- OK
CREATE TABLE motivo_pep (
    id_motivo_pep  UUID PRIMARY KEY,
    descripcion    VARCHAR(200) NOT NULL,
    actualizado_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Conceptos de transferencia (5.2) — son fijos según la doc, pero se
-- modelan en tabla por si Agilpagos agrega nuevos.

-- PENDIENTE
-- SgEstadoTransaccion
CREATE TABLE concepto_transferencia (
    id_concepto_transferencia UUID PRIMARY KEY,
    codigo                    VARCHAR(10) NOT NULL,   -- VAR, ALQ, EXP, FAC, HON
    descripcion               VARCHAR(100) NOT NULL
);

INSERT INTO concepto_transferencia (id_concepto_transferencia, codigo, descripcion) VALUES
    ('45D4F58B-46A2-4754-BBFA-FECB8CF88BFC', 'VAR', 'Varios'),
    ('CC441F51-7531-424E-842A-C3A1DBBBF6CE', 'ALQ', 'Alquileres'),
    ('06A17DA8-57A5-4104-819A-F46ACE68E25F', 'EXP', 'Expensas'),
    ('FCEA71F5-7395-4CB0-B816-DA493F0605B5', 'FAC', 'Facturas'),
    ('B3300CA6-948C-4AB3-857E-4B88C29BE404', 'HON', 'Honorarios');

-- Estados de transacción (5.4) — GUID fijos documentados.
-- OK - Revisar
-- SgEstadoTransaccion
CREATE TABLE estado_transaccion (
    id_estado_transaccion UUID PRIMARY KEY,
    descripcion           VARCHAR(60) NOT NULL,
    es_final              BOOLEAN NOT NULL,
    es_exitoso            BOOLEAN NOT NULL   -- NULL/false si es error o no aplica
);

INSERT INTO estado_transaccion (id_estado_transaccion, descripcion, es_final, es_exitoso) VALUES
    ('FA4B44CA-685B-4625-8C47-81969A6E2598', 'Pendiente', FALSE, FALSE),
    ('E24A00E1-10A4-4E23-8D60-61EB055480AF', 'Informado Al Banco', FALSE, FALSE),
    ('0FFA0273-BC86-4BFA-9144-7FBF415B06EA', 'Pendiente Confirmación en Banco', FALSE, FALSE),
    ('1165CCFC-0E13-427A-86D2-E89782F9B2FF', 'Informado Al Banco Con Error', TRUE, FALSE),
    ('FC3F6A69-BE98-48B9-9842-4AE2C851E2DD', 'Pendiente de Informar al integrador', FALSE, FALSE),
    ('B1CE7121-7802-42DE-8891-64EF6FEB1223', 'Error al informar al integrador', FALSE, FALSE),
    ('5FB79B38-00ED-47B8-B7CE-B760CBEAE9D8', 'Procesado', TRUE, TRUE);

-- Tipos de impuesto (idWebOperacion de la sección 4). El campo que
-- referencia esta tabla desde impuesto_retencion se llama igual que en
-- el JSON de Agilpagos: id_web_operacion (ver excepción de convención).

-- NUEVO
-- SgTipoImpuesto
CREATE TABLE tipo_impuesto (
    id_tipo_impuesto UUID PRIMARY KEY,
    descripcion      VARCHAR(60) NOT NULL
);

INSERT INTO tipo_impuesto (id_tipo_impuesto, descripcion) VALUES
    ('A1254625-BA0F-474D-AD9D-15816099743C', 'Impuesto SIRCUPA'),
    ('A34A085B-F73D-41F1-AECF-DE8187AE6223', 'Impuesto Ley 25413');

-- Tipos de operación en avisos (idWebOperacion de la sección 6.1) —
-- distinto universo de GUID que el de impuestos, ojo con no confundirlos.

-- NUEVO
-- SgTipoOperacionAviso
CREATE TABLE tipo_operacion_aviso (
    id_tipo_operacion_aviso UUID PRIMARY KEY,
    descripcion             VARCHAR(60) NOT NULL
);

INSERT INTO tipo_operacion_aviso (id_tipo_operacion_aviso, descripcion) VALUES
    ('883E49C3-7AA2-42B7-A258-DEF8A6C6E838', 'Transferencias'),
    ('CB3F2930-B318-4DDB-8861-3C2926A87CF3', 'Operación con QR');

-- Tipos de cuenta de la Mutual (VFP identifica cada una con una letra:
-- C = Caja de Ahorro Común, E = Caja de Ahorro Especial,
-- D = Caja de Ahorro Diferencial). Se modela en catálogo porque además
-- existe un código numérico equivalente en VFP.
-- AJUSTAR id_tipo_cuenta_mutual con los códigos numéricos reales de VFP.

-- REVISAR
-- Parece redundante, se ha creado el modelo pero 
-- Hay ue comparar con el modelo SgTipoCuenta (CUENTA GENERAL)
-- SgTipoCuentaMutual
CREATE TABLE tipo_cuenta_mutual (
    id_tipo_cuenta_mutual SMALLINT PRIMARY KEY,   -- código numérico en VFP (a confirmar)
    codigo_letra          CHAR(1) NOT NULL UNIQUE, -- C / E / D
    descripcion           VARCHAR(60) NOT NULL
);

INSERT INTO tipo_cuenta_mutual (id_tipo_cuenta_mutual, codigo_letra, descripcion) VALUES
    (1, 'C', 'Caja de Ahorro Común'),
    (2, 'E', 'Caja de Ahorro Especial'),
    (3, 'D', 'Caja de Ahorro Diferencial');


-- Constantes fijas de la integración Agilpagos: valores que el propio
-- documento define como GUID únicos e invariables (no tienen endpoint
-- de consulta, hay que tenerlos hardcodeados en algún lado — mejor acá
-- que dispersos en el código de aplicación). Clave natural, no lleva
-- id_ porque no es un identificador sino un nombre de parámetro.


-- NUEVO
-- SgConstanteAgilpagos
CREATE TABLE constante_agilpagos (
    clave       VARCHAR(60) PRIMARY KEY,
    valor       UUID NOT NULL,
    descripcion VARCHAR(200) NOT NULL
);

INSERT INTO constante_agilpagos (clave, valor, descripcion) VALUES
    ('ID_NACIONALIDAD_PAIS_DOMICILIO_AR', '76B19E61-B8DC-40F4-BFAB-422CBFFE5002',
        'Argentina dentro del catálogo de Nacionalidades. Único valor admitido para idPaisDomicilio, y valor usado para idNacionalidad/idPaisNacimiento cuando corresponde a Argentina (3.0/3.1).'),
    ('ID_TIPO_DOCUMENTO_DNI', '209C1CAA-C56D-4E03-BB40-E9EF2F319A3F',
        'Valor fijo de idTipoDocumento representando DNI (3.1).'),
    ('ID_TIPO_PERSONA_FISICA', '20EB9127-7CA8-49E0-9E0B-CA8293218ACA',
        'Valor fijo de idTipoPersona para personas físicas (3.1).'),
    ('ID_TIPO_CUENTA_CVU', 'D2483A34-78BE-40A2-B8CB-07AD4BCF6F61',
        'Valor fijo de idTipoCuenta al dar de alta una CVU (3.1).'),
    ('ID_MOTIVO_BAJA_ARREPENTIMIENTO', '977E860B-368F-4B89-8F17-1DCE5335B9F5',
        'Valor de idMotivoBaja a usar en el DELETE de CVU / "botón de arrepentimiento" (3.3.2).');

-- Configuración por ambiente (UAT / PROD). id_entidad e
-- id_entidad_tipo_documento se reciben junto con las credenciales al
-- dar de alta el ambiente (2.1 / 3.1) y son distintos entre UAT y PROD.
-- Las credenciales en sí (client secret / API key) NO se guardan acá:
-- van en el gestor de secretos de la aplicación, no en la base de datos.

-- NUEVO
-- SgAmbienteAgilpagos
CREATE TABLE ambiente_agilpagos (
    id_ambiente_agilpagos     SMALLSERIAL PRIMARY KEY,
    nombre                    VARCHAR(10) NOT NULL UNIQUE,   -- 'UAT' | 'PROD'
    url_base                  VARCHAR(255) NOT NULL,
    url_onboarding            VARCHAR(255) NOT NULL,
    url_swagger               VARCHAR(255),
    id_entidad                UUID NOT NULL,
    id_entidad_tipo_documento UUID NOT NULL,   -- asociado al tipo de documento DNI para esta entidad/ambiente
    activo                    BOOLEAN NOT NULL DEFAULT TRUE,
    creado_at                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- 2) MAESTRO DE SOCIOS Y CVU
-- =====================================================================

-- socio: espejo 1:1 del "Usuario" de Agilpagos (que agrupa una o más
-- CVU). El puente hacia la Mutual es la clave compuesta sucursal +
-- código de socio (ej. sucursal 01 + socio 000373 = 1000373). Se
-- modela explícita (no como string armado) para poder indexar y
-- reportar por sucursal, y para no depender de que el padding se arme
-- siempre igual en el código de aplicación.
CREATE TABLE socio (
    id_socio                 BIGSERIAL PRIMARY KEY,
    id_sucursal              SMALLINT NOT NULL,            -- código de sucursal (2 dígitos, 01-99)
    codigo_socio             INTEGER NOT NULL,             -- código de socio dentro de la sucursal (hasta 6 dígitos)
    id_socio_mutual          INTEGER GENERATED ALWAYS AS (id_sucursal * 1000000 + codigo_socio) STORED,
        -- equivalente al id_socio de VFP, ej. sucursal 1 + socio 373 = 1000373
    id_usuario_agilpagos     UUID NOT NULL,                -- "idUsuario" devuelto en el alta
    cuit                     BIGINT NOT NULL,
    email                    VARCHAR(150) NOT NULL,        -- único por persona (regla 2.4.1)
    caracteristica_pais      VARCHAR(5),
    codigo_area              VARCHAR(10),
    numero_telefono          VARCHAR(20),
    nombre                   VARCHAR(40) NOT NULL,
    apellido                 VARCHAR(40) NOT NULL,
    genero                   CHAR(1),                      -- M/F/X
    fecha_nacimiento         DATE,
    numero_documento         VARCHAR(15) NOT NULL,         -- DNI, sin prefijo F/M (regla 3.1)
    numero_tramite_documento VARCHAR(20) NOT NULL,         -- impreso en el DNI
    id_nacionalidad          UUID REFERENCES nacionalidad(id_nacionalidad),
    id_pais_nacimiento       UUID REFERENCES nacionalidad(id_nacionalidad),
        -- mismo universo de valores que idNacionalidad; puede diferir de la nacionalidad actual
    id_estado_civil          UUID REFERENCES estado_civil(id_estado_civil),
    id_condicion_fiscal      UUID REFERENCES condicion_fiscal(id_condicion_fiscal),
    id_ocupacion             UUID REFERENCES ocupacion(id_ocupacion),
    es_pep                   BOOLEAN NOT NULL DEFAULT FALSE,
    id_motivo_pep            UUID REFERENCES motivo_pep(id_motivo_pep),
    es_uif                   BOOLEAN NOT NULL DEFAULT FALSE,
    ley_fatca                BOOLEAN NOT NULL DEFAULT FALSE,
    id_pais_domicilio        UUID NOT NULL DEFAULT '76b19e61-b8dc-40f4-bfab-422cbffe5002',
        -- CHECK: la API únicamente admite Argentina como domicilio (3.0).
        -- Se guarda igual (en vez de omitirlo) para dejar trazabilidad
        -- explícita del valor enviado, por si la restricción cambia.
    id_provincia             UUID REFERENCES provincia(id_provincia),
    localidad                VARCHAR(100),
    calle                    VARCHAR(150),
    altura                   VARCHAR(20),
    cp                       VARCHAR(15),
    piso                     VARCHAR(10),
    departamento             VARCHAR(10),
    observaciones_domicilio  VARCHAR(255),
    fecha_alta_agilpagos     DATE,
    estado                   BOOLEAN NOT NULL DEFAULT TRUE  -- espejo local, no confundir con estado de CVU

    -- ============================================================
    -- Restricciones de unicidad
    -- ============================================================
    CONSTRAINT uq_socio_usuario_agilpagos UNIQUE (id_usuario_agilpagos),
    CONSTRAINT uq_socio_cuit              UNIQUE (cuit),
    CONSTRAINT uq_socio_email             UNIQUE (email),
    CONSTRAINT uq_socio_documento         UNIQUE (numero_documento),
    -- Un código de socio solo es único dentro de su sucursal
    CONSTRAINT uq_socio_sucursal_codigo   UNIQUE (id_sucursal, codigo_socio),

    -- ============================================================
    -- Restricciones de rango para blindar la fórmula de id_socio_mutual
    -- ============================================================
    -- id_sucursal ocupa 2 dígitos (01-99) y codigo_socio hasta 6 dígitos (0-999999).
    -- Sin estos CHECK, por ejemplo (sucursal=2, codigo=0) y (sucursal=1, codigo=1000000)
    -- darían el mismo id_socio_mutual = 2000000.
    CONSTRAINT chk_socio_sucursal_rango CHECK (id_sucursal BETWEEN 1 AND 99),
    CONSTRAINT chk_socio_codigo_rango   CHECK (codigo_socio BETWEEN 0 AND 999999),

    -- ============================================================
    -- Reglas de negocio
    -- ============================================================
    -- La API solo admite Argentina como país de domicilio (3.0).
    CONSTRAINT chk_socio_pais_domicilio_ar
        CHECK (id_pais_domicilio = '76b19e61-b8dc-40f4-bfab-422cbffe5002')
);

-- Índices redundantes con los UNIQUE ya definidos, por eso quedan comentados:
-- ix_socio_socio_mutual  → solo útil si se consulta por id_socio_mutual directamente
-- ix_socio_sucursal      → redundante, es prefijo izquierdo de UNIQUE (id_sucursal, codigo_socio)
-- ix_socio_cuit          → redundante, ya cubierto por UNIQUE (cuit)
--
-- CREATE INDEX ix_socio_socio_mutual ON socio (id_socio_mutual);
-- CREATE INDEX ix_socio_sucursal     ON socio (id_sucursal);
-- CREATE INDEX ix_socio_cuit         ON socio (cuit);

-----------------------------------------------------------------------------------------------------------------------------------
-- cvu: cada fila es una CVU dada de alta (un socio puede tener varias,
-- una por tipo de caja: Común / Especial / Diferencial).
-- numero_cuenta_entidad es EL campo que define la Mutual y que NO es
-- reutilizable si se da de baja (regla 3.1) — ideal para trazabilidad.


CREATE TABLE cuenta_cvu (
    id_cvu                              BIGSERIAL PRIMARY KEY,
    id_socio                            BIGINT NOT NULL REFERENCES socio(id_socio),
    id_tipo_cuenta_mutual               SMALLINT NOT NULL REFERENCES tipo_cuenta_mutual(id_tipo_cuenta_mutual),
        -- distingue si esta CVU corresponde a la caja C, E o D del socio
    numero_cuenta_entidad               VARCHAR(30) NOT NULL UNIQUE,  -- definido por la Mutual; convención: id_socio_mutual + letra de tipo de cuenta (ver trigger más abajo)
    id_cvu                              UUID,                        -- "id" devuelto por GET /CVU, usado para Saldos/Movimientos (7.1) OJO!
    cvu                                 VARCHAR(22) NOT NULL UNIQUE,
    alias                               VARCHAR(20) UNIQUE,
    id_usuario_entidad_lineas_cuentas   UUID,                        -- devuelto en el alta, usado en algunos endpoints
    estado_vcu                          VARCHAR(30) NOT NULL DEFAULT 'Activo',
        -- valores documentados: Activo / Inactivo / Cerrado / Inactivo por usuario
    favorita                            BOOLEAN NOT NULL DEFAULT FALSE,  -- Cuenta por defecto.
    bloqueada_compliance                BOOLEAN NOT NULL DEFAULT FALSE, -- ver tabla evento_novedad_cvu (6.2)
    fecha_alta                          DATE,
    fecha_baja                          DATE,
    id_motivo_baja                      UUID,
    observaciones_baja                  VARCHAR(255),
    alias_actualizado_at                TIMESTAMPTZ,   -- para respetar la regla de 24hs entre cambios (3.2)
    UNIQUE (id_socio, id_tipo_cuenta_mutual)   -- un socio no puede tener 2 CVU del mismo tipo de caja
);

CREATE INDEX ix_cvu_usuario ON cvu (id_usuario);
CREATE INDEX ix_cvu_estado ON cvu (estado);
CREATE INDEX ix_cvu_tipo_cuenta ON cvu (id_tipo_cuenta_mutual);

-- Autogenera numero_cuenta_entidad si no se especifica explícitamente,
-- combinando id_socio_mutual (sucursal + socio) con la letra de tipo de
-- cuenta. Ej: sucursal 01 + socio 000373 + cuenta Común -> "1000373C".
-- Esto asegura que el identificador que se envía a Agilpagos (3.1)
-- siempre permite reconstruir sucursal, socio y tipo de cuenta con solo
-- mirarlo, sin depender de que cada desarrollador arme el string a mano.
CREATE OR REPLACE FUNCTION fn_generar_numero_cuenta_entidad()
RETURNS TRIGGER AS $$
DECLARE
    v_id_socio_mutual INTEGER;
    v_codigo_letra    CHAR(1);
BEGIN
    IF NEW.numero_cuenta_entidad IS NULL THEN
        SELECT id_socio_mutual INTO v_id_socio_mutual
        FROM usuario WHERE id_usuario = NEW.id_usuario;

        SELECT codigo_letra INTO v_codigo_letra
        FROM tipo_cuenta_mutual WHERE id_tipo_cuenta_mutual = NEW.id_tipo_cuenta_mutual;

        NEW.numero_cuenta_entidad := v_id_socio_mutual::TEXT || v_codigo_letra;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cvu_numero_cuenta_entidad
    BEFORE INSERT ON cvu
    FOR EACH ROW
    EXECUTE FUNCTION fn_generar_numero_cuenta_entidad();

-----------------------------------------------------------------------------------------------------------------------------------
-- Historial de alias (opcional pero recomendado: permite auditar cambios
-- y validar la regla de "1 cambio cada 24hs" sin depender solo del campo
-- alias_actualizado_at de la tabla cvu).
CREATE TABLE cvu_alias_historial (
    id_cvu_alias_historial BIGSERIAL PRIMARY KEY,
    id_cvu                 BIGINT NOT NULL REFERENCES cvu(id_cvu),
    alias_anterior         VARCHAR(20),
    alias_nuevo            VARCHAR(20) NOT NULL,
    origen                 VARCHAR(20) NOT NULL DEFAULT 'MUTUAL', -- MUTUAL | COELSA_AUTOMATICO
    creado_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-----------------------------------------------------------------------------------------------------------------------------------
-- De acá en adelante LEONCIO
-----------------------------------------------------------------------------------------------------------------------------------

-- =====================================================================
-- 3) TRANSACCIONES SALIENTES (las que origina la Mutual, sección 5)
-- =====================================================================
-- Una fila = una solicitud de transferencia (POST /Transacciones).
-- id_transaccion_entidad es NUESTRO identificador (obligatorio guardarlo,
-- se usa para consultar estado — 5.6 — y para idempotencia si hay que
-- reintentar el POST tras un timeout).

CREATE TABLE movimiento (
	id_movimiento            BIGSERIAL PRIMARY KEY,
	tipo_movimiento          VARCHAR(20) NOT NULL,  -- CASH_OUT | CASH_IN | REVERSA | IMPUESTO | AJUSTE
	
	-- identificación del socio y CVU.
	id_cvu                   BIGINT REFERENCES cvu(id_cvu),
	numero_cuenta_entidad    VARCHAR(30) NOT NULL UNIQUE,  -- definido por la Mutual; convención: id_socio_mutual + letra de tipo de cuenta (ver trigger)
	
	-- datos de la transacción.
	importe                  NUMERIC(15,2),
	fecha                    TIMESTAMPTZ NOT NULL DEFAULT now(),
	id_estado_transaccion    UUID REFERENCES estado_transaccion(id_estado_transaccion),
	conciliado               BOOLEAN NOT NULL DEFAULT FALSE,
	
    -- sincronización con VFP / contabilidad Mutual
    sincronizado_vfp         BOOLEAN NOT NULL DEFAULT FALSE,
    sincronizado_vfp_at      TIMESTAMPTZ,
    comprobante_vfp_id       BIGINT NOT NULL,   -- referencia al asiento/comprobante generado en VFP
	
    id_transaccion_agilpagos BIGINT NOT NULL,
	observaciones            VARCHAR(255) NOT NULL
);


-- Tabla para los datos del Request de Transferencias (CASH-OUT) (No sé si vale la pena crearla).
CREATE TABLE cashout_request (
    id_cashout_request       BIGSERIAL PRIMARY KEY,
	id_movimiento            BIGINT REFERENCES movimiento(id_movimiento),
	
	cuit_credito             BIGINT NOT NULL,
	cbu_credito              VARCHAR(22) NOT NULL,
	nombre_credito           VARCHAR(150),
	id_concepto              UUID NOT NULL REFERENCES concepto_transferencia(id_concepto_transferencia),
	importe                  NUMERIC(15,2) NOT NULL,
	descripcion              VARCHAR(255) NOT NULL,
	observaciones            VARCHAR(255) NOT NULL,
    id_transaccion_entidad   UUID NOT NULL,
    creado_at                TIMESTAMPTZ NOT NULL DEFAULT now()
;


-- Tabla para los datos del Response de Transferencias (CASH-OUT).
CREATE TABLE cashout_request (
    id_cashout_response      BIGSERIAL PRIMARY KEY,
	id_movimiento            BIGINT REFERENCES movimiento(id_movimiento),
	
    id_debito                UUID,       -- "id" del response
    id_estado_debito         UUID REFERENCES estado_transaccion(id_estado_transaccion),
    error_coelsa_debito      VARCHAR(255),
    total_debito             NUMERIC(15,2),
	
    id_credito               UUID,       -- "idCredito" (null si destino es externo)
    id_estado_credito        UUID REFERENCES estado_transaccion(id_estado_transaccion),
    error_coelsa_credito     VARCHAR(255),
    total_credito            NUMERIC(15,2),
	
	id_coelsa                VARCHAR(60)
;


-- Tabla para los datos del Response de Transferencias (CASH-OUT).
CREATE TABLE cashin_request (
    id_cashout_request        BIGSERIAL PRIMARY KEY,
	id_movimiento             BIGINT REFERENCES movimiento(id_movimiento),
	
    id_transaccion            UUID,       -- "idTransaccion" del request
    id_transaccion_anulada    UUID,       -- "idTransaccionAnulada" del request
	id_transaccion_originante BIGINT      -- "idTransaccionOriginante" del request
	id_transaccion_entidad    BIGINT      -- "idTransaccionEntidad" del request
    id_entidad                UUID,       -- "idEntidad" del request
	id_tipo_transaccion       BIGINT      -- "idTipoTransaccion" del request 1: Débito; 2: Crédito; 3:Reversa Débito; 4: Reversa Crédito
	id_web_operacion          UUID REFERENCES tipo_operacion_aviso(id_tipo_operacion_aviso),  -- "idWebOperacion" del request
	importe                   NUMERIC(15,2) NOT NULL,
	total                     NUMERIC(15,2) NOT NULL,       -- neto luego de impuestos
	id_moneda                 SMALLINT NOT NULL DEFAULT 1,  -- Fijo, para Peso Argentino.
	fecha_operacion           TIMESTAMPTZ NOT NULL,
	fecha_contable            TIMESTAMPTZ,
	observaciones             VARCHAR(255),
	numero_cuenta             VARCHAR(30) NOT NULL,      -- = numero_cuenta_entidad -> permite resolver el socio
	cvu                       VARCHAR(22) NOT NULL,
	cuenta_bloqueada          BOOLEAN NOT NULL DEFAULT FALSE,
	id_coelsa                 VARCHAR(60),
	
	-- contraparte
	cuenta_contraparte        VARCHAR(30),
	cuit_contraparte          BIGINT,
	titular_contraparte       VARCHAR(150),
;

-- =====================================================================
-- 4) IMPUESTOS / RETENCIONES (sección 4, esquema multi-gravamen)
-- =====================================================================
-- Una transacción (saliente o un aviso de crédito entrante) puede tener
-- 0, 1 o varias retenciones asociadas (ej. SIRCUPA + Ley 25413).
-- Se modela en tabla aparte y genérica porque aplica tanto a
-- cash_out como a cash_in (sección 5).

CREATE TABLE movimiento_impuesto (
    id_movimiento_impuesto     BIGSERIAL PRIMARY KEY,
	id_movimiento              BIGINT REFERENCES movimiento(id_movimiento),
	
    id_transaccion_impouesto   UUID NOT NULL,           -- id de la retención en sí (Agilpagos)
    id_transaccion_originante  UUID NOT NULL,           -- a qué transacción de crédito/débito se vincula
    importe                    NUMERIC(15,2) NOT NULL,
    id_tipo_transaccion        SMALLINT NOT NULL,       -- 1=Débito 2=Crédito 3=Reversa débito 4=Reversa crédito
    id_web_operacion           UUID NOT NULL REFERENCES tipo_impuesto(id_tipo_impuesto),

    UNIQUE (id_transaccion)
);


CREATE TABLE saldo_cvu (
	id_saldo_cvu           BIGSERIAL PRIMARY KEY,
	id_cvu                 BIGINT NOT NULL REFERENCES cvu(id_cvu),
	id_socio               BIGINT NOT NULL REFERENCES socio(id_socio),
	numero_cuenta_entidad  VARCHAR(30) NOT NULL UNIQUE
	saldo                  NUMERIC(15,2) NOT NULL
);

-- =====================================================================
-- FIN DEL SCRIPT
-- =====================================================================
