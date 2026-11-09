"""Dependencias comunes: usuario autenticado y control de acceso por rol (RNF-003)."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import leer_token

esquema = HTTPBearer(auto_error=False)


def usuario_actual(cred: HTTPAuthorizationCredentials | None = Depends(esquema)) -> dict:
    if cred is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Debes iniciar sesión.")
    try:
        return leer_token(cred.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La sesión no es válida o expiró.") from exc


def requiere_rol(*roles: str):
    def _verificar(usuario: dict = Depends(usuario_actual)) -> dict:
        if usuario.get("rol") not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para esta acción.")
        return usuario
    return _verificar
