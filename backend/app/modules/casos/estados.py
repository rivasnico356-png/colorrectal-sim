"""Patrón State (1.3.2.2, sección 4): ciclo de vida del caso clínico Borrador → Revisado → Publicado (RF-002 2.5).

Cada estado es una clase que implementa solo sus transiciones válidas; una transición no permitida lanza un error
de negocio (409). La regla «el revisor es un Profesional de la salud distinto del autor» se valida antes de cualquier
transición en service.revisar y también con la restricción CHECK de la tabla caso.
"""
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.errores import ErrorNegocio


@dataclass
class ContextoRevision:
    db: Session
    id_caso: int
    revisor: str
    fuente_clinica: str | None


class EstadoCaso:
    nombre = ""

    def aprobar(self, ctx: ContextoRevision) -> "EstadoCaso":
        raise ErrorNegocio("Solo se aprueban casos en borrador.", 409)

    def publicar(self, ctx: ContextoRevision) -> "EstadoCaso":
        raise ErrorNegocio("Solo se publican casos revisados.", 409)

    def devolver(self, ctx: ContextoRevision) -> "EstadoCaso":
        """Cualquier estado puede volver a Borrador para corregir el caso."""
        ctx.db.execute(text("""UPDATE caso SET estado = 'borrador', id_revisor = NULL, fecha_revision = NULL,
                                  fecha_publicacion = NULL WHERE id_caso = :c"""), {"c": ctx.id_caso})
        return EstadoBorrador()


class EstadoBorrador(EstadoCaso):
    nombre = "borrador"

    def aprobar(self, ctx: ContextoRevision) -> EstadoCaso:
        if not (ctx.fuente_clinica and ctx.fuente_clinica.strip()):
            raise ErrorNegocio("Registra la fuente clínica de respaldo.", 422)
        etapas_validas = ctx.db.execute(text("""SELECT count(*) FROM etapa e WHERE e.id_caso = :c AND EXISTS
                                                (SELECT 1 FROM opcion_decision o WHERE o.id_etapa = e.id_etapa AND o.es_correcta)"""),
                                        {"c": ctx.id_caso}).scalar()
        if not etapas_validas:
            raise ErrorNegocio("El caso necesita al menos una etapa con solución esperada.", 422)
        ctx.db.execute(text("""UPDATE caso SET estado = 'revisado', id_revisor = CAST(:r AS uuid), fuente_clinica = :f,
                                  fecha_revision = now() WHERE id_caso = :c"""),
                       {"r": ctx.revisor, "f": ctx.fuente_clinica, "c": ctx.id_caso})
        return EstadoRevisado()


class EstadoRevisado(EstadoCaso):
    nombre = "revisado"

    def publicar(self, ctx: ContextoRevision) -> EstadoCaso:
        ctx.db.execute(text("UPDATE caso SET estado = 'publicado', fecha_publicacion = now() WHERE id_caso = :c"),
                       {"c": ctx.id_caso})
        return EstadoPublicado()


class EstadoPublicado(EstadoCaso):
    nombre = "publicado"


ESTADOS: dict[str, type[EstadoCaso]] = {e.nombre: e for e in (EstadoBorrador, EstadoRevisado, EstadoPublicado)}
ACCIONES = {"aprobar", "publicar", "devolver"}


def estado_de(nombre: str) -> EstadoCaso:
    return ESTADOS[nombre]()


def aplicar(nombre_estado: str, accion: str, ctx: ContextoRevision) -> EstadoCaso:
    if accion not in ACCIONES:
        raise ErrorNegocio("Acción de revisión no válida.", 422)
    return getattr(estado_de(nombre_estado), accion)(ctx)
