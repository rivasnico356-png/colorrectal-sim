"""Observadores de DecisionRegistrada de M07 Interacción humano-IA y M08 Progreso (patrón Observer)."""
from sqlalchemy import text

from app.core.eventos import DecisionRegistrada, suscribir


class ObsInteraccionIA:
    """RF-007 7.1: guarda la decisión con la confianza declarada y si siguió o no la sugerencia de la IA."""

    def __call__(self, evento: DecisionRegistrada) -> None:
        evento.db.execute(text("""INSERT INTO decision (id_intento, id_etapa, id_opcion, confianza_declarada, siguio_ia, es_correcta,
                                                        puntaje, tiempo_respuesta_ms)
                                  VALUES (:i, :e, :o, :c, :s, :k, :p, :t)"""),
                          {"i": evento.id_intento, "e": evento.id_etapa, "o": evento.id_opcion, "c": (evento.confianza or 0) * 20,
                           "s": evento.siguio_ia, "k": evento.es_correcta, "p": evento.puntaje, "t": evento.tiempo_ms})


class ObsProgreso:
    """RF-008: cuando no quedan etapas sin responder, cierra el intento con su puntaje total."""

    def __call__(self, evento: DecisionRegistrada) -> dict:
        pendientes = evento.db.execute(text("""SELECT count(*) FROM etapa e WHERE e.id_caso = :c AND NOT EXISTS
                                               (SELECT 1 FROM decision d WHERE d.id_intento = :i AND d.id_etapa = e.id_etapa)"""),
                                       {"c": evento.id_caso, "i": evento.id_intento}).scalar()
        if pendientes == 0:
            evento.db.execute(text("""UPDATE intento SET estado = 'finalizado', fecha_fin = now(),
                                         puntaje_total = (SELECT coalesce(sum(puntaje), 0) FROM decision WHERE id_intento = :i)
                                      WHERE id_intento = :i"""), {"i": evento.id_intento})
            evento.intento_finalizado = True
        return {"intento_finalizado": evento.intento_finalizado}


obs_interaccion = ObsInteraccionIA()
obs_progreso = ObsProgreso()
suscribir(DecisionRegistrada, obs_interaccion, orden=10)
suscribir(DecisionRegistrada, obs_progreso, orden=20)
