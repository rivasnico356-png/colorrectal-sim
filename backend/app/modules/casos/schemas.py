"""Esquemas del módulo M02 Casos clínicos (RF-002)."""
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Tema = Literal["tamizaje", "pólipos", "estadios", "tratamiento", "seguimiento"]


class CasoIn(BaseModel):
    """RF-002 2.1: título, descripción sencilla, datos del paciente simulado y nivel."""
    titulo: str = Field(min_length=5, max_length=150)
    tema: Tema
    nivel_dificultad: int = Field(ge=1, le=5)
    descripcion: str = Field(min_length=20)
    contexto_simulado: str = Field(min_length=10)


class OpcionIn(BaseModel):
    """RF-002 2.3 y 2.4: opción con puntaje, explicación y fuente; puede ser la que recomienda la IA."""
    texto: str = Field(min_length=1)
    puntaje: int = Field(ge=0, le=100)
    retroalimentacion: str = Field(min_length=10)
    fuente: str = Field(min_length=5)
    es_correcta: bool = False
    recomendada_ia: bool = False


class EtapaIn(BaseModel):
    orden: int = Field(ge=1)
    enunciado: str = Field(min_length=10)
    recomendacion_ia: str = Field(min_length=10)
    usa_modelo_vision: bool = False
    opciones: list[OpcionIn] = Field(min_length=2)

    @model_validator(mode="after")
    def reglas(self):
        if sum(o.es_correcta for o in self.opciones) != 1:
            raise ValueError("Cada etapa debe tener exactamente una solución esperada.")
        if sum(o.recomendada_ia for o in self.opciones) != 1:
            raise ValueError("Marca la opción que recomienda la IA en esta etapa.")
        return self

    @property
    def ia_erronea_intencional(self) -> bool:
        return not next(o for o in self.opciones if o.recomendada_ia).es_correcta


class RevisionIn(BaseModel):
    """RF-002 2.5: el revisor registra la fuente clínica y aprueba o devuelve el caso."""
    accion: Literal["aprobar", "devolver", "publicar"]
    fuente_clinica: str | None = None
