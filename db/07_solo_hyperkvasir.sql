-- Colorrectal-Sim · Un solo dataset en el catálogo: HyperKvasir (licencia CC BY 4.0 verificada el 15-11-2026).
-- Idempotente: se aplica en cada arranque (ver app/preparar.py).
BEGIN;
INSERT INTO dataset (nombre, fuente_url, licencia, version, modalidad)
VALUES ('HyperKvasir', 'https://datasets.simula.no/hyper-kvasir/', 'CC BY 4.0 (Borgli et al., 2020)', NULL, 'endoscopia (imagen y video)')
ON CONFLICT (nombre) DO UPDATE SET fuente_url = EXCLUDED.fuente_url, licencia = EXCLUDED.licencia, modalidad = EXCLUDED.modalidad;

-- Los recursos que apuntaban a otro dataset (por ejemplo, la imagen del caso de demostración) pasan a HyperKvasir.
UPDATE recurso_multimedia
SET id_dataset = (SELECT id_dataset FROM dataset WHERE nombre = 'HyperKvasir'),
    licencia = 'HyperKvasir (Borgli et al., 2020), CC BY 4.0'
WHERE id_dataset IN (SELECT id_dataset FROM dataset WHERE nombre <> 'HyperKvasir');

DELETE FROM dataset WHERE nombre <> 'HyperKvasir';
COMMIT;
