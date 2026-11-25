"""Rutas del módulo M04 Agente tutor de IA (RF-004). Toda la lógica pasa por la fachada del tutor (patrón Facade)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import USUARIO, requiere_rol
from app.core.errores import ErrorNegocio
from app.modules.tutor.fachada import FachadaTutor

router = APIRouter(tags=["Agente tutor de IA"])


class ConsultaTutor(BaseModel):
    pregunta: str | None = Field(default=None, min_length=2, max_length=500)


@router.post("/intentos/{id_intento}/etapas/{id_etapa}/tutor")
def consultar(id_intento: int, id_etapa: int, consulta: ConsultaTutor, db: Session = Depends(get_db),
              usuario: dict = Depends(requiere_rol(USUARIO))) -> dict:
    """Sin pregunta: explica la sugerencia de la etapa (4.2). Con pregunta: consulta conversacional con límite (4.3)."""
    try:
        return FachadaTutor().consultar(db, id_intento, id_etapa, usuario["sub"], consulta.pregunta)
    except ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e
