"""Pruebas unitarias de reglas de validación (sin base de datos)."""
import pytest
from pydantic import ValidationError

from app.core.textos import ROTULO_IA
from app.modules.casos.schemas import EtapaIn
from app.modules.usuarios.schemas import RegistroIn

OPCION = {"texto": "A", "puntaje": 0, "retroalimentacion": "Explicación de la opción.", "fuente": "Fuente de respaldo"}


def _registro(clave: str) -> dict:
    return {"nombre": "Ana", "correo": "ana@ejemplo.com", "contrasena": clave, "rango_edad": "40-49", "acepta_politica": True}


@pytest.mark.parametrize("clave", ["solamente", "12345678", "abc12"])
def test_contrasena_exige_letras_numeros_y_largo(clave):
    with pytest.raises(ValidationError):
        RegistroIn(**_registro(clave))


def test_contrasena_valida():
    assert RegistroIn(**_registro("Segura123")).contrasena == "Segura123"


def _etapa(opciones):
    return {"orden": 1, "enunciado": "Observe la imagen de la etapa.", "recomendacion_ia": "La IA sugiere la opción A.",
            "opciones": opciones}


def test_etapa_exige_una_sola_respuesta_correcta():
    with pytest.raises(ValidationError):
        EtapaIn(**_etapa([OPCION | {"es_correcta": True, "recomendada_ia": True}, OPCION | {"es_correcta": True}]))


def test_etapa_exige_recomendacion_de_la_ia():
    with pytest.raises(ValidationError):
        EtapaIn(**_etapa([OPCION | {"es_correcta": True}, OPCION]))


def test_marca_error_intencional_si_la_ia_recomienda_una_opcion_incorrecta():
    e = EtapaIn(**_etapa([OPCION | {"es_correcta": True, "puntaje": 100}, OPCION | {"recomendada_ia": True}]))
    assert e.ia_erronea_intencional


def test_rotulo_texto_exacto_del_srs():
    assert ROTULO_IA == ("Resultado experimental de apoyo a la detección e interpretación; "
                         "no reemplaza la valoración de su médico.")
