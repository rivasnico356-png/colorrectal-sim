"""Rutas del módulo M02 Casos clínicos (RF-002) y catálogo (2.6)."""
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import ADMIN, PROFESIONAL, requiere_rol, usuario_actual
from app.core.errores import ErrorNegocio
from app.modules.casos import service
from app.modules.casos.schemas import CasoIn, EtapaIn, RevisionIn

router = APIRouter(tags=["Casos clínicos"])
EDITORES = requiere_rol(PROFESIONAL, ADMIN)


def _ejecutar(funcion, *args):
    try:
        return funcion(*args)
    except ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e


@router.get("/casos")
def catalogo(tema: str | None = None, nivel: int | None = None, buscar: str | None = None,
             estado: Literal["no_iniciado", "en_curso", "completado"] | None = None,
             db: Session = Depends(get_db), usuario: dict = Depends(usuario_actual)) -> list[dict]:
    """RF-002 2.6: casos publicados con filtros combinables y estado para el usuario actual (RF-006 6.1: bloqueo por nivel)."""
    filas = db.execute(
        text("""SELECT c.id_caso, c.titulo, c.tema, c.nivel_dificultad, c.descripcion,
                       (SELECT count(*) FROM etapa e WHERE e.id_caso = c.id_caso) AS etapas,
                       CASE WHEN EXISTS (SELECT 1 FROM intento i WHERE i.id_caso = c.id_caso
                                           AND i.id_usuario = CAST(:u AS uuid) AND i.estado = 'finalizado') THEN 'completado'
                            WHEN EXISTS (SELECT 1 FROM intento i WHERE i.id_caso = c.id_caso
                                           AND i.id_usuario = CAST(:u AS uuid) AND i.estado = 'en_curso') THEN 'en_curso'
                            ELSE 'no_iniciado' END AS estado_usuario
                FROM caso c
                WHERE c.estado = 'publicado' AND NOT c.eliminado
                  AND (CAST(:tema AS text) IS NULL OR c.tema = :tema)
                  AND (CAST(:nivel AS int) IS NULL OR c.nivel_dificultad = :nivel)
                  AND (CAST(:b AS text) IS NULL OR c.titulo ILIKE '%' || :b || '%' OR c.descripcion ILIKE '%' || :b || '%')
                ORDER BY c.nivel_dificultad, c.titulo"""),
        {"tema": tema, "nivel": nivel, "b": buscar, "u": usuario["sub"]},
    ).mappings().all()
    maximo = service.dificultad_maxima(db, usuario["sub"])
    requisito = service.niveles_por_dificultad(db)
    salida = []
    for f in filas:
        if estado and f["estado_usuario"] != estado:
            continue
        bloqueado = f["nivel_dificultad"] > maximo
        salida.append(dict(f) | {"bloqueado": bloqueado,
                                 "requisito": f"Alcanza el nivel {requisito[f['nivel_dificultad']]}" if bloqueado else None})
    return salida


# ---- Editor de casos para el Profesional de la salud (pantallas 10 y 11) ----

@router.get("/editor/casos")
def mis_casos(db: Session = Depends(get_db), usuario: dict = Depends(EDITORES)) -> list[dict]:
    filas = db.execute(text("""SELECT c.id_caso, c.titulo, c.tema, c.nivel_dificultad, c.estado, a.nombre AS autor,
                                      (c.id_autor = CAST(:u AS uuid)) AS es_autor
                               FROM caso c JOIN usuario a ON a.id_usuario = c.id_autor
                               WHERE NOT c.eliminado ORDER BY c.id_caso DESC"""), {"u": usuario["sub"]}).mappings().all()
    return [dict(f) for f in filas]


@router.get("/editor/casos/{id_caso}")
def ver_caso(id_caso: int, db: Session = Depends(get_db), _: dict = Depends(EDITORES)) -> dict:
    return _ejecutar(service.contenido, db, id_caso)


@router.get("/editor/casos/{id_caso}/versiones")
def versiones(id_caso: int, db: Session = Depends(get_db), _: dict = Depends(EDITORES)) -> list[dict]:
    filas = db.execute(text("""SELECT v.numero, v.fecha, u.nombre AS editor FROM caso_version v
                               JOIN usuario u ON u.id_usuario = v.id_editor WHERE v.id_caso = :c ORDER BY v.numero DESC"""),
                       {"c": id_caso}).mappings().all()
    return [dict(f) for f in filas]


@router.post("/editor/casos", status_code=status.HTTP_201_CREATED)
def crear_caso(datos: CasoIn, db: Session = Depends(get_db), usuario: dict = Depends(requiere_rol(PROFESIONAL))) -> dict:
    """RF-002 2.1: solo el Profesional de la salud crea casos."""
    return {"id_caso": _ejecutar(service.crear_caso, db, usuario["sub"], datos)}


@router.put("/editor/casos/{id_caso}", status_code=status.HTTP_204_NO_CONTENT)
def editar_caso(id_caso: int, datos: CasoIn, db: Session = Depends(get_db), usuario: dict = Depends(requiere_rol(PROFESIONAL))) -> None:
    _ejecutar(service.editar_caso, db, usuario["sub"], id_caso, datos)


@router.put("/editor/casos/{id_caso}/etapas", status_code=status.HTTP_201_CREATED)
def guardar_etapa(id_caso: int, datos: EtapaIn, db: Session = Depends(get_db),
                  usuario: dict = Depends(requiere_rol(PROFESIONAL))) -> dict:
    return {"id_etapa": _ejecutar(service.guardar_etapa, db, usuario["sub"], id_caso, datos)}


@router.post("/editor/etapas/{id_etapa}/recursos", status_code=status.HTTP_201_CREATED)
async def subir_recurso(id_etapa: int, archivo: UploadFile = File(...), id_dataset: int = Form(...), licencia: str = Form(...),
                        db: Session = Depends(get_db), usuario: dict = Depends(requiere_rol(PROFESIONAL))) -> dict:
    datos = await archivo.read()
    return {"id_recurso": _ejecutar(service.guardar_recurso, db, usuario["sub"], id_etapa, archivo.filename or "", datos,
                                    id_dataset, licencia)}


@router.post("/editor/casos/{id_caso}/revision")
def revisar(id_caso: int, datos: RevisionIn, db: Session = Depends(get_db), usuario: dict = Depends(requiere_rol(PROFESIONAL))) -> dict:
    return {"estado": _ejecutar(service.revisar, db, usuario["sub"], id_caso, datos.accion, datos.fuente_clinica)}


@router.delete("/editor/casos/{id_caso}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_caso(id_caso: int, db: Session = Depends(get_db), usuario: dict = Depends(EDITORES)) -> None:
    _ejecutar(service.eliminar_caso, db, usuario["sub"], id_caso)


@router.get("/datasets")
def datasets(db: Session = Depends(get_db), _: dict = Depends(usuario_actual)) -> list[dict]:
    filas = db.execute(text("SELECT id_dataset, nombre, fuente_url, licencia, modalidad FROM dataset ORDER BY id_dataset")).mappings()
    return [dict(f) for f in filas]
