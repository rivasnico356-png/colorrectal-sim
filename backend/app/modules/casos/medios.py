"""Publica las imágenes y videos de los casos guardados en la base (RF-002 2.2, RF-003 3.3).

Los recursos vienen de datasets públicos, por eso se sirven sin sesión, igual que antes desde la carpeta /media.
Admite peticiones parciales (Range) para que el visor de video pueda avanzar cuadro a cuadro.
"""
import re

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db

router = APIRouter(tags=["Casos"])
RANGO = re.compile(r"bytes=(\d*)-(\d*)$")


def contenido(db: Session, id_recurso: int) -> dict | None:
    fila = db.execute(text("SELECT tipo_mime, sha256, datos FROM recurso_contenido WHERE id_recurso = :i"),
                      {"i": id_recurso}).mappings().first()
    return dict(fila) if fila else None


def bytes_de_ruta(db: Session, ruta: str) -> bytes | None:
    """Contenido de un recurso a partir de su ruta de almacenamiento (recursos/<id>.<ext>)."""
    m = re.fullmatch(r"recursos/(\d+)\.\w+", ruta or "")
    fila = contenido(db, int(m.group(1))) if m else None
    return bytes(fila["datos"]) if fila else None


@router.get("/media/recursos/{nombre}", include_in_schema=False)
def servir(nombre: str, rango: str | None = Header(None, alias="Range"), db: Session = Depends(get_db)) -> Response:
    m = re.fullmatch(r"(\d+)\.(jpg|jpeg|png|mp4)", nombre.lower())
    fila = contenido(db, int(m.group(1))) if m else None
    if fila is None:
        raise HTTPException(404, "Recurso no encontrado.")
    datos = bytes(fila["datos"])
    total = len(datos)
    cabeceras = {"Accept-Ranges": "bytes", "ETag": f'"{fila["sha256"]}"', "Cache-Control": "public, max-age=86400"}
    r = RANGO.match(rango or "")
    if not r or (not r.group(1) and not r.group(2)):
        return Response(datos, media_type=fila["tipo_mime"], headers=cabeceras)
    if r.group(1):
        inicio = int(r.group(1))
        fin = min(int(r.group(2)), total - 1) if r.group(2) else total - 1
    else:  # bytes=-N: los últimos N bytes
        inicio, fin = max(0, total - int(r.group(2))), total - 1
    if inicio >= total or inicio > fin:
        return Response(status_code=416, headers={"Content-Range": f"bytes */{total}"})
    cabeceras["Content-Range"] = f"bytes {inicio}-{fin}/{total}"
    return Response(datos[inicio:fin + 1], status_code=206, media_type=fila["tipo_mime"], headers=cabeceras)
