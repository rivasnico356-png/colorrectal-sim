-- Colorrectal-Sim · Kvasir-SEG en el catálogo de datasets (licencia verificada el 12-11-2026 en la fuente oficial).
-- Idempotente: se aplica en cada arranque (ver app/preparar.py).
INSERT INTO dataset (nombre, fuente_url, licencia, version, modalidad)
VALUES ('Kvasir-SEG', 'https://datasets.simula.no/kvasir-seg', 'Investigación y educación, con cita (Jha et al., 2020)', NULL,
        'colonoscopia con máscara')
ON CONFLICT (nombre) DO NOTHING;
