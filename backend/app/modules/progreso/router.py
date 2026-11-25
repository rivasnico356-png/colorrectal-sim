"""M08 Reportes (RF-008) y exportación seudonimizada de M07 (RF-007 7.2)."""
import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.deps import ADMIN, PROFESIONAL, USUARIO, requiere_rol
from app.modules.usuarios.service import bitacora

router = APIRouter(tags=["Progreso y reportes"])


def historial(db: Session, id_usuario: str) -> list[dict]:
    filas = db.execute(text("""SELECT i.id_intento, c.titulo, c.tema, i.estado, i.puntaje_total, i.fecha_inicio, i.fecha_fin,
                                      (SELECT count(*) FROM decision d WHERE d.id_intento = i.id_intento AND d.es_correcta) AS aciertos,
                                      (SELECT count(*) FROM decision d WHERE d.id_intento = i.id_intento) AS decisiones
                               FROM intento i JOIN caso c ON c.id_caso = i.id_caso
                               WHERE i.id_usuario = CAST(:u AS uuid) ORDER BY i.fecha_inicio DESC"""), {"u": id_usuario}).mappings()
    return [dict(f) for f in filas]


def progreso(db: Session, id_usuario: str) -> dict:
    perfil = db.execute(text("""SELECT u.puntaje_acumulado, n.nombre AS nivel,
                                       (SELECT min(n2.puntaje_minimo) FROM nivel n2 WHERE n2.puntaje_minimo > u.puntaje_acumulado)
                                       AS siguiente_nivel_desde
                                FROM usuario u LEFT JOIN nivel n ON n.id_nivel = u.id_nivel WHERE u.id_usuario = CAST(:u AS uuid)"""),
                        {"u": id_usuario}).mappings().first()
    t = db.execute(text("""SELECT count(*) AS decisiones, count(*) FILTER (WHERE d.es_correcta) AS aciertos,
                                  count(*) FILTER (WHERE e.ia_erronea_intencional) AS errores_ia,
                                  count(*) FILTER (WHERE e.ia_erronea_intencional AND NOT d.siguio_ia) AS errores_ia_detectados,
                                  avg(d.confianza_declarada / 20.0) FILTER (WHERE d.es_correcta) AS confianza_en_aciertos,
                                  avg(d.confianza_declarada / 20.0) FILTER (WHERE NOT d.es_correcta) AS confianza_en_errores
                           FROM decision d JOIN intento i ON i.id_intento = d.id_intento JOIN etapa e ON e.id_etapa = d.id_etapa
                           WHERE i.id_usuario = CAST(:u AS uuid)"""), {"u": id_usuario}).mappings().first()
    evolucion = db.execute(text("""SELECT i.fecha_fin::date AS fecha, c.titulo, i.puntaje_total FROM intento i
                                   JOIN caso c ON c.id_caso = i.id_caso
                                   WHERE i.id_usuario = CAST(:u AS uuid) AND i.estado = 'finalizado' ORDER BY i.fecha_fin"""),
                           {"u": id_usuario}).mappings().all()
    insignias = db.execute(text("""SELECT i.nombre, i.criterio, ui.fecha_obtencion FROM usuario_insignia ui
                                   JOIN insignia i ON i.id_insignia = ui.id_insignia WHERE ui.id_usuario = CAST(:u AS uuid)
                                   ORDER BY ui.fecha_obtencion"""), {"u": id_usuario}).mappings().all()

    def pct(a, b):
        return round(100 * a / b) if b else None

    ca, ce = t["confianza_en_aciertos"], t["confianza_en_errores"]
    return {
        "puntaje_acumulado": perfil["puntaje_acumulado"], "nivel": perfil["nivel"],
        "siguiente_nivel_desde": perfil["siguiente_nivel_desde"],
        "porcentaje_aciertos": pct(t["aciertos"], t["decisiones"]),
        "tasa_deteccion_errores_ia": pct(t["errores_ia_detectados"], t["errores_ia"]),
        "calibracion": {
            "confianza_en_aciertos": round(float(ca), 1) if ca is not None else None,
            "confianza_en_errores": round(float(ce), 1) if ce is not None else None,
            "explicacion": "Una buena calibración significa que te sientes más seguro cuando aciertas que cuando te equivocas.",
        },
        "evolucion": [dict(e) for e in evolucion],
        "insignias": [dict(i) for i in insignias],
    }


@router.get("/progreso/historial")
def mi_historial(db: Session = Depends(get_db), usuario: dict = Depends(requiere_rol(USUARIO))) -> list[dict]:
    """RF-008 8.1: solo sus propios intentos."""
    return historial(db, usuario["sub"])


@router.get("/progreso")
def mi_progreso(db: Session = Depends(get_db), usuario: dict = Depends(requiere_rol(USUARIO))) -> dict:
    """RF-008 8.2."""
    return progreso(db, usuario["sub"])


CONSENTIDOS = """SELECT v.id_usuario FROM vinculo v JOIN autorizacion_datos a ON a.id_usuario = v.id_usuario
                 AND a.tipo = 'compartir_avance' AND a.aceptada
                 WHERE v.id_profesional = CAST(:p AS uuid) AND v.fecha_fin IS NULL AND v.autoriza_compartir"""


