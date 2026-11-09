"""Rutas del módulo M02 Biblioteca de casos (RF-002): catálogo de casos publicados."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import usuario_actual

router = APIRouter(tags=["Biblioteca de casos"])


@router.get("/casos")
def catalogo(tema: str | None = None, nivel: int | None = None,
             db: Session = Depends(get_db), _: dict = Depends(usuario_actual)) -> list[dict]:
    filas = db.execute(
        text("""SELECT c.id_caso, c.titulo, c.tema, c.nivel_dificultad,
                       (SELECT count(*) FROM etapa e WHERE e.id_caso = c.id_caso) AS etapas
                FROM caso c
                WHERE c.estado = 'publicado' AND NOT c.eliminado
                  AND (CAST(:tema AS text) IS NULL OR c.tema = :tema)
                  AND (CAST(:nivel AS int) IS NULL OR c.nivel_dificultad = :nivel)
                ORDER BY c.nivel_dificultad, c.titulo"""),
        {"tema": tema, "nivel": nivel},
    ).mappings().all()
    return [dict(f) for f in filas]
