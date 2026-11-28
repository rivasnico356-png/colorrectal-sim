# Base de datos y privacidad

PostgreSQL 16 con **24 tablas**. El esquema se crea con nueve scripts numerados que se ejecutan en orden; no se usa ORM ni Alembic. Al arrancar, el backend (`app/preparar.py`) aplica los que falten, y desde el 05 todos se pueden volver a ejecutar sin error:

| Script | Contenido |
|---|---|
| `db/01_schema.sql` | 19 tablas del modelo de datos, restricciones, índices y vista de exportación |
| `db/02_catalogos.sql` | Roles, niveles, insignias y catálogo de datasets |
| `db/03_ajustes_srs.sql` | Campos que pide el SRS (descripción del caso, puntaje y fuente por opción, insignias) y las tablas `caso_version` y `sesion_revocada` |
| `db/04_estudios_recuperacion.sql` | Tabla `recuperacion_contrasena` y avisos de comentarios |
| `db/05_recursos_en_base.sql` | Tabla `recurso_contenido`: las imágenes y videos de los casos se guardan en la base para que no se pierdan al redesplegar |
| `db/06_kvasir_seg.sql` | Sin efecto; se conserva para no romper bases ya creadas |
| `db/07_solo_hyperkvasir.sql` | Deja HyperKvasir (Borgli et al., 2020), CC BY 4.0, como único dataset del catálogo |
| `db/08_estudios_en_base.sql` | Tabla `estudio_contenido`: los estudios propios cifrados se guardan en la base para que no se pierdan al reiniciar el servidor |
| `db/09_version_prompt_estudios.sql` | Columna `version_prompt` en `interpretacion_estudio` (RNF-007): cada interpretación guarda la versión del modelo y la del prompt del tutor |

## Protección de datos (Congreso de la República de Colombia, 2012)

* **Autorizaciones separadas:** política de tratamiento (obligatoria), datos sensibles y compartir el avance, con versión y fecha; se pueden revocar.
* **Derechos del titular:** consulta de todos sus datos, rectificación y supresión de la cuenta.
* **Contraseñas** con bcrypt; **sesiones** que se invalidan al cerrar.
* **Estudios propios:** se quitan los metadatos EXIF y DICOM, se guarda solo la imagen y se cifra en reposo.
* **Exportación seudonimizada:** cada persona se identifica con un código SHA-256 con sal; no salen nombres ni correos.
* **Bitácora** de cambios y de cada consulta del profesional al avance individual.

## En la demostración pública

* La base es PostgreSQL 16 gratuita de Render (`colorrectal-sim-db`). Vence hacia el 12-12-2026; antes hay que respaldarla o pasarla a otro plan.
* Con `ENTORNO=demostracion` la API rechaza subir estudios propios (responde 403), para no recibir datos reales de personas, salvo que `ESTUDIOS_EN_DEMO=1`: entonces los acepta con el aviso de usar solo imágenes de datasets públicos como HyperKvasir.
