"""Patrón Observer (Patrones de diseño 1.3.2.2, sección 5).

M05 Evaluación publica DecisionRegistrada y no conoce a sus observadores. Se suscriben, en este orden:
1. ObsInteraccionIA (M07): registra la decisión humano-IA (RF-007 7.1).
2. ObsProgreso (M08): cierra el intento cuando no quedan etapas (RF-008).
3. ObsGamificacion (M06): puntaje, nivel e insignias (RF-006).
Todos corren en la misma transacción (ADR-05); el orden se fija con `orden` porque la gamificación necesita
saber si el intento terminó.
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
    intento_finalizado: bool = False
    id_caso: int | None = None
    id_opcion: int | None = None
    confianza: int | None = None        # declarada de 1 a 5 (se guarda de 0 a 100)
    tiempo_ms: int | None = None


class BusEventos:
    """Bus de eventos de dominio en proceso: guarda los observadores de cada tipo de evento en orden."""

    def __init__(self):
        self._suscriptores: dict[type, list[tuple[int, Callable]]] = defaultdict(list)

    def suscribir(self, tipo: type, observador: Callable, orden: int = 50) -> None:
        if all(m is not observador for _, m in self._suscriptores[tipo]):
            self._suscriptores[tipo].append((orden, observador))
            self._suscriptores[tipo].sort(key=lambda par: par[0])

    def suscriptores(self, tipo: type) -> list[Callable]:
        return [m for _, m in self._suscriptores[tipo]]

    def publicar(self, evento: object) -> list:
        return [m(evento) for m in self.suscriptores(type(evento))]


bus = BusEventos()


def suscribir(tipo: type, manejador: Callable, orden: int = 50) -> None:
    bus.suscribir(tipo, manejador, orden)


def suscriptores(tipo: type) -> list[Callable]:
    return bus.suscriptores(tipo)


def publicar(evento: object) -> list:
    return bus.publicar(evento)
