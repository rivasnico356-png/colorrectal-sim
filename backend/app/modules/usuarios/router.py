"""Rutas del módulo M01 Usuarios y acceso (RF-001)."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import ADMIN, esquema, requiere_rol, usuario_actual
from app.core.errores import ErrorNegocio
from app.modules.usuarios import service
from app.modules.usuarios.schemas import (
    CambioUsuarioIn,
    CuentaNuevaIn,
    LoginIn,
    RecuperarIn,
    RegistroIn,
    RestablecerIn,
    TokenOut,
    UsuarioOut,
)

router = APIRouter(tags=["Usuarios y acceso"])


@router.post("/auth/registro", status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroIn, db: Session = Depends(get_db)) -> dict:
    try:
        return {"id_usuario": service.registrar(db, datos)}
    except ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e


@router.post("/auth/login", response_model=TokenOut)
def login(datos: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    try:
        token, rol = service.iniciar_sesion(db, datos.correo, datos.contrasena)
    except ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e
    return TokenOut(access_token=token, rol=rol)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(cred: HTTPAuthorizationCredentials | None = Depends(esquema), _: dict = Depends(usuario_actual),
           db: Session = Depends(get_db)) -> None:
    service.cerrar_sesion(db, cred.credentials)


@router.post("/auth/recuperar", status_code=status.HTTP_202_ACCEPTED)
def recuperar(datos: RecuperarIn, db: Session = Depends(get_db)) -> dict:
    """RF-001 1.3: la respuesta es igual exista o no el correo."""
    service.solicitar_recuperacion(db, datos.correo)
    return {"mensaje": "Si el correo está registrado, te enviamos un enlace para restablecer la contraseña."}


@router.post("/auth/restablecer", status_code=status.HTTP_204_NO_CONTENT)
def restablecer(datos: RestablecerIn, db: Session = Depends(get_db)) -> None:
    try:
        service.restablecer(db, datos.token, datos.contrasena)
    except ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e


@router.get("/usuarios/me", response_model=UsuarioOut)
def mi_perfil(usuario: dict = Depends(usuario_actual), db: Session = Depends(get_db)) -> UsuarioOut:
    fila = db.execute(
        text("""SELECT u.id_usuario::text, u.nombre, u.correo, r.nombre AS rol, u.rango_edad, u.puntaje_acumulado,
                       n.nombre AS nivel
                FROM usuario u JOIN rol r ON r.id_rol = u.id_rol LEFT JOIN nivel n ON n.id_nivel = u.id_nivel
                WHERE u.id_usuario = CAST(:u AS uuid)"""),
        {"u": usuario["sub"]},
    ).mappings().first()
    if fila is None:
        raise HTTPException(404, "Usuario no encontrado.")
    return UsuarioOut(**fila)


# ---- RF-001 1.5: administración de usuarios (pantalla 13) ----

@router.get("/admin/usuarios")
def listar_usuarios(buscar: str | None = None, db: Session = Depends(get_db), _: dict = Depends(requiere_rol(ADMIN))) -> list[dict]:
    filas = db.execute(
        text("""SELECT u.id_usuario::text, u.nombre, u.correo, r.nombre AS rol, u.estado, u.fecha_registro
                FROM usuario u JOIN rol r ON r.id_rol = u.id_rol
                WHERE u.estado <> 'suprimido'
                  AND (CAST(:b AS text) IS NULL OR u.nombre ILIKE '%' || :b || '%' OR u.correo ILIKE '%' || :b || '%')
                ORDER BY u.fecha_registro DESC LIMIT 200"""),
        {"b": buscar},
    ).mappings().all()
    return [dict(f) for f in filas]


@router.post("/admin/usuarios", status_code=status.HTTP_201_CREATED)
def crear_cuenta(datos: CuentaNuevaIn, db: Session = Depends(get_db), admin: dict = Depends(requiere_rol(ADMIN))) -> dict:
    try:
        return {"id_usuario": service.crear_cuenta(db, admin["sub"], datos)}
    except ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e


@router.patch("/admin/usuarios/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_usuario(id_usuario: str, cambio: CambioUsuarioIn, db: Session = Depends(get_db),
                    admin: dict = Depends(requiere_rol(ADMIN))) -> None:
    try:
        service.cambiar_usuario(db, admin["sub"], id_usuario, cambio)
    except ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e
