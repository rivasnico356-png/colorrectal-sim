-- Colorrectal-Sim · RNF-007: cada interpretación de un estudio propio (RF-010 10.3) guarda la versión del modelo
-- de visión y también la versión del prompt del tutor que escribió la explicación.
-- Se puede ejecutar varias veces sin error (app/preparar.py lo aplica en cada arranque).
ALTER TABLE interpretacion_estudio ADD COLUMN IF NOT EXISTS version_prompt VARCHAR(20);
