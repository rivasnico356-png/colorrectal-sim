"""Rutas del módulo M04 Agente tutor de IA (RF-004) con registro de cada interacción (RF-007, RNF-007)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.deps import USUARIO, requiere_rol
from app.core.textos import ROTULO_IA
from app.modules.simulacion.service import consultas_usadas
from app.modules.tutor.prompt import VERSION_PROMPT
from app.modules.tutor.servicio import crear_servicio

router = APIRouter(tags=["Agente tutor de IA"])


class ConsultaTutor(BaseModel):
    pregunta: str | None = Field(default=None, min_length=2, max_length=500)


@router.post("/intentos/{id_intento}/etapas/{id_etapa}/tutor")
def consultar(id_intento: int, id_etapa: int, consulta: ConsultaTutor, db: Session = Depends(get_db),
              usuario: dict = Depends(requiere_rol(USUARIO))) -> dict:
    """Sin pregunta: explica la sugerencia de la etapa (4.2). Con pregunta: consulta conversacional con límite (4.3)."""
    fila = db.execute(text("""SELECT e.enunciado, e.recomendacion_ia, c.contexto_simulado,
                                     (SELECT texto FROM opcion_decision o WHERE o.id_etapa = e.id_etapa AND o.recomendada_ia) AS opcion
                              FROM intento i JOIN caso c ON c.id_caso = i.id_caso JOIN etapa e ON e.id_caso = c.id_caso
                              WHERE i.id_intento = :i AND i.id_usuario = CAST(:u AS uuid) AND e.id_etapa = :e"""),
                      {"i": id_intento, "u": usuario["sub"], "e": id_etapa}).mappings().first()
    if fila is None:
        raise HTTPException(404, "Etapa no encontrada en este intento.")
    maximo = get_settings().tutor_max_consultas_etapa
    usadas = consultas_usadas(db, id_intento, id_etapa)
    if consulta.pregunta and usadas >= maximo:
        raise HTTPException(429, f"Ya usaste las {maximo} preguntas de esta etapa.")
    recomendacion = fila["recomendacion_ia"] + (f" (opción sugerida: {fila['opcion']})" if fila["opcion"] else "")
    servicio = crear_servicio()
    r = servicio.explicar(fila["enunciado"], recomendacion, fila["recomendacion_ia"], consulta.pregunta,
                          contexto_caso=fila["contexto_simulado"])
    tipo = "respuesta" if consulta.pregunta else "recomendacion"
    db.execute(text("""INSERT INTO interaccion_ia (id_intento, id_etapa, tipo, proveedor, version_modelo, version_prompt,
                                                   consulta, respuesta, latencia_ms)
                       VALUES (:i, :e, :t, :p, :m, :v, :c, :r, :l)"""),
               {"i": id_intento, "e": id_etapa, "t": tipo, "p": r.proveedor, "m": r.version_modelo, "v": VERSION_PROMPT,
                "c": consulta.pregunta or "explicar sugerencia", "r": r.texto, "l": r.latencia_ms})
    db.commit()
    restantes = maximo - usadas - (1 if consulta.pregunta else 0)
    return {"texto": r.texto, "proveedor": r.proveedor, "version_modelo": r.version_modelo, "version_prompt": VERSION_PROMPT,
            "latencia_ms": r.latencia_ms, "rotulo": ROTULO_IA, "consultas_restantes": max(0, restantes),
            "aviso": "El tutor no respondió; se muestra la explicación preparada para la etapa." if r.proveedor == "predefinida" else None}
