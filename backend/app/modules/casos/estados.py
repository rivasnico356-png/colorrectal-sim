"""Patrón State (1.3.2.2, sección 4): ciclo de vida del caso clínico Borrador → Revisado → Publicado (RF-002 2.5).

CasoClinico delega cada acción en su objeto EstadoCaso. Cada estado concreto implementa solo sus transiciones
válidas; las demás lanzan un error de negocio (409). EstadoBorrador.marcar_revisado valida que el revisor sea un
Profesional de la salud distinto del autor y registra la fuente clínica; la base lo refuerza con la restricción
CHECK ck_caso_3.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.errores import ErrorNegocio


class EstadoCaso:
    nombre = ""

    def marcar_revisado(self, caso: "CasoClinico", revisor: str, fuente_clinica: str | None) -> None:
        raise ErrorNegocio("Solo se aprueban casos en borrador.", 409)

    def publicar(self, caso: "CasoClinico") -> None:
        raise ErrorNegocio("Solo se publican casos revisados.", 409)

    def devolver(self, caso: "CasoClinico", observacion: str | None = None) -> None:
        """Cualquier estado puede volver a Borrador para corregir el caso."""
        caso.db.execute(text("""UPDATE caso SET estado = 'borrador', id_revisor = NULL, fecha_revision = NULL,
                                   fecha_publicacion = NULL WHERE id_caso = :c"""), {"c": caso.id_caso})
        caso.estado = EstadoBorrador()


class EstadoBorrador(EstadoCaso):
    nombre = "borrador"

    def marcar_revisado(self, caso: "CasoClinico", revisor: str, fuente_clinica: str | None) -> None:
        if revisor == caso.id_autor:
            raise ErrorNegocio("El revisor debe ser distinto al autor del caso.", 403)
        if not (fuente_clinica and fuente_clinica.strip()):
            raise ErrorNegocio("Registra la fuente clínica de respaldo.", 422)
        etapas_validas = caso.db.execute(text("""SELECT count(*) FROM etapa e WHERE e.id_caso = :c AND EXISTS
                                                 (SELECT 1 FROM opcion_decision o WHERE o.id_etapa = e.id_etapa AND o.es_correcta)"""),
                                         {"c": caso.id_caso}).scalar()
        if not etapas_validas:
            raise ErrorNegocio("El caso necesita al menos una etapa con solución esperada.", 422)
        caso.db.execute(text("""UPDATE caso SET estado = 'revisado', id_revisor = CAST(:r AS uuid), fuente_clinica = :f,
                                   fecha_revision = now() WHERE id_caso = :c"""),
                        {"r": revisor, "f": fuente_clinica, "c": caso.id_caso})
        caso.estado = EstadoRevisado()


class EstadoRevisado(EstadoCaso):
    nombre = "revisado"

    def publicar(self, caso: "CasoClinico") -> None:
        caso.db.execute(text("UPDATE caso SET estado = 'publicado', fecha_publicacion = now() WHERE id_caso = :c"),
                        {"c": caso.id_caso})
        caso.estado = EstadoPublicado()


class EstadoPublicado(EstadoCaso):
    nombre = "publicado"


ESTADOS: dict[str, type[EstadoCaso]] = {e.nombre: e for e in (EstadoBorrador, EstadoRevisado, EstadoPublicado)}


def estado_de(nombre: str) -> EstadoCaso:
    return ESTADOS[nombre]()


class CasoClinico:
    """Contexto del patrón State: guarda el estado actual y le delega las acciones de revisión."""

    def __init__(self, db: Session, id_caso: int, id_autor: str, estado: str):
        self.db, self.id_caso, self.id_autor = db, id_caso, id_autor
        self.estado: EstadoCaso = estado_de(estado)

    def marcar_revisado(self, revisor: str, fuente_clinica: str | None) -> None:
        self.estado.marcar_revisado(self, revisor, fuente_clinica)

    def publicar(self) -> None:
        self.estado.publicar(self)

    def devolver(self, observacion: str | None = None) -> None:
        self.estado.devolver(self, observacion)

    def ejecutar(self, accion: str, revisor: str, fuente_clinica: str | None) -> str:
        """Traduce la acción de la API (aprobar, publicar o devolver) a la operación del estado."""
        if accion == "aprobar":
            self.marcar_revisado(revisor, fuente_clinica)
        elif accion == "publicar":
            self.publicar()
        elif accion == "devolver":
            self.devolver(fuente_clinica)
        else:
            raise ErrorNegocio("Acción de revisión no válida.", 422)
        return self.estado.nombre
