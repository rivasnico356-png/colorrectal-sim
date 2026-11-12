"""M03 Simulación, M05 Evaluación y M07 Interacción humano-IA (RF-003, RF-004 4.1 y 4.4, RF-005, RF-007)."""
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errores import ErrorNegocio
from app.core.eventos import DecisionRegistrada, publicar
from app.core.textos import AVISO_ALCANCE, ROTULO_IA
from app.modules.casos.service import dificultad_maxima, niveles_por_dificultad
from app.modules.estudios.vision import obtener_modelo


def _intento(db: Session, id_usuario: str, id_intento: int) -> dict:
    fila = db.execute(text("""SELECT i.*, c.titulo, c.descripcion, c.contexto_simulado FROM intento i
                              JOIN caso c ON c.id_caso = i.id_caso
                              WHERE i.id_intento = :i AND i.id_usuario = CAST(:u AS uuid)"""),
                      {"i": id_intento, "u": id_usuario}).mappings().first()
    if fila is None:
        raise ErrorNegocio("Intento no encontrado.", 404)
    return dict(fila)


def aviso() -> dict:
    return {"aviso": AVISO_ALCANCE}


def iniciar(db: Session, id_usuario: str, id_caso: int, acepto_aviso: bool) -> dict:
    """RF-003 3.1: crea el intento tras aceptar el aviso de alcance. 3.6: si hay uno en curso, se retoma."""
    caso = db.execute(text("SELECT nivel_dificultad FROM caso WHERE id_caso = :c AND estado = 'publicado' AND NOT eliminado"),
                      {"c": id_caso}).scalar()
    if caso is None:
        raise ErrorNegocio("Caso no disponible.", 404)
    if caso > dificultad_maxima(db, id_usuario):
        raise ErrorNegocio(f"Caso bloqueado. Alcanza el nivel {niveles_por_dificultad(db)[caso]} para desbloquearlo.", 403)
    en_curso = db.execute(text("""SELECT id_intento FROM intento WHERE id_usuario = CAST(:u AS uuid) AND id_caso = :c
                                  AND estado = 'en_curso' ORDER BY fecha_inicio DESC LIMIT 1"""),
                          {"u": id_usuario, "c": id_caso}).scalar()
    if en_curso:
        return {"id_intento": en_curso, "retomado": True}
    if not acepto_aviso:
        raise ErrorNegocio("Debes aceptar el aviso de alcance para iniciar el caso.", 422)
    id_intento = db.execute(text("""INSERT INTO intento (id_usuario, id_caso, aviso_aceptado)
                                    VALUES (CAST(:u AS uuid), :c, TRUE) RETURNING id_intento"""),
                            {"u": id_usuario, "c": id_caso}).scalar_one()
    db.commit()
    return {"id_intento": id_intento, "retomado": False}


def _etapa_actual(db: Session, id_intento: int, id_caso: int) -> dict | None:
    """RF-003 3.2: la primera etapa, en orden, que aún no tiene decisión."""
    fila = db.execute(text("""SELECT e.* FROM etapa e WHERE e.id_caso = :c AND NOT EXISTS
                              (SELECT 1 FROM decision d WHERE d.id_intento = :i AND d.id_etapa = e.id_etapa)
                              ORDER BY e.orden LIMIT 1"""), {"c": id_caso, "i": id_intento}).mappings().first()
    return dict(fila) if fila else None


def consultas_usadas(db: Session, id_intento: int, id_etapa: int) -> int:
    return db.execute(text("""SELECT count(*) FROM interaccion_ia WHERE id_intento = :i AND id_etapa = :e AND tipo = 'respuesta'"""),
                      {"i": id_intento, "e": id_etapa}).scalar()


