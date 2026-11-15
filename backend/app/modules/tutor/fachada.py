"""Patrón Facade (1.3.2.2, sección 3): una sola entrada al subsistema del tutor (RF-004, RF-007, RNF-007).

El router de la API solo llama a FachadaTutor.consultar. Por dentro, la fachada arma el contexto sin datos personales,
pasa la pregunta por la cadena de validación (Chain of Responsibility), pide la respuesta al servicio con respaldo
(Strategy + Adapter + Factory Method), la rotula y registra la interacción. Así ninguna salida de la IA llega a la
persona sin rótulo ni registro.
"""
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errores import ErrorNegocio
from app.core.textos import ROTULO_IA
from app.modules.simulacion.service import consultas_usadas
from app.modules.tutor.prompt import VERSION_PROMPT
from app.modules.tutor.servicio import ServicioTutor, crear_servicio
from app.modules.tutor.validacion import Consulta, ConsultaRechazada, Validador, crear_cadena


@dataclass
class ContextoEtapa:
    enunciado: str
    recomendacion_ia: str
    opcion_sugerida: str | None
    contexto_caso: str | None


class ConstructorContexto:
    """Lee de la base solo lo que el tutor necesita del caso; nunca datos de la persona (IE-02)."""

    def armar(self, db: Session, id_intento: int, id_etapa: int, id_usuario: str) -> ContextoEtapa:
        fila = db.execute(text("""SELECT e.enunciado, e.recomendacion_ia, c.contexto_simulado,
                                         (SELECT texto FROM opcion_decision o WHERE o.id_etapa = e.id_etapa AND o.recomendada_ia) AS opcion
                                  FROM intento i JOIN caso c ON c.id_caso = i.id_caso JOIN etapa e ON e.id_caso = c.id_caso
                                  WHERE i.id_intento = :i AND i.id_usuario = CAST(:u AS uuid) AND e.id_etapa = :e"""),
                          {"i": id_intento, "u": id_usuario, "e": id_etapa}).mappings().first()
        if fila is None:
            raise ErrorNegocio("Etapa no encontrada en este intento.", 404)
        return ContextoEtapa(fila["enunciado"], fila["recomendacion_ia"], fila["opcion"], fila["contexto_simulado"])


class FachadaTutor:
    def __init__(self, servicio: ServicioTutor | None = None, validacion: Validador | None = None,
                 contexto: ConstructorContexto | None = None, maximo: int | None = None):
        self.servicio = servicio or crear_servicio()
        self.validacion = validacion or crear_cadena()
        self.contexto = contexto or ConstructorContexto()
        self.maximo = maximo if maximo is not None else get_settings().tutor_max_consultas_etapa

    def consultar(self, db: Session, id_intento: int, id_etapa: int, id_usuario: str, pregunta: str | None) -> dict:
        etapa = self.contexto.armar(db, id_intento, id_etapa, id_usuario)
        usadas = consultas_usadas(db, id_intento, id_etapa)
        try:
            self.validacion.validar(Consulta(pregunta, usadas, self.maximo))
        except ConsultaRechazada as r:
            if not r.es_guia:
                raise ErrorNegocio(r.mensaje, r.codigo) from r
            # Respuesta guía: no se llamó a la IA, no gasta pregunta y no se registra como interacción con la IA.
            return {"texto": r.mensaje, "proveedor": "validacion", "version_modelo": "-", "version_prompt": VERSION_PROMPT,
                    "latencia_ms": 0, "rotulo": None, "consultas_restantes": max(0, self.maximo - usadas),
                    "aviso": "Tu pregunta no se envió al tutor."}
        recomendacion = etapa.recomendacion_ia + (f" (opción sugerida: {etapa.opcion_sugerida})" if etapa.opcion_sugerida else "")
        r = self.servicio.explicar(etapa.enunciado, recomendacion, etapa.recomendacion_ia, pregunta,
                                   contexto_caso=etapa.contexto_caso)
        self._registrar(db, id_intento, id_etapa, pregunta, r)
        restantes = self.maximo - usadas - (1 if pregunta else 0)
        return {"texto": r.texto, "proveedor": r.proveedor, "version_modelo": r.version_modelo, "version_prompt": VERSION_PROMPT,
                "latencia_ms": r.latencia_ms, "rotulo": ROTULO_IA, "consultas_restantes": max(0, restantes),
                "aviso": "El tutor no respondió; se muestra la explicación preparada para la etapa."
                if r.proveedor == "predefinida" else None}

    @staticmethod
    def _registrar(db: Session, id_intento: int, id_etapa: int, pregunta: str | None, r) -> None:
        """RF-007 y RNF-007: cada salida queda con proveedor, versión del modelo, versión del prompt y latencia."""
        db.execute(text("""INSERT INTO interaccion_ia (id_intento, id_etapa, tipo, proveedor, version_modelo, version_prompt,
                                                       consulta, respuesta, latencia_ms)
                           VALUES (:i, :e, :t, :p, :m, :v, :c, :r, :l)"""),
                   {"i": id_intento, "e": id_etapa, "t": "respuesta" if pregunta else "recomendacion", "p": r.proveedor,
                    "m": r.version_modelo, "v": VERSION_PROMPT, "c": pregunta or "explicar sugerencia", "r": r.texto,
                    "l": r.latencia_ms})
        db.commit()
