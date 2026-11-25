"""Patrón Strategy (1.3.2.2, sección 2; RF-004 4.5): IA generativa → modelo alternativo → recomendación predefinida.

ServicioTutor recibe una lista de estrategias (EstrategiaRecomendacion) y las prueba en orden; si una falla o
agota el tiempo, conmuta a la siguiente. La última, EstrategiaPredefinida, nunca falla, así que la simulación
no se bloquea si la IA no responde.
"""
import logging
from typing import Protocol

from app.core.textos import ROTULO_IA
from app.modules.tutor import prompt
from app.modules.tutor.proveedores import ErrorProveedor, FabricaProveedores, ProveedorLLM, RespuestaIA

registro = logging.getLogger("colorrectal.tutor")
MENSAJE_PREDEFINIDA = f"El tutor no está disponible en este momento. Esta es la explicación preparada para la etapa. {ROTULO_IA}"


class EstrategiaRecomendacion(Protocol):
    nombre: str

    def obtener(self, mensaje: str, explicacion_predefinida: str) -> RespuestaIA: ...


class EstrategiaIA:
    """Obtiene la respuesta de un proveedor de IA (principal o alternativo) por su adaptador."""

    def __init__(self, proveedor: ProveedorLLM):
        self.proveedor = proveedor
        self.nombre = proveedor.nombre

    def obtener(self, mensaje: str, explicacion_predefinida: str) -> RespuestaIA:
        return self.proveedor.completar(prompt.SISTEMA, mensaje)


class EstrategiaPredefinida:
    """Recomendación que el Profesional de la salud configuró para la etapa (último respaldo)."""

    nombre = "predefinida"

    def obtener(self, mensaje: str, explicacion_predefinida: str) -> RespuestaIA:
        return RespuestaIA(f"{explicacion_predefinida}\n\n{MENSAJE_PREDEFINIDA}", "predefinida", "-", 0)


class ServicioTutor:
    def __init__(self, estrategias: list):
        # Acepta estrategias o proveedores (se envuelven en EstrategiaIA); siempre termina en la predefinida.
        self.estrategias: list[EstrategiaRecomendacion] = [e if hasattr(e, "obtener") else EstrategiaIA(e) for e in estrategias]
        if not any(isinstance(e, EstrategiaPredefinida) for e in self.estrategias):
            self.estrategias.append(EstrategiaPredefinida())
        self.errores: list[str] = []

    def recomendar(self, enunciado: str, recomendacion: str, explicacion_predefinida: str,
                   pregunta: str | None = None, descripcion_imagen: str | None = None,
                   contexto_caso: str | None = None) -> RespuestaIA:
        mensaje = prompt.contexto_etapa(enunciado, recomendacion, descripcion_imagen, contexto_caso)
        mensaje += f"\n\nPregunta de la persona: {pregunta}" if pregunta else "\n\nExplica la sugerencia de esta etapa."
        self.errores.clear()
        for estrategia in self.estrategias:
            try:
                return estrategia.obtener(mensaje, explicacion_predefinida)
            except (ErrorProveedor, TimeoutError) as e:
                self.errores.append(f"{estrategia.nombre}: {e}")
                # Va al registro del servidor para revisar la falla; nunca incluye la clave de API.
                registro.warning("Tutor: falló %s (%s): %s", estrategia.nombre,
                                 getattr(getattr(estrategia, "proveedor", None), "modelo", "-"), e)
        return EstrategiaPredefinida().obtener(mensaje, explicacion_predefinida)  # pragma: no cover

    explicar = recomendar  # nombre usado por la fachada y las pruebas anteriores


def crear_servicio() -> ServicioTutor:
    """Arma las estrategias con los adaptadores que crea la fábrica según las variables de entorno."""
    return ServicioTutor([EstrategiaIA(FabricaProveedores.crear("principal")),
                          EstrategiaIA(FabricaProveedores.crear("alternativo")),
                          EstrategiaPredefinida()])
