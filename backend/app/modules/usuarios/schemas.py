"""Esquemas de entrada y salida del módulo M01 Usuarios y acceso."""
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

RangoEdad = Literal["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    contrasena: str = Field(min_length=8, max_length=72)
    rango_edad: RangoEdad
    acepta_politica: bool
    autoriza_datos_sensibles: bool = False
    autoriza_compartir: bool = False

    @field_validator("acepta_politica")
    @classmethod
    def politica_obligatoria(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Debes aceptar la política de tratamiento de datos para registrarte.")
        return v


class LoginIn(BaseModel):
    correo: EmailStr
    contrasena: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str


class UsuarioOut(BaseModel):
    id_usuario: str
    nombre: str
    correo: EmailStr
    rol: str
    puntaje_acumulado: int
