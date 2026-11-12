"""M06 Gamificación (RF-006): reacciona al evento DecisionRegistrada (patrón Observer)."""
from sqlalchemy import text

from app.core.eventos import DecisionRegistrada, suscribir


def _cumple(db, id_usuario: str, regla: str, evento: DecisionRegistrada) -> bool:
    if regla.startswith("casos_completados>="):
        minimo = int(regla.split(">=")[1])
        hechos = db.execute(text("""SELECT count(DISTINCT id_caso) FROM intento
                                    WHERE id_usuario = CAST(:u AS uuid) AND estado = 'finalizado'"""), {"u": id_usuario}).scalar()
        return hechos >= minimo
    if regla == "caso_perfecto":
        if not evento.intento_finalizado:
            return False
        fallos = db.execute(text("SELECT count(*) FROM decision WHERE id_intento = :i AND NOT es_correcta"),
                            {"i": evento.id_intento}).scalar()
        return fallos == 0
    if regla.startswith("ia_erronea_detectada>="):
        minimo = int(regla.split(">=")[1])
        detectados = db.execute(text("""SELECT count(*) FROM decision d JOIN intento i ON i.id_intento = d.id_intento
                                        JOIN etapa e ON e.id_etapa = d.id_etapa
                                        WHERE i.id_usuario = CAST(:u AS uuid) AND e.ia_erronea_intencional AND NOT d.siguio_ia"""),
                               {"u": id_usuario}).scalar()
        return detectados >= minimo
    return False


def al_registrar_decision(evento: DecisionRegistrada) -> dict:
    """RF-006 6.1 (puntaje y nivel) y 6.2 (insignias configurables)."""
    db, u = evento.db, evento.id_usuario
    nivel_antes = db.execute(text("SELECT id_nivel FROM usuario WHERE id_usuario = CAST(:u AS uuid)"), {"u": u}).scalar()
    db.execute(text("""UPDATE usuario SET puntaje_acumulado = puntaje_acumulado + :p,
                              id_nivel = (SELECT id_nivel FROM nivel WHERE puntaje_minimo <= puntaje_acumulado + :p
                                          ORDER BY puntaje_minimo DESC LIMIT 1)
                       WHERE id_usuario = CAST(:u AS uuid)"""), {"p": evento.puntaje, "u": u})
    nivel = db.execute(text("""SELECT n.id_nivel, n.nombre FROM usuario u JOIN nivel n ON n.id_nivel = u.id_nivel
                               WHERE u.id_usuario = CAST(:u AS uuid)"""), {"u": u}).mappings().first()
    nuevas = []
    pendientes = db.execute(text("""SELECT id_insignia, nombre, regla FROM insignia i WHERE regla IS NOT NULL AND NOT EXISTS
                                    (SELECT 1 FROM usuario_insignia ui WHERE ui.id_insignia = i.id_insignia
                                     AND ui.id_usuario = CAST(:u AS uuid))"""), {"u": u}).mappings().all()
    for ins in pendientes:
        if _cumple(db, u, ins["regla"], evento):
            db.execute(text("INSERT INTO usuario_insignia (id_usuario, id_insignia) VALUES (CAST(:u AS uuid), :i)"),
                       {"u": u, "i": ins["id_insignia"]})
            nuevas.append(ins["nombre"])
    subio = nivel is not None and nivel["id_nivel"] != nivel_antes
    return {"nivel_nuevo": nivel["nombre"] if subio else None, "insignias_nuevas": nuevas}


suscribir(DecisionRegistrada, al_registrar_decision)
