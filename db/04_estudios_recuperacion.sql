-- Colorrectal-Sim · Estudios propios (RF-010) y recuperación de contraseña (RF-001 1.3)
BEGIN;

-- RF-001 1.3: enlace de un solo uso que expira. Solo se guarda el hash del token.
CREATE TABLE recuperacion_contrasena (
    id_recuperacion  BIGINT GENERATED ALWAYS AS IDENTITY,
    id_usuario       UUID NOT NULL,
    hash_token       CHAR(64) NOT NULL UNIQUE,
    expira           TIMESTAMPTZ NOT NULL,
    usado            BOOLEAN DEFAULT FALSE NOT NULL,
    fecha            TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT pk_recuperacion_contrasena PRIMARY KEY (id_recuperacion),
    CONSTRAINT fk_recuperacion_usuario FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario) ON DELETE CASCADE
);

-- RF-010 10.4: la persona recibe un aviso cuando el profesional comenta su estudio.
ALTER TABLE comentario_estudio ADD COLUMN leido BOOLEAN DEFAULT FALSE NOT NULL;

-- RF-010 10.2: el sistema advierte si la imagen puede tener texto sobreimpreso.
ALTER TABLE estudio_propio ADD COLUMN advertencia_texto BOOLEAN DEFAULT FALSE NOT NULL;

COMMIT;
