"""Punto de entrada de la API de Colorrectal-Sim (monolito modular, ADR-01)."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.modules.casos.medios import router as medios_router
from app.modules.casos.router import router as casos_router
from app.modules.estudios.router import router as estudios_router
from app.modules.gamificacion import service as gamificacion  # noqa: F401  registra el observador de M06
from app.modules.privacidad.router import router as privacidad_router
from app.modules.progreso.router import router as progreso_router
from app.modules.simulacion.router import router as simulacion_router
from app.modules.tutor.router import router as tutor_router
from app.modules.usuarios.router import router as usuarios_router
from app.modules.vinculos.router import router as vinculos_router

s = get_settings()
app = FastAPI(title=s.app_nombre, version="0.5.0",
              description="API de la plataforma de simulación Colorrectal-Sim (Medical programmers, USC).")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in s.cors_origenes.split(",")],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])



@app.middleware("http")
async def cabeceras_seguridad(request, call_next):
    """RNF-003: cabeceras de seguridad (hallazgos del escaneo OWASP ZAP)."""
    respuesta = await call_next(request)
    respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
    # Las imágenes y videos de los casos (/media) se muestran con <img> y <video> desde el frontend, que corre en otro
    # puerto del mismo sitio; el resto de respuestas solo se leen con fetch (CORS) y pueden ser same-origin.
    politica = "same-site" if request.url.path.startswith("/media/") else "same-origin"
    respuesta.headers.setdefault("Cross-Origin-Resource-Policy", politica)
    respuesta.headers.setdefault("X-Frame-Options", "DENY")
    respuesta.headers.setdefault("Referrer-Policy", "no-referrer")
    return respuesta


for r in (usuarios_router, privacidad_router, vinculos_router, casos_router, simulacion_router, tutor_router, progreso_router,
          estudios_router):
    app.include_router(r, prefix="/api/v1")

# Imágenes y videos de los casos guardados en la base; va antes de la carpeta /media para tener prioridad.
app.include_router(medios_router)

# Imágenes y videos de los datasets públicos asociados a las etapas (RF-002 2.2).
Path(s.media_dir).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=s.media_dir), name="media")


@app.get("/api/v1/salud", tags=["Sistema"])
def salud() -> dict:
    return {"estado": "ok", "version": app.version}


# Despliegue público: la API sirve también el frontend compilado, así la aplicación tiene un solo enlace.
# Se monta al final para que /api, /docs y /media tengan prioridad.
if Path(s.web_dir).is_dir():
    app.mount("/", StaticFiles(directory=s.web_dir, html=True), name="web")
