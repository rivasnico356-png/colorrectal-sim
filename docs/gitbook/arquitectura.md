# Arquitectura

Colorrectal-Sim es un **monolito modular** (ADR-01): una sola API con módulos separados por responsabilidad, un frontend web y una base de datos relacional, todo en contenedores Docker.

```mermaid
flowchart LR
    U[Navegador<br/>React + TypeScript] -->|HTTPS / REST| A[API FastAPI]
    A --> DB[(PostgreSQL 16)]
    A --> IA[Proveedor de IA<br/>principal y alternativo]
    A --> V[Modelo de visión ONNX<br/>dentro del backend]
    A --> ES[(Estudios cifrados<br/>Fernet por archivo)]
    A --> C[Correo<br/>API HTTPS de Brevo]
```

Las imágenes y videos de los casos se guardan en la base (tabla `recurso_contenido`) y la API los sirve en `/media/recursos/…` con soporte de rangos para el video.

## Despliegue

| Entorno | Cómo corre |
|---|---|
| Local (desarrollo) | `docker compose up`: 3 contenedores (frontend con Vite, backend FastAPI y PostgreSQL 16) |
| Demostración pública | Render: un solo servicio Docker (`despliegue/Dockerfile`) que compila el frontend y lo sirve desde FastAPI, más una base PostgreSQL 16 administrada. Se despliega solo con cada cambio en `develop` (`render.yaml`) |

```mermaid
flowchart LR
    GH[GitHub · rama develop] -->|despliegue automático| R[Render · servicio web Docker<br/>FastAPI + frontend compilado + modelo ONNX]
    REL[GitHub Release modelo-vision] -->|vision.onnx al construir| R
    R --> PG[(Render PostgreSQL 16)]
    R --> G[Groq · tutor de IA]
    R --> B[Brevo · correo]
```

## Decisiones de arquitectura vigentes

| Decisión | Motivo |
|---|---|
| Monolito modular (ADR-01) | Un equipo pequeño y un solo despliegue |
| Modelo de visión en ONNX dentro del backend | Corre en CPU, sin GPU ni servicio aparte (reemplaza la idea de un servicio de inferencia separado) |
| Acceso a datos con SQL y scripts numerados | Control total del esquema del documento de datos, sin ORM ni Alembic |
| Correo por la API HTTPS de Brevo | Render gratuito bloquea los puertos SMTP; el SMTP queda como alternativa local |
| Despliegue en Render | Enlace público gratuito para el profesor y las pruebas con usuarios |

## Módulos del backend

| Módulo | Carpeta | Responsabilidad |
|---|---|---|
| M01 Usuarios y acceso | `usuarios/`, `vinculos/` | Registro, sesión, recuperación, roles, administración y vínculo |
| M02 Casos clínicos | `casos/` | Editor, versiones, recursos, revisión y catálogo |
| M03 Simulación · M05 Evaluación · M07 Interacción | `simulacion/` | Intentos, etapas, decisiones, puntaje y registro |
| M04 Tutor de IA | `tutor/` | Tutor con Groq (`gpt-oss-120b`) y respaldo (`gpt-oss-20b`), luego recomendación predefinida |
| M06 Gamificación | `gamificacion/` | Niveles e insignias |
| M08 Reportes | `progreso/` | Historial, progreso, panel y exportación |
| M09 Privacidad | `privacidad/` | Autorizaciones y derechos del titular |
| M10 Estudios propios | `estudios/` | Desidentificación, cifrado, modelo de visión y comentarios |

## Patrones de diseño

| Patrón | Dónde | Para qué |
|---|---|---|
| Adapter | `tutor/proveedores.py`, `estudios/vision.py` | Mismo contrato para cualquier proveedor de IA o modelo |
| Strategy | `tutor/servicio.py` | Cadena IA principal → alternativo → recomendación predefinida |
| Factory Method | `tutor/servicio.py::crear_servicio` | Arma la cadena desde la configuración |
| Observer | `core/eventos.py` | La evaluación publica *DecisionRegistrada* y la gamificación reacciona sin acoplarse |

## Reglas

* El frontend solo habla con la API REST.
* Los módulos no llaman servicios externos directamente: lo hacen por adaptadores.
* Las claves se leen de variables de entorno; nunca están en el repositorio.
