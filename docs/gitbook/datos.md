# Base de datos y privacidad

PostgreSQL 16 con **23 tablas**. El esquema se crea con seis scripts numerados que se ejecutan en orden; no se usa ORM ni Alembic. Al arrancar, el backend (`app/preparar.py`) aplica los que falten, y desde el 05 todos se pueden volver a ejecutar sin error:

| Script | Contenido |
|---|---|
| `db/01_schema.sql` | 19 tablas del modelo de datos, restricciones, índices y vista de exportación |
| `db/02_catalogos.sql` | Roles, niveles y datasets públicos |
| `db/03_ajustes_srs.sql` | Campos que pide el SRS (descripción del caso, puntaje y fuente por opción, insignias) y las tablas `caso_version` y `sesion_revocada` |
| `db/04_estudios_recuperacion.sql` | Tabla `recuperacion_contrasena` y avisos de comentarios |
| `db/05_recursos_en_base.sql` | Tabla `recurso_contenido`: las imágenes y videos de los casos se guardan en la base para que no se pierdan al redesplegar |
| `db/06_kvasir_seg.sql` | Registra el dataset Kvasir-SEG en el catálogo |

## Protección de datos (Congreso de la República de Colombia, 2012)

* **Autorizaciones separadas:** política de tratamiento (obligatoria), datos sensibles y compartir el avance, con versión y fecha; se pueden revocar.
* **Derechos del titular:** consulta de todos sus datos, rectificación y supresión de la cuenta.
* **Contraseñas** con bcrypt; **sesiones** que se invalidan al cerrar.
* **Estudios propios:** se quitan los metadatos EXIF y DICOM, se guarda solo la imagen y se cifra en reposo.
* **Exportación seudonimizada:** cada persona se identifica con un código SHA-256 con sal; no salen nombres ni correos.
* **Bitácora** de cambios y de cada consulta del profesional al avance individual.

## En la demostración pública

* La base es PostgreSQL 16 gratuita de Render (`colorrectal-sim-db`). Vence hacia el 12-12-2026; antes hay que respaldarla o pasarla a otro plan.
* Con `ENTORNO=demostracion` la API rechaza subir estudios propios (responde 403), para no recibir datos reales de pacientes.
