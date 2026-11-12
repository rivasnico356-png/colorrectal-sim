# Base de datos y privacidad

PostgreSQL 16 con 22 tablas. El esquema se crea con cuatro scripts que Docker ejecuta en orden:

| Script | Contenido |
|---|---|
| `db/01_schema.sql` | 19 tablas del modelo de datos, restricciones, índices y vista de exportación |
| `db/02_catalogos.sql` | Roles, niveles y datasets públicos |
| `db/03_ajustes_srs.sql` | Campos que pide el SRS: descripción del caso, puntaje y fuente por opción, versiones, sesiones cerradas, insignias |
| `db/04_estudios_recuperacion.sql` | Recuperación de contraseña y avisos de comentarios |

## Protección de datos (Congreso de la República de Colombia, 2012)

* **Autorizaciones separadas:** política de tratamiento (obligatoria), datos sensibles y compartir el avance, con versión y fecha; se pueden revocar.
* **Derechos del titular:** consulta de todos sus datos, rectificación y supresión de la cuenta.
* **Contraseñas** con bcrypt; **sesiones** que se invalidan al cerrar.
* **Estudios propios:** se quitan los metadatos EXIF y DICOM, se guarda solo la imagen y se cifra en reposo.
* **Exportación seudonimizada:** cada persona se identifica con un código SHA-256 con sal; no salen nombres ni correos.
* **Bitácora** de cambios y de cada consulta del profesional al avance individual.
