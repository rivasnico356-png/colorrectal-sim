"""PU-03 a PU-05: cadena de respaldo del agente tutor (RF-004, ADR-04)."""
import json

import httpx

from app.modules.tutor.proveedores import AdaptadorOpenAICompatible, ErrorProveedor, RespuestaIA, texto_plano
from app.modules.tutor.servicio import ServicioTutor


class Falla:
    def __init__(self, nombre):
        self.nombre, self.modelo = nombre, "x"

    def completar(self, sistema, mensaje):
        raise ErrorProveedor("caído")


class Responde:
    def __init__(self, nombre):
        self.nombre, self.modelo = nombre, "m"

    def completar(self, sistema, mensaje):
        return RespuestaIA("explicación", self.nombre, self.modelo, 10)


ARGS = ("Etapa 1", "Observe la mucosa", "Explicación preparada")


def test_usa_principal_si_responde():
    assert ServicioTutor([Responde("principal"), Responde("alternativo")]).explicar(*ARGS).proveedor == "principal"


def test_pasa_al_alternativo_si_falla_el_principal():
    s = ServicioTutor([Falla("principal"), Responde("alternativo")])
    assert s.explicar(*ARGS).proveedor == "alternativo"
    assert len(s.errores) == 1


def test_usa_predefinida_si_todo_falla():
    r = ServicioTutor([Falla("principal"), Falla("alternativo")]).explicar(*ARGS)
    assert r.proveedor == "predefinida"
    assert "Explicación preparada" in r.texto and "no reemplaza" in r.texto


def test_adaptador_sin_clave_lanza_error():
    a = AdaptadorOpenAICompatible("principal", "http://x", "", "m")
    try:
        a.completar("s", "m")
        raise AssertionError("debía fallar")
    except ErrorProveedor:
        pass


def test_adaptador_lee_respuesta_formato_openai():
    def manejador(request):
        assert request.headers["Authorization"] == "Bearer k"
        return httpx.Response(200, json={"choices": [{"message": {"content": " hola "}}]})
    a = AdaptadorOpenAICompatible("principal", "http://x/v1", "k", "m",
                                  cliente=httpx.Client(transport=httpx.MockTransport(manejador)))
    assert a.completar("s", "m").texto == "hola"


def test_adaptador_pide_razonamiento_bajo_a_gpt_oss():
    """Los modelos gpt-oss de Groq razonan antes de responder: esfuerzo bajo y sin el razonamiento en la respuesta."""
    enviado = {}

    def manejador(request):
        enviado.update(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": "listo"}}]})
    a = AdaptadorOpenAICompatible("principal", "http://x/v1", "k", "openai/gpt-oss-120b",
                                  cliente=httpx.Client(transport=httpx.MockTransport(manejador)))
    assert a.completar("s", "m").texto == "listo"
    assert enviado["reasoning_effort"] == "low" and enviado["include_reasoning"] is False
    assert enviado["max_completion_tokens"] == 1024 and "max_tokens" not in enviado


def test_adaptador_explica_el_rechazo_del_proveedor_y_limpia_la_clave():
    def manejador(request):
        assert request.headers["Authorization"] == "Bearer k"
        return httpx.Response(401, json={"error": {"message": "Invalid API Key"}})
    a = AdaptadorOpenAICompatible("principal", "http://x", " k\n", "m",
                                  cliente=httpx.Client(transport=httpx.MockTransport(manejador)))
    try:
        a.completar("s", "m")
        raise AssertionError("debía fallar")
    except ErrorProveedor as e:
        assert "401" in str(e) and "Invalid API Key" in str(e)


def test_respuesta_del_modelo_queda_en_texto_plano():
    texto = "## Pista\n\nEn esta etapa hay una **sugerencia**:\n- Revisa la imagen  \n* Compara opciones"
    assert texto_plano(texto) == "Pista\n\nEn esta etapa hay una sugerencia:\n• Revisa la imagen\n• Compara opciones"


def test_adaptador_convierte_error_http():
    a = AdaptadorOpenAICompatible("principal", "http://x", "k", "m",
                                  cliente=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(503))))
    try:
        a.completar("s", "m")
        raise AssertionError("debía fallar")
    except ErrorProveedor:
        pass
