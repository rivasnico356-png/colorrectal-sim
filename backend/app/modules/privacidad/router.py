"""M09 Privacidad (RF-009, Ley 1581 de 2012): autorizaciones, consulta, rectificación y supresión de datos."""
import secrets
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import usuario_actual
from app.core.security import hash_contrasena, verificar_contrasena
from app.modules.usuarios.schemas import RangoEdad
from app.modules.usuarios.service import VERSION_POLITICA, bitacora

router = APIRouter(tags=["Privacidad"])

TipoRevocable = Literal["datos_sensibles", "compartir_avance"]


class AutorizacionIn(BaseModel):
    aceptada: bool


class RectificacionIn(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    rango_edad: RangoEdad | None = None


class SupresionIn(BaseModel):
    contrasena: str
    confirmar: bool


def _autorizaciones(db: Session, id_usuario: str) -> list[dict]:
    filas = db.execute(text("""SELECT tipo, version_politica, aceptada, fecha_aceptacion, fecha_revocacion
                               FROM autorizacion_datos WHERE id_usuario = CAST(:u AS uuid) ORDER BY id_autorizacion"""),
                       {"u": id_usuario}).mappings().all()
    return [dict(f) | {"version_vigente": VERSION_POLITICA} for f in filas]


@router.get("/privacidad/autorizaciones")
def ver_autorizaciones(usuario: dict = Depends(usuario_actual), db: Session = Depends(get_db)) -> list[dict]:
    """RF-009 9.1: la persona puede consultar en todo momento qué autorizó y con qué versión de la política."""
    return _autorizaciones(db, usuario["sub"])


@router.put("/privacidad/autorizaciones/{tipo}", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_autorizacion(tipo: TipoRevocable, datos: AutorizacionIn, usuario: dict = Depends(usuario_actual),
                         db: Session = Depends(get_db)) -> None:
    """RF-009 9.1: otorgar o revocar una autorización opcional. Revocar 'compartir_avance' deja de compartir con todos."""
    db.execute(text("""UPDATE autorizacion_datos
                       SET aceptada = :a, version_politica = :v,
                           fecha_aceptacion = CASE WHEN :a THEN now() ELSE fecha_aceptacion END,
                           fecha_revocacion = CASE WHEN :a THEN NULL ELSE now() END
                       WHERE id_usuario = CAST(:u AS uuid) AND tipo = :t"""),
               {"a": datos.aceptada, "v": VERSION_POLITICA, "u": usuario["sub"], "t": tipo})
    if tipo == "compartir_avance" and not datos.aceptada:
        db.execute(text("UPDATE vinculo SET autoriza_compartir = FALSE WHERE id_usuario = CAST(:u AS uuid) AND fecha_fin IS NULL"),
                   {"u": usuario["sub"]})
    bitacora(db, usuario["sub"], "autorizacion_datos", tipo, "otorgar" if datos.aceptada else "revocar")
    db.commit()


@router.get("/privacidad/mis-datos")
def mis_datos(usuario: dict = Depends(usuario_actual), db: Session = Depends(get_db)) -> dict:
    """RF-009 9.2: consulta de todos los datos personales que guarda la plataforma."""
    u = usuario["sub"]
    perfil = db.execute(text("""SELECT u.nombre, u.correo, u.rango_edad, r.nombre AS rol, u.fecha_registro, u.puntaje_acumulado
                                FROM usuario u JOIN rol r ON r.id_rol = u.id_rol WHERE u.id_usuario = CAST(:u AS uuid)"""),
                        {"u": u}).mappings().first()
    vinculos = db.execute(text("""SELECT p.nombre AS profesional, v.autoriza_compartir, v.fecha_inicio
                                  FROM vinculo v JOIN usuario p ON p.id_usuario = v.id_profesional
                                  WHERE v.id_usuario = CAST(:u AS uuid) AND v.fecha_fin IS NULL"""), {"u": u}).mappings().all()
    conteos = db.execute(text("""SELECT (SELECT count(*) FROM intento WHERE id_usuario = CAST(:u AS uuid)) AS intentos,
                                        (SELECT count(*) FROM estudio_propio WHERE id_usuario = CAST(:u AS uuid) AND NOT eliminado)
                                        AS estudios_propios"""), {"u": u}).mappings().first()
    return {"perfil": dict(perfil), "autorizaciones": _autorizaciones(db, u), "vinculos": [dict(v) for v in vinculos],
            "registros": dict(conteos)}


@router.patch("/usuarios/me", status_code=status.HTTP_204_NO_CONTENT)
def rectificar(datos: RectificacionIn, usuario: dict = Depends(usuario_actual), db: Session = Depends(get_db)) -> None:
    """RF-009 9.2b: rectificación de datos personales, registrada en la bitácora."""
    cambios = datos.model_dump(exclude_none=True)
    if not cambios:
        raise HTTPException(400, "No hay datos para actualizar.")
    db.execute(text("""UPDATE usuario SET nombre = coalesce(:n, nombre), rango_edad = coalesce(:e, rango_edad)
                       WHERE id_usuario = CAST(:u AS uuid)"""), {"n": datos.nombre, "e": datos.rango_edad, "u": usuario["sub"]})
    bitacora(db, usuario["sub"], "usuario", usuario["sub"], "rectificar", {"campos": sorted(cambios)})
    db.commit()


@router.delete("/usuarios/me", status_code=status.HTTP_204_NO_CONTENT)
def suprimir(datos: SupresionIn, usuario: dict = Depends(usuario_actual), db: Session = Depends(get_db)) -> None:
    """RF-009 9.3: supresión de la cuenta. Se borran los datos que identifican a la persona; las decisiones quedan
    solo con el identificador interno, que la exportación seudonimiza."""
    u = usuario["sub"]
    hash_actual = db.execute(text("SELECT hash_contrasena FROM usuario WHERE id_usuario = CAST(:u AS uuid)"), {"u": u}).scalar()
    if not datos.confirmar or not verificar_contrasena(datos.contrasena, hash_actual or ""):
        raise HTTPException(400, "Confirma la supresión con tu contraseña.")
    db.execute(text("""UPDATE usuario SET nombre = 'Cuenta suprimida', correo = 'suprimido-' || id_usuario || '@invalid',
                              hash_contrasena = :h, estado = 'suprimido'
                       WHERE id_usuario = CAST(:u AS uuid)"""), {"h": hash_contrasena(secrets.token_urlsafe(24)), "u": u})
    db.execute(text("""UPDATE autorizacion_datos SET aceptada = FALSE, fecha_revocacion = now()
                       WHERE id_usuario = CAST(:u AS uuid)"""), {"u": u})
    db.execute(text("UPDATE vinculo SET fecha_fin = now() WHERE (id_usuario = CAST(:u AS uuid) OR id_profesional = CAST(:u AS uuid)) "
                    "AND fecha_fin IS NULL"), {"u": u})
    db.execute(text("UPDATE estudio_propio SET eliminado = TRUE WHERE id_usuario = CAST(:u AS uuid)"), {"u": u})
    bitacora(db, u, "usuario", u, "suprimir")
    db.commit()
