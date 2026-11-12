"""Patrón Observer (Interfaz y módulos, sección 6.3).

M05 Evaluación publica DecisionRegistrada; M06 Gamificación y M08 Reportes reaccionan
sin que M05 dependa de ellos.
"""
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session


@dataclass
class DecisionRegistrada:
    db: Session
    id_usuario: str
    id_intento: int
    id_etapa: int
    es_correcta: bool
    siguio_ia: bool
    ia_erronea: bool
    puntaje: int
    intento_finalizado: bool


_suscriptores: dict[type, list[Callable]] = defaultdict(list)


def suscribir(tipo: type, manejador: Callable) -> None:
    if manejador not in _suscriptores[tipo]:
        _suscriptores[tipo].append(manejador)


def publicar(evento: object) -> list:
    return [m(evento) for m in _suscriptores[type(evento)]]
