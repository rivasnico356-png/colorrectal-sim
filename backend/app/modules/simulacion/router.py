"""Rutas de M03 Simulación y M05 Evaluación."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import USUARIO, requiere_rol
from app.core.errores import ErrorNegocio
from app.modules.simulacion import service

router = APIRouter(tags=["Simulación"])
SOLO_USUARIO = requiere_rol(USUARIO)


class InicioIn(BaseModel):
    id_caso: int
    acepto_aviso: bool = False


class DecisionIn(BaseModel):
    id_etapa: int
    id_opcion: int
    confianza: int = Field(ge=1, le=5, description="RF-003 3.5: confianza declarada en escala 1 a 5")
    tiempo_ms: int | None = Field(default=None, ge=0)


def _ejecutar(funcion, *args):
    try:
        return funcion(*args)
    except ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e


@router.get("/simulacion/aviso")
def aviso() -> dict:
    return service.aviso()


@router.post("/intentos", status_code=status.HTTP_201_CREATED)
def iniciar(datos: InicioIn, db: Session = Depends(get_db), usuario: dict = Depends(SOLO_USUARIO)) -> dict:
    return _ejecutar(service.iniciar, db, usuario["sub"], datos.id_caso, datos.acepto_aviso)


@router.get("/intentos/{id_intento}")
def estado(id_intento: int, db: Session = Depends(get_db), usuario: dict = Depends(SOLO_USUARIO)) -> dict:
    return _ejecutar(service.estado, db, usuario["sub"], id_intento)


@router.post("/intentos/{id_intento}/decisiones")
def decidir(id_intento: int, datos: DecisionIn, db: Session = Depends(get_db), usuario: dict = Depends(SOLO_USUARIO)) -> dict:
    return _ejecutar(service.decidir, db, usuario["sub"], id_intento, datos.id_etapa, datos.id_opcion, datos.confianza,
                     datos.tiempo_ms)


@router.get("/intentos/{id_intento}/resumen")
def resumen(id_intento: int, db: Session = Depends(get_db), usuario: dict = Depends(SOLO_USUARIO)) -> dict:
    return _ejecutar(service.resumen, db, usuario["sub"], id_intento)