def estado(db: Session, id_usuario: str, id_intento: int) -> dict:
    intento = _intento(db, id_usuario, id_intento)
    total = db.execute(text("SELECT count(*) FROM etapa WHERE id_caso = :c"), {"c": intento["id_caso"]}).scalar()
    respondidas = db.execute(text("SELECT count(*) FROM decision WHERE id_intento = :i"), {"i": id_intento}).scalar()
    salida = {"id_intento": id_intento, "id_caso": intento["id_caso"], "titulo": intento["titulo"],
              "descripcion": intento["descripcion"], "contexto_simulado": intento["contexto_simulado"],
              "estado": intento["estado"], "progreso": {"actual": min(respondidas + 1, total), "total": total},
              "etapa": None}
    etapa = _etapa_actual(db, id_intento, intento["id_caso"]) if intento["estado"] == "en_curso" else None
    if etapa is None:
        return salida
    opciones = db.execute(text("SELECT id_opcion, texto, recomendada_ia FROM opcion_decision WHERE id_etapa = :e ORDER BY id_opcion"),
                          {"e": etapa["id_etapa"]}).mappings().all()
    recursos = db.execute(text("""SELECT r.tipo, '/media/' || r.ruta_almacenamiento AS url, r.ruta_almacenamiento, r.licencia,
                                         d.nombre AS dataset, d.fuente_url
                                  FROM recurso_multimedia r LEFT JOIN dataset d ON d.id_dataset = r.id_dataset
                                  WHERE r.id_etapa = :e ORDER BY r.id_recurso"""), {"e": etapa["id_etapa"]}).mappings().all()
    recomendada = next((o for o in opciones if o["recomendada_ia"]), None)
    # RF-004 4.1 y RF-007: la recomendación configurada se muestra antes de decidir y queda registrada una vez.
    ya = db.execute(text("""SELECT 1 FROM interaccion_ia WHERE id_intento = :i AND id_etapa = :e AND tipo = 'recomendacion'
                            AND proveedor = 'predefinida'"""), {"i": id_intento, "e": etapa["id_etapa"]}).first()
    if not ya:
        db.execute(text("""INSERT INTO interaccion_ia (id_intento, id_etapa, tipo, proveedor, version_modelo, consulta, respuesta)
                           VALUES (:i, :e, 'recomendacion', 'predefinida', 'configurada', 'recomendacion de la etapa', :r)"""),
                   {"i": id_intento, "e": etapa["id_etapa"], "r": etapa["recomendacion_ia"]})
        db.commit()
    maximo = get_settings().tutor_max_consultas_etapa
    salida["etapa"] = {
        "id_etapa": etapa["id_etapa"], "orden": etapa["orden"], "enunciado": etapa["enunciado"],
        "recursos": [{k: v for k, v in r.items() if k != "ruta_almacenamiento"} for r in recursos],
        "opciones": [{"id_opcion": o["id_opcion"], "texto": o["texto"]} for o in opciones],
        "recomendacion_ia": {"texto": etapa["recomendacion_ia"], "id_opcion": recomendada["id_opcion"] if recomendada else None,
                             "rotulo": ROTULO_IA},
        "modelo_vision": _vision_etapa(recursos) if etapa["usa_modelo_vision"] else None,
        "tutor": {"consultas_restantes": max(0, maximo - consultas_usadas(db, id_intento, etapa["id_etapa"])), "maximo": maximo},
    }
    return salida


def _vision_etapa(recursos) -> dict:
    """RF-003 3.4: región de interés, clasificación experimental y confianza del modelo sobre la imagen de la etapa."""
    modelo = obtener_modelo()
    imagen = next((r for r in recursos if r["tipo"] == "imagen"), None)
    archivo = Path(get_settings().media_dir) / imagen["ruta_almacenamiento"] if imagen else None
    if modelo is None or archivo is None or not archivo.exists():
        return {"disponible": False}
    r = modelo.analizar(archivo.read_bytes())
    return {"disponible": True, "roi": r.roi, "clasificacion": r.clasificacion, "confianza": r.confianza,
            "version_modelo": r.version_modelo, "rotulo": ROTULO_IA,
            "que_significa": "La confianza indica qué tan parecido es lo que ve el modelo a los ejemplos con que fue entrenado; "
                             "no es una probabilidad de enfermedad."}


