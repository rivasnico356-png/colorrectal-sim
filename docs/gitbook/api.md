# API REST

Base: `/api/v1`. La documentación interactiva está en `/docs` (Swagger) al ejecutar el backend. Todas las rutas, salvo registro, inicio de sesión, recuperación y salud, exigen el token en el encabezado `Authorization: Bearer`.

| Método | Ruta |
|---|---|
| PATCH | `/admin/usuarios/{id_usuario}` |
| GET | `/admin/usuarios` |
| POST | `/admin/usuarios` |
| POST | `/auth/login` |
| POST | `/auth/logout` |
| POST | `/auth/recuperar` |
| POST | `/auth/registro` |
| POST | `/auth/restablecer` |
| GET | `/casos` |
| GET | `/datasets` |
| PUT | `/editor/casos/{id_caso}/etapas` |
| POST | `/editor/casos/{id_caso}/revision` |
| GET | `/editor/casos/{id_caso}/versiones` |
| DELETE | `/editor/casos/{id_caso}` |
| GET | `/editor/casos/{id_caso}` |
| PUT | `/editor/casos/{id_caso}` |
| GET | `/editor/casos` |
| POST | `/editor/casos` |
| POST | `/editor/etapas/{id_etapa}/recursos` |
| POST | `/estudios/{id_estudio}/comentarios` |
| PUT | `/estudios/{id_estudio}/compartir` |
| GET | `/estudios/{id_estudio}/imagen` |
| DELETE | `/estudios/{id_estudio}` |
| GET | `/estudios/{id_estudio}` |
| GET | `/estudios` |
| POST | `/estudios` |
| GET | `/exportacion/interacciones.csv` |
| POST | `/intentos/{id_intento}/decisiones` |
| POST | `/intentos/{id_intento}/etapas/{id_etapa}/tutor` |
| GET | `/intentos/{id_intento}/resumen` |
| GET | `/intentos/{id_intento}` |
| POST | `/intentos` |
| GET | `/notificaciones` |
| PUT | `/privacidad/autorizaciones/{tipo}` |
| GET | `/privacidad/autorizaciones` |
| GET | `/privacidad/mis-datos` |
| GET | `/profesional/estudios` |
| GET | `/profesional/panel` |
| GET | `/profesional/usuarios/{id_usuario}/avance` |
| GET | `/progreso/historial` |
| GET | `/progreso` |
| GET | `/simulacion/aviso` |
| DELETE | `/usuarios/me` |
| GET | `/usuarios/me` |
| PATCH | `/usuarios/me` |
| DELETE | `/vinculos/{id_vinculo}` |
| PATCH | `/vinculos/{id_vinculo}` |
| GET | `/vinculos` |
| POST | `/vinculos` |
| GET | `/salud` |
