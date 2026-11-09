"""Rutas del módulo M01 Usuarios y acceso."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import usuario_actual
from app.modules.usuarios import service
from app.modules.usuarios.schemas import LoginIn, RegistroIn, TokenOut, UsuarioOut

router = APIRouter(tags=["Usuarios y acceso"])


@router.post("/auth/registro", status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroIn, db: Session = Depends(get_db)) -> dict:
    try:
        return {"id_usuario": service.registrar(db, datos)}
    except service.ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e


@router.post("/auth/login", response_model=TokenOut)
def login(datos: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    try:
        token, rol = service.iniciar_sesion(db, datos.correo, datos.contrasena)
    except service.ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e
    return TokenOut(access_token=token, rol=rol)


@router.get("/usuarios/me", response_model=UsuarioOut)
def mi_perfil(usuario: dict = Depends(usuario_actual), db: Session = Depends(get_db)) -> UsuarioOut:
    fila = db.execute(
        text("""SELECT u.id_usuario::text, u.nombre, u.correo, r.nombre AS rol, u.puntaje_acumulado
                FROM usuario u JOIN rol r ON r.id_rol = u.id_rol WHERE u.id_usuario = :u"""),
        {"u": usuario["sub"]},
    ).mappings().first()
    if fila is None:
        raise HTTPException(404, "Usuario no encontrado.")
    return UsuarioOut(**fila)
