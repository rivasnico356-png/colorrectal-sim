"""Patrón Strategy (RF-004 4.5): IA principal → modelo alternativo → recomendación predefinida.
La simulación nunca se bloquea si la IA falla."""
import logging

from app.core.config import get_settings
from app.core.textos import ROTULO_IA
from app.modules.tutor import prompt
from app.modules.tutor.proveedores import AdaptadorOpenAICompatible, ErrorProveedor, ProveedorLLM, RespuestaIA

registro = logging.getLogger("colorrectal.tutor")
MENSAJE_PREDEFINIDA = f"El tutor no está disponible en este momento. Esta es la explicación preparada para la etapa. {ROTULO_IA}"


class ServicioTutor:
    def __init__(self, proveedores: list[ProveedorLLM]):
        self.proveedores = proveedores
        self.errores: list[str] = []

    def explicar(self, enunciado: str, recomendacion: str, explicacion_predefinida: str,
                 pregunta: str | None = None, descripcion_imagen: str | None = None,
                 contexto_caso: str | None = None) -> RespuestaIA:
        mensaje = prompt.contexto_etapa(enunciado, recomendacion, descripcion_imagen, contexto_caso)
        mensaje += f"\n\nPregunta de la persona: {pregunta}" if pregunta else "\n\nExplica la sugerencia de esta etapa."
        self.errores.clear()
        for proveedor in self.proveedores:
            try:
                return proveedor.completar(prompt.SISTEMA, mensaje)
            except ErrorProveedor as e:
                self.errores.append(f"{proveedor.nombre}: {e}")
                # Va al registro del servidor para diagnosticar; nunca incluye la clave de API.
                registro.warning("Tutor: falló %s (%s): %s", proveedor.nombre, getattr(proveedor, "modelo", "-"), e)
        return RespuestaIA(f"{explicacion_predefinida}\n\n{MENSAJE_PREDEFINIDA}", "predefinida", "-", 0)


def crear_servicio() -> ServicioTutor:
    """Factory Method: arma la cadena de proveedores según la configuración (variables de entorno)."""
    s = get_settings()
    return ServicioTutor([
        AdaptadorOpenAICompatible("principal", s.ia_api_url, s.ia_api_key, s.ia_modelo_principal, s.ia_timeout_segundos),
        AdaptadorOpenAICompatible("alternativo", s.ia_api_url, s.ia_api_key, s.ia_modelo_alternativo, s.ia_timeout_segundos),
    ])
