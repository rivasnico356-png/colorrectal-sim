-- Colorrectal-Sim · Estudios propios cifrados guardados en la base (RF-010 10.2, RNF-003).
-- Igual que recurso_contenido (05): el disco del plan gratuito de Render no es persistente, así que el archivo
-- cifrado se guarda en la base para que no se pierda cuando el servidor se reinicia.
-- Se puede ejecutar varias veces sin error (app/preparar.py lo aplica en cada arranque).
BEGIN;

CREATE TABLE IF NOT EXISTS estudio_contenido (
    id_estudio     BIGINT,
    datos_cifrados BYTEA NOT NULL,
    CONSTRAINT pk_estudio_contenido PRIMARY KEY (id_estudio),
    CONSTRAINT fk_estudio_contenido_estudio FOREIGN KEY (id_estudio) REFERENCES estudio_propio (id_estudio) ON DELETE CASCADE
);

COMMIT;
