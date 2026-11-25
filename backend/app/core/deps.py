"""Dependencias comunes: usuario autenticado y control de acceso por rol (RF-001 1.4, RNF-003)."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import leer_token

esquema = HTTPBearer(auto_error=False)

USUARIO, PROFESIONAL, ADMIN = "Usuario", "Profesional de la salud", "Administrador"


def usuario_actual(cred: HTTPAuthorizationCredentials | None = Depends(esquema), db: Session = Depends(get_db)) -> dict:
    if cred is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Debes iniciar sesión.")
    try:
        datos = leer_token(cred.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La sesión no es válida o expiró.") from exc
    # RF-001 1.2b: un token de una sesión cerrada ya no sirve.
    revocada = db.execute(text("SELECT 1 FROM sesion_revocada WHERE jti = CAST(:j AS uuid)"), {"j": datos.get("jti")}).first()
    activo = db.execute(text("SELECT estado = 'activo' FROM usuario WHERE id_usuario = CAST(:u AS uuid)"),
                        {"u": datos["sub"]}).scalar()
    if revocada or not activo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La sesión no es válida o expiró.")
    return datos


def requiere_rol(*roles: str):
    def _verificar(usuario: dict = Depends(usuario_actual)) -> dict:
        if usuario.get("rol") not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para esta acción.")
        return usuario
    return _verificar
