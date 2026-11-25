"""Patrón Chain of Responsibility (1.3.2.2, sección 6): validación de las consultas al tutor (RF-004 4.3, RNF-003).

Cada regla es un eslabón. Si la consulta no cumple, el eslabón corta la cadena con ConsultaRechazada y la pregunta
no llega a la IA externa; si cumple, la pasa al siguiente. Las reglas se prueban por separado y se pueden reordenar.
"""
import re
from dataclasses import dataclass


@dataclass
class Consulta:
    pregunta: str | None    # None: la persona solo pidió la explicación de la sugerencia (RF-004 4.2)
    usadas: int             # preguntas ya hechas en la etapa
    maximo: int             # TUTOR_MAX_CONSULTAS_ETAPA


class ConsultaRechazada(Exception):
    """codigo 4xx: error para la interfaz. codigo 200: respuesta guía que se muestra en el chat sin llamar a la IA."""

    def __init__(self, mensaje: str, codigo: int):
        super().__init__(mensaje)
        self.mensaje, self.codigo = mensaje, codigo

    @property
    def es_guia(self) -> bool:
        return self.codigo == 200


class Validador:
    def __init__(self, siguiente: "Validador | None" = None):
        self.siguiente = siguiente

    def validar(self, consulta: Consulta) -> None:
        if consulta.pregunta is not None:
            self.revisar(consulta)
        if self.siguiente:
            self.siguiente.validar(consulta)

    def revisar(self, consulta: Consulta) -> None:  # pragma: no cover - cada eslabón lo redefine
        raise NotImplementedError


class ValidadorLongitud(Validador):
    MINIMO, MAXIMO = 2, 500

    def revisar(self, consulta: Consulta) -> None:
        if not self.MINIMO <= len(consulta.pregunta.strip()) <= self.MAXIMO:
            raise ConsultaRechazada(f"Escribe una pregunta de {self.MINIMO} a {self.MAXIMO} caracteres.", 422)


class ValidadorLimite(Validador):
    def revisar(self, consulta: Consulta) -> None:
        if consulta.usadas >= consulta.maximo:
            raise ConsultaRechazada(f"Ya usaste las {consulta.maximo} preguntas de esta etapa.", 429)


class ValidadorTema(Validador):
    """Mantiene al tutor en el caso: rechaza los intentos de cambiarle las reglas o el papel."""
    PATRONES = [r"ignora\w* (las |tus |todas )?(instrucciones|reglas)", r"olvida\w* (las |tus )?(instrucciones|reglas)",
                r"\bact[uú]a como\b", r"\bfinge (que eres|ser)\b", r"\bprompt (del )?sistema\b", r"\bsystem prompt\b"]
    GUIA = ("Solo puedo ayudarte con el caso que estás resolviendo y con la detección e interpretación del cáncer colorrectal "
            "en imágenes. Prueba con una pregunta sobre la etapa, por ejemplo: ¿qué debo observar en esta imagen?")

    def revisar(self, consulta: Consulta) -> None:
        if any(re.search(p, consulta.pregunta, re.IGNORECASE) for p in self.PATRONES):
            raise ConsultaRechazada(self.GUIA, 200)


class ValidadorSeguridad(Validador):
    """RNF-003: no envía datos personales a la IA externa. RF-004: no da indicaciones de tratamiento."""
    DATOS_PERSONALES = [r"[\w.+-]+@[\w-]+\.[\w.]+", r"(?<!\d)\d{7,12}(?!\d)"]  # correo, teléfono o número de documento
    TRATAMIENTO = [r"\bdosis\b", r"\bqu[eé] (medicamento|remedio|pastilla)s?\b", r"\b(debo|puedo) (tomar|dejar de tomar)\b",
                   r"\bqu[eé] tratamiento (debo|me sirve|necesito)\b", r"\bme (receta|recetas|formula|formulas)\b"]
    GUIA_DATOS = ("Por tu privacidad, no escribas correos, teléfonos ni números de documento en tus preguntas. "
                  "Vuelve a escribirla sin esos datos.")
    GUIA_TRATAMIENTO = ("No puedo dar indicaciones de tratamiento ni de medicamentos. Esa decisión es de tu médico. "
                        "Puedo ayudarte a entender la imagen y la etapa del caso.")

    def revisar(self, consulta: Consulta) -> None:
        if any(re.search(p, consulta.pregunta) for p in self.DATOS_PERSONALES):
            raise ConsultaRechazada(self.GUIA_DATOS, 200)
        if any(re.search(p, consulta.pregunta, re.IGNORECASE) for p in self.TRATAMIENTO):
            raise ConsultaRechazada(self.GUIA_TRATAMIENTO, 200)


def crear_cadena() -> Validador:
    """Orden: primero lo barato (longitud y límite) y después el contenido."""
    return ValidadorLongitud(ValidadorLimite(ValidadorTema(ValidadorSeguridad())))
