-- Colorrectal-Sim · Contenido de las imágenes y videos de los casos guardado en la base (RF-002 2.2).
-- Así los recursos se conservan aunque el servidor se reinicie (el disco del plan gratuito de Render no es persistente)
-- y viajan con las copias de seguridad de la base.
-- Desde este script en adelante cada script debe poder ejecutarse varias veces sin error (app/preparar.py los aplica
-- en cada arranque a las bases que ya existen).
BEGIN;

CREATE TABLE IF NOT EXISTS recurso_contenido (
    id_recurso     BIGINT,
    tipo_mime      VARCHAR(20) NOT NULL,
    tamano_bytes   INTEGER NOT NULL,
    sha256         CHAR(64) NOT NULL,
    datos          BYTEA NOT NULL,
    CONSTRAINT pk_recurso_contenido PRIMARY KEY (id_recurso),
    CONSTRAINT fk_recurso_contenido_recurso FOREIGN KEY (id_recurso) REFERENCES recurso_multimedia (id_recurso) ON DELETE CASCADE,
    CONSTRAINT ck_recurso_contenido_1 CHECK (tamano_bytes > 0)
);

COMMIT;
