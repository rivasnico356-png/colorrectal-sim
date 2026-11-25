-- Colorrectal-Sim · Ajustes al esquema para cumplir el SRS v1.2
-- Agrega los campos que pide el SRS y que no estaban en la Arquitectura de datos v1.0.
-- Cada cambio indica el requisito que lo exige.
BEGIN;

-- RF-002 2.1: descripción en lenguaje sencillo y datos del paciente simulado.
-- RF-002 2.5: fecha en que el revisor aprobó el caso.
ALTER TABLE caso
    ADD COLUMN descripcion       TEXT,
    ADD COLUMN contexto_simulado TEXT,
    ADD COLUMN fecha_revision    TIMESTAMPTZ;

-- RF-002 2.3: puntaje por opción (correcta, parcial o incorrecta), explicación y fuente.
-- RF-004 4.1 y 4.4: opción que recomienda la IA en la etapa (puede ser errónea a propósito).
ALTER TABLE opcion_decision
    ADD COLUMN puntaje        SMALLINT DEFAULT 0 NOT NULL,
    ADD COLUMN fuente         TEXT,
    ADD COLUMN recomendada_ia BOOLEAN DEFAULT FALSE NOT NULL,
    ADD CONSTRAINT ck_opcion_decision_puntaje CHECK (puntaje BETWEEN 0 AND 100);
CREATE UNIQUE INDEX uq_opcion_recomendada ON opcion_decision (id_etapa) WHERE recomendada_ia;

-- RF-002 2.1b: al editar un caso se conserva la versión anterior.
CREATE TABLE caso_version (
    id_version     BIGINT GENERATED ALWAYS AS IDENTITY,
    id_caso        BIGINT NOT NULL,
    numero         INTEGER NOT NULL,
    contenido      JSONB NOT NULL,
    id_editor      UUID NOT NULL,
    fecha          TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT pk_caso_version PRIMARY KEY (id_version),
    CONSTRAINT fk_caso_version_caso FOREIGN KEY (id_caso) REFERENCES caso (id_caso) ON DELETE CASCADE,
    CONSTRAINT fk_caso_version_editor FOREIGN KEY (id_editor) REFERENCES usuario (id_usuario),
    CONSTRAINT uq_caso_version UNIQUE (id_caso, numero)
);

-- RF-001 1.2b: al cerrar sesión el token queda invalidado.
CREATE TABLE sesion_revocada (
    jti            UUID,
    expira         TIMESTAMPTZ NOT NULL,
    CONSTRAINT pk_sesion_revocada PRIMARY KEY (jti)
);

-- RF-009 9.3: el titular puede suprimir su cuenta.
ALTER TABLE usuario DROP CONSTRAINT ck_usuario_1;
ALTER TABLE usuario ADD CONSTRAINT ck_usuario_1 CHECK (estado IN ('activo','inactivo','suprimido'));

-- RF-006 6.2: insignias configurables por el administrador (criterio legible y regla de cálculo).
ALTER TABLE insignia ADD COLUMN regla VARCHAR(40);
INSERT INTO insignia (nombre, criterio, regla) VALUES
    ('Primer caso', 'Completar el primer caso de simulación.', 'casos_completados>=1'),
    ('Caso perfecto', 'Responder bien todas las etapas de un caso.', 'caso_perfecto'),
    ('Ojo crítico', 'Detectar 3 recomendaciones erróneas de la IA sin seguirlas.', 'ia_erronea_detectada>=3'),
    ('Constancia', 'Completar 5 casos.', 'casos_completados>=5');

COMMIT;