def decidir(db: Session, id_usuario: str, id_intento: int, id_etapa: int, id_opcion: int, confianza: int,
            tiempo_ms: int | None) -> dict:
    """RF-003 3.5, RF-004 4.4, RF-005 5.1–5.3 y RF-007 7.1."""
    intento = _intento(db, id_usuario, id_intento)
    if intento["estado"] != "en_curso":
        raise ErrorNegocio("Este intento ya terminó.", 409)
    actual = _etapa_actual(db, id_intento, intento["id_caso"])
    if actual is None or actual["id_etapa"] != id_etapa:
        raise ErrorNegocio("Responde la etapa actual antes de avanzar.", 409)
    elegida = db.execute(text("SELECT * FROM opcion_decision WHERE id_opcion = :o AND id_etapa = :e"),
                         {"o": id_opcion, "e": id_etapa}).mappings().first()
    if elegida is None:
        raise ErrorNegocio("La opción no pertenece a esta etapa.", 422)
    correcta = db.execute(text("SELECT * FROM opcion_decision WHERE id_etapa = :e AND es_correcta"), {"e": id_etapa}).mappings().first()
    resultado = "correcto" if elegida["es_correcta"] else ("parcial" if elegida["puntaje"] > 0 else "incorrecto")
    puntaje = elegida["puntaje"]
    siguio_ia = bool(elegida["recomendada_ia"])
    db.execute(text("""INSERT INTO decision (id_intento, id_etapa, id_opcion, confianza_declarada, siguio_ia, es_correcta, puntaje,
                                             tiempo_respuesta_ms)
                       VALUES (:i, :e, :o, :c, :s, :k, :p, :t)"""),
               {"i": id_intento, "e": id_etapa, "o": id_opcion, "c": confianza * 20, "s": siguio_ia,
                "k": bool(elegida["es_correcta"]), "p": puntaje, "t": tiempo_ms})
    finalizado = _etapa_actual(db, id_intento, intento["id_caso"]) is None
    if finalizado:
        db.execute(text("""UPDATE intento SET estado = 'finalizado', fecha_fin = now(),
                                  puntaje_total = (SELECT coalesce(sum(puntaje), 0) FROM decision WHERE id_intento = :i)
                           WHERE id_intento = :i"""), {"i": id_intento})
    efectos = publicar(DecisionRegistrada(db, id_usuario, id_intento, id_etapa, bool(elegida["es_correcta"]), siguio_ia,
                                          bool(actual["ia_erronea_intencional"]), puntaje, finalizado))
    db.commit()
    extra = {"nivel_nuevo": None, "insignias_nuevas": []}
    for e in efectos:
        if isinstance(e, dict):
            extra["nivel_nuevo"] = extra["nivel_nuevo"] or e.get("nivel_nuevo")
            extra["insignias_nuevas"] += e.get("insignias_nuevas", [])
    ia_erronea = bool(actual["ia_erronea_intencional"])
    return {
        "resultado": resultado, "puntaje": puntaje,
        "respuesta_esperada": correcta["texto"] if correcta else None,
        "explicacion": correcta["retroalimentacion"] if correcta else None,
        "fuente": correcta["fuente"] if correcta else None,
        "explicacion_de_tu_opcion": None if elegida["es_correcta"] else elegida["retroalimentacion"],
        "siguio_ia": siguio_ia,
        "ia_estaba_equivocada": ia_erronea,
        "detectaste_error_ia": ia_erronea and not siguio_ia,
        "intento_finalizado": finalizado,
    } | extra


def resumen(db: Session, id_usuario: str, id_intento: int) -> dict:
    """RF-005 5.4: resumen al completar la última etapa; los datos salen del intento registrado."""
    intento = _intento(db, id_usuario, id_intento)
    if intento["estado"] != "finalizado":
        raise ErrorNegocio("El resumen está disponible al terminar el caso.", 409)
    decisiones = db.execute(text("""SELECT e.orden, d.es_correcta, d.puntaje, d.siguio_ia, e.ia_erronea_intencional,
                                           d.confianza_declarada / 20 AS confianza, d.tiempo_respuesta_ms
                                    FROM decision d JOIN etapa e ON e.id_etapa = d.id_etapa
                                    WHERE d.id_intento = :i ORDER BY e.orden"""), {"i": id_intento}).mappings().all()
    duracion = (intento["fecha_fin"] - intento["fecha_inicio"]).total_seconds()
    return {
        "id_intento": id_intento, "titulo": intento["titulo"], "puntaje_total": intento["puntaje_total"],
        "aciertos": sum(d["es_correcta"] for d in decisiones), "etapas": len(decisiones),
        "tiempo_segundos": round(duracion),
        "siguio_ia": sum(d["siguio_ia"] for d in decisiones),
        "rechazo_ia": sum(not d["siguio_ia"] for d in decisiones),
        "errores_ia": sum(d["ia_erronea_intencional"] for d in decisiones),
        "errores_ia_detectados": sum(d["ia_erronea_intencional"] and not d["siguio_ia"] for d in decisiones),
        "decisiones": [dict(d) for d in decisiones],
    }
