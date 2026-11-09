"""Punto de entrada de la API de Colorrectal-Sim (monolito modular, ADR-01)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.modules.casos.router import router as casos_router
from app.modules.tutor.router import router as tutor_router
from app.modules.usuarios.router import router as usuarios_router

s = get_settings()
app = FastAPI(title=s.app_nombre, version="0.1.0",
              description="API de la plataforma de simulación Colorrectal-Sim (Medical programmers, USC).")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in s.cors_origenes.split(",")],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for r in (usuarios_router, casos_router, tutor_router):
    app.include_router(r, prefix="/api/v1")


@app.get("/api/v1/salud", tags=["Sistema"])
def salud() -> dict:
    return {"estado": "ok", "version": app.version}
