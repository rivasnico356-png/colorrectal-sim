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
| `SMTP_SERVIDOR` y relacionadas | Correo de recuperación de contraseña |

## Primer administrador

El registro público crea cuentas de Usuario. El primer administrador se crea una sola vez con:

```bash
docker compose exec backend python -m app.crear_admin admin@ejemplo.com "Nombre del administrador"
```

Desde su cuenta se crean los profesionales de la salud en *Usuarios y roles*.
