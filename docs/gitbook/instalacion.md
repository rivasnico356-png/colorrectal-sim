# Instalación y ejecución

## Requisitos

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) y [Git](https://git-scm.com/).

## Pasos

```bash
git clone https://github.com/rivasnico356-png/colorrectal-sim.git
cd colorrectal-sim
cp .env.example .env      # completa los valores; nunca subas .env
docker compose up --build
```

| Servicio | Dirección |
|---|---|
| Aplicación web | http://localhost:5173 |
| API | http://localhost:8000/api/v1 |
| Documentación de la API | http://localhost:8000/docs |

## Variables principales

| Variable | Para qué |
|---|---|
| `JWT_SECRETO` | Firma de las sesiones |
| `IA_API_KEY` | Clave del proveedor de IA (opcional: sin ella se usa la explicación predefinida) |
| `TUTOR_MAX_CONSULTAS_ETAPA` | Preguntas al tutor por etapa |
| `CLAVE_CIFRADO_ESTUDIOS` | Cifrado de los estudios propios |
| `MODELO_VISION_RUTA` | Archivo ONNX del modelo de visión |
| `BREVO_API_KEY` y `SMTP_REMITENTE` | Correo de recuperación de contraseña por la API de Brevo (el remitente debe estar verificado en Brevo). Sin clave, en local se puede usar `SMTP_SERVIDOR` y relacionadas |
| `ADMIN_CORREO`, `ADMIN_NOMBRE` y `ADMIN_CONTRASENA` | Crean o sincronizan el primer administrador al arrancar |
| `ENTORNO` y `CASO_DEMO` | `demostracion` bloquea los estudios propios; `CASO_DEMO=1` publica el caso de demostración |

## Primer administrador

El registro público crea cuentas de Usuario. Si `ADMIN_CORREO` y `ADMIN_CONTRASENA` están definidas, el backend crea el administrador al arrancar (y si cambias la contraseña en la variable, la actualiza). También se puede crear a mano:

```bash
docker compose exec backend python -m app.crear_admin admin@ejemplo.com "Nombre del administrador"
```

Desde su cuenta se crean los profesionales de la salud en *Usuarios y roles*.

## Modelo de visión en local

Descarga `vision.onnx` y `vision.json` del release **modelo-vision** del repositorio y cópialos a `backend/modelos/`. Sin ellos la plataforma funciona igual y avisa que el modelo no está disponible. Los pasos para Windows están en [Modelo de visión](modelo-vision.md#usarlo-en-el-entorno-local).

## Demostración pública (Render)

El archivo `render.yaml` crea el servicio web y la base de datos. Las claves (`IA_API_KEY`, `BREVO_API_KEY`, `ADMIN_CONTRASENA`…) se escriben a mano en el panel de Render, en *Environment*; nunca en el repositorio. Cada cambio en `develop` se despliega solo y GitHub lo muestra en *Deployments*.
