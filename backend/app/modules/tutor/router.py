"""Rutas del módulo M04 Agente tutor de IA."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.deps import usuario_actual
from app.modules.tutor.prompt import VERSION_PROMPT
from app.modules.tutor.servicio import crear_servicio

router = APIRouter(tags=["Agente tutor de IA"])


class ConsultaTutor(BaseModel):
    enunciado: str = Field(max_length=2000)
    recomendacion: str = Field(max_length=2000)
    explicacion_predefinida: str = Field(max_length=2000)
    pregunta: str | None = Field(default=None, max_length=500)


@router.post("/tutor/explicar")
def explicar(consulta: ConsultaTutor, _: dict = Depends(usuario_actual)) -> dict:
    r = crear_servicio().explicar(consulta.enunciado, consulta.recomendacion,
                                  consulta.explicacion_predefinida, consulta.pregunta)
    return {"texto": r.texto, "proveedor": r.proveedor, "version_modelo": r.version_modelo,
            "version_prompt": VERSION_PROMPT, "latencia_ms": r.latencia_ms,
            "rotulo": "Resultado experimental de apoyo; no reemplaza la valoración de su médico."}
