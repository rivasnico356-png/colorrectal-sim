"""Vínculo directo Usuario–Profesional de la salud (RF-001 1.6). Sin grupos ni códigos.

El Usuario busca a su profesional por correo, crea el vínculo y decide si comparte su avance.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import PROFESIONAL, USUARIO, requiere_rol, usuario_actual
from app.modules.usuarios.service import bitacora

router = APIRouter(tags=["Vínculo con el profesional"])


class VinculoIn(BaseModel):
    correo_profesional: EmailStr
    autoriza_compartir: bool = False


class CompartirIn(BaseModel):
    autoriza_compartir: bool


def _autorizo_compartir(db: Session, id_usuario: str) -> bool:
    return bool(db.execute(text("""SELECT aceptada FROM autorizacion_datos
                                   WHERE id_usuario = CAST(:u AS uuid) AND tipo = 'compartir_avance'"""),
                           {"u": id_usuario}).scalar())


@router.post("/vinculos", status_code=status.HTTP_201_CREATED)
def crear_vinculo(datos: VinculoIn, usuario: dict = Depends(requiere_rol(USUARIO)), db: Session = Depends(get_db)) -> dict:
    prof = db.execute(text("""SELECT u.id_usuario::text FROM usuario u JOIN rol r ON r.id_rol = u.id_rol
                              WHERE lower(u.correo) = lower(:c) AND r.nombre = :r AND u.estado = 'activo'"""),
                      {"c": datos.correo_profesional, "r": PROFESIONAL}).scalar()
    if prof is None:
        raise HTTPException(404, "No encontramos un profesional de la salud con ese correo.")
    if datos.autoriza_compartir and not _autorizo_compartir(db, usuario["sub"]):
        raise HTTPException(409, "Primero autoriza compartir tu avance en la sección de privacidad.")
    existe = db.execute(text("""SELECT 1 FROM vinculo WHERE id_usuario = CAST(:u AS uuid) AND id_profesional = CAST(:p AS uuid)
                                AND fecha_fin IS NULL"""), {"u": usuario["sub"], "p": prof}).first()
    if existe:
        raise HTTPException(409, "Ya estás vinculado con ese profesional.")
    id_vinculo = db.execute(text("""INSERT INTO vinculo (id_usuario, id_profesional, autoriza_compartir)
                                    VALUES (CAST(:u AS uuid), CAST(:p AS uuid), :a) RETURNING id_vinculo"""),
                            {"u": usuario["sub"], "p": prof, "a": datos.autoriza_compartir}).scalar_one()
    bitacora(db, usuario["sub"], "vinculo", str(id_vinculo), "crear")
    db.commit()
    return {"id_vinculo": id_vinculo}


@router.get("/vinculos")
def mis_vinculos(usuario: dict = Depends(usuario_actual), db: Session = Depends(get_db)) -> list[dict]:
    columna = "v.id_profesional" if usuario["rol"] == USUARIO else "v.id_usuario"
    otro = "v.id_usuario" if usuario["rol"] == USUARIO else "v.id_profesional"
    filas = db.execute(text(f"""SELECT v.id_vinculo, o.id_usuario::text AS id_persona, o.nombre, o.correo, v.autoriza_compartir, v.fecha_inicio
                               FROM vinculo v JOIN usuario o ON o.id_usuario = {columna}
                               WHERE {otro} = CAST(:u AS uuid) AND v.fecha_fin IS NULL ORDER BY v.fecha_inicio"""),
                       {"u": usuario["sub"]}).mappings().all()
    return [dict(f) for f in filas]


@router.patch("/vinculos/{id_vinculo}", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_compartir(id_vinculo: int, datos: CompartirIn, usuario: dict = Depends(requiere_rol(USUARIO)),
                      db: Session = Depends(get_db)) -> None:
    if datos.autoriza_compartir and not _autorizo_compartir(db, usuario["sub"]):
        raise HTTPException(409, "Primero autoriza compartir tu avance en la sección de privacidad.")
    r = db.execute(text("""UPDATE vinculo SET autoriza_compartir = :a
                           WHERE id_vinculo = :v AND id_usuario = CAST(:u AS uuid) AND fecha_fin IS NULL"""),
                   {"a": datos.autoriza_compartir, "v": id_vinculo, "u": usuario["sub"]})
    if r.rowcount == 0:
        raise HTTPException(404, "Vínculo no encontrado.")
    bitacora(db, usuario["sub"], "vinculo", str(id_vinculo), "compartir" if datos.autoriza_compartir else "dejar_de_compartir")
    db.commit()


@router.delete("/vinculos/{id_vinculo}", status_code=status.HTTP_204_NO_CONTENT)
def terminar_vinculo(id_vinculo: int, usuario: dict = Depends(usuario_actual), db: Session = Depends(get_db)) -> None:
    r = db.execute(text("""UPDATE vinculo SET fecha_fin = now(), autoriza_compartir = FALSE
                           WHERE id_vinculo = :v AND fecha_fin IS NULL
                             AND (id_usuario = CAST(:u AS uuid) OR id_profesional = CAST(:u AS uuid))"""),
                   {"v": id_vinculo, "u": usuario["sub"]})
    if r.rowcount == 0:
        raise HTTPException(404, "Vínculo no encontrado.")
    bitacora(db, usuario["sub"], "vinculo", str(id_vinculo), "terminar")
    db.commit()