@router.get("/profesional/panel")
def panel(id_caso: int | None = None, db: Session = Depends(get_db), prof: dict = Depends(requiere_rol(PROFESIONAL))) -> dict:
    """RF-008 8.3: indicadores agregados, sin nombres, solo de usuarios vinculados que autorizaron compartir."""
    g = db.execute(text(f"""SELECT count(DISTINCT i.id_usuario) AS usuarios,
                                   round(avg(i.puntaje_total) FILTER (WHERE i.estado = 'finalizado')) AS puntaje_promedio,
                                   count(*) FILTER (WHERE i.estado = 'finalizado') AS casos_completados
                            FROM intento i WHERE i.id_usuario IN ({CONSENTIDOS})
                              AND (CAST(:c AS bigint) IS NULL OR i.id_caso = :c)"""), {"p": prof["sub"], "c": id_caso}).mappings().first()
    por_caso = db.execute(text(f"""SELECT c.id_caso, c.titulo, count(d.*) AS decisiones,
                                          round(100.0 * count(*) FILTER (WHERE d.es_correcta) / nullif(count(d.*), 0)) AS pct_aciertos,
                                          round(100.0 * count(*) FILTER (WHERE d.siguio_ia) / nullif(count(d.*), 0)) AS pct_acepta_ia
                                   FROM decision d JOIN intento i ON i.id_intento = d.id_intento JOIN caso c ON c.id_caso = i.id_caso
                                   WHERE i.id_usuario IN ({CONSENTIDOS}) AND (CAST(:c AS bigint) IS NULL OR c.id_caso = :c)
                                   GROUP BY c.id_caso, c.titulo ORDER BY c.titulo"""), {"p": prof["sub"], "c": id_caso}).mappings().all()
    return dict(g) | {"por_caso": [dict(f) for f in por_caso]}


@router.get("/profesional/usuarios/{id_usuario}/avance")
def avance_individual(id_usuario: str, db: Session = Depends(get_db), prof: dict = Depends(requiere_rol(PROFESIONAL))) -> dict:
    """RF-008 8.4: solo si el usuario autorizó compartir; el acceso queda registrado (quién y cuándo)."""
    autorizado = db.execute(text(f"SELECT 1 FROM ({CONSENTIDOS}) x WHERE x.id_usuario = CAST(:u AS uuid)"),
                            {"p": prof["sub"], "u": id_usuario}).first()
    if not autorizado:
        raise HTTPException(403, "Este usuario no autorizó compartir su avance contigo.")
    bitacora(db, prof["sub"], "avance_individual", id_usuario, "consultar")
    db.commit()
    return {"historial": historial(db, id_usuario), "progreso": progreso(db, id_usuario)}


@router.get("/exportacion/interacciones.csv")
def exportar(id_caso: int | None = None, desde: date | None = None, hasta: date | None = None, db: Session = Depends(get_db),
             quien: dict = Depends(requiere_rol(PROFESIONAL, ADMIN))) -> StreamingResponse:
    """RF-007 7.2: sin nombres ni correos; el profesional solo exporta datos de quienes lo autorizaron."""
    db.execute(text("SELECT set_config('app.sal_seudonimo', :s, true)"), {"s": get_settings().sal_seudonimo})
    filtro = "TRUE" if quien["rol"] == ADMIN else f"i.id_usuario IN ({CONSENTIDOS})"
    filas = db.execute(text(f"""SELECT encode(digest(i.id_usuario::text || coalesce(current_setting('app.sal_seudonimo', true), ''),
                                                    'sha256'), 'hex') AS id_seudonimo,
                                       u.rango_edad, i.id_caso, e.orden AS etapa, o.texto AS decision,
                                       (SELECT texto FROM opcion_decision r WHERE r.id_etapa = e.id_etapa AND r.recomendada_ia)
                                         AS recomendacion_ia,
                                       NOT e.ia_erronea_intencional AS recomendacion_ia_correcta, d.siguio_ia, d.es_correcta,
                                       d.puntaje, d.confianza_declarada / 20 AS confianza_1a5, d.tiempo_respuesta_ms, d.fecha
                                FROM decision d JOIN intento i ON i.id_intento = d.id_intento JOIN etapa e ON e.id_etapa = d.id_etapa
                                JOIN usuario u ON u.id_usuario = i.id_usuario LEFT JOIN opcion_decision o ON o.id_opcion = d.id_opcion
                                WHERE {filtro} AND (CAST(:c AS bigint) IS NULL OR i.id_caso = :c)
                                  AND (CAST(:d AS date) IS NULL OR d.fecha::date >= :d)
                                  AND (CAST(:h AS date) IS NULL OR d.fecha::date <= :h)
                                ORDER BY d.fecha"""),
                       {"p": quien["sub"], "c": id_caso, "d": desde, "h": hasta}).mappings().all()
    salida = io.StringIO()
    columnas = ["id_seudonimo", "rango_edad", "id_caso", "etapa", "decision", "recomendacion_ia", "recomendacion_ia_correcta",
                "siguio_ia", "es_correcta", "puntaje", "confianza_1a5", "tiempo_respuesta_ms", "fecha"]
    escritor = csv.DictWriter(salida, fieldnames=columnas)
    escritor.writeheader()
    escritor.writerows([dict(f) for f in filas])
    bitacora(db, quien["sub"], "exportacion", None, "exportar", {"filas": len(filas)})
    db.commit()
    return StreamingResponse(iter([salida.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=interacciones.csv"})
