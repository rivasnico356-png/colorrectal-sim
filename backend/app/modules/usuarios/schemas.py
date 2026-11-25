"""Esquemas de entrada y salida del módulo M01 Usuarios y acceso."""
import re
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

RangoEdad = Literal["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]
Rol = Literal["Usuario", "Profesional de la salud", "Administrador"]


def validar_contrasena(v: str) -> str:
    """RF-001 1.1: mínimo 8 caracteres con letras y números."""
    if not (re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", v) and re.search(r"\d", v)):
        raise ValueError("La contraseña debe tener letras y números.")
    return v


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    contrasena: str = Field(min_length=8, max_length=72)
    rango_edad: RangoEdad
    acepta_politica: bool
    autoriza_datos_sensibles: bool = False
    autoriza_compartir: bool = False

    _contrasena = field_validator("contrasena")(validar_contrasena)

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
    rango_edad: str
    puntaje_acumulado: int
    nivel: str | None


class CuentaNuevaIn(BaseModel):
    """RF-001 1.1: el administrador crea cuentas de Profesional de la salud o Administrador."""
    nombre: str = Field(min_length=2, max_length=120)
    correo: EmailStr
    contrasena: str = Field(min_length=8, max_length=72)
    rol: Rol
    rango_edad: RangoEdad = "30-39"

    _contrasena = field_validator("contrasena")(validar_contrasena)


class CambioUsuarioIn(BaseModel):
    """RF-001 1.5: cambiar rol o activar/desactivar una cuenta."""
    rol: Rol | None = None
    estado: Literal["activo", "inactivo"] | None = None


class RecuperarIn(BaseModel):
    correo: EmailStr


class RestablecerIn(BaseModel):
    token: str = Field(min_length=20)
    contrasena: str = Field(min_length=8, max_length=72)

    _contrasena = field_validator("contrasena")(validar_contrasena)
