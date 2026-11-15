-- Colorrectal-Sim · Datos de catálogo iniciales (sin datos personales)
BEGIN;
INSERT INTO rol (nombre) VALUES ('Usuario'), ('Profesional de la salud'), ('Administrador');

-- Niveles de gamificación (RF-006). Los puntajes mínimos se pueden ajustar.
INSERT INTO nivel (nombre, puntaje_minimo) VALUES ('Explorador', 0), ('Analista', 500), ('Experto', 1500);

-- Datasets públicos previstos (Arquitectura de datos, Tabla 2).
-- Licencias pendientes de verificar en la fuente oficial antes de usar cada imagen.
INSERT INTO dataset (nombre, fuente_url, licencia, version, modalidad) VALUES
 ('HyperKvasir', 'https://datasets.simula.no/hyper-kvasir/', 'CC BY 4.0 (Borgli et al., 2020)', NULL, 'endoscopia (imagen y video)');
COMMIT;
