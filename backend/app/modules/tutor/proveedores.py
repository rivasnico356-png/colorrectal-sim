"""Patrón Adapter (ADR-04): cada proveedor de IA implementa la misma interfaz ProveedorLLM."""
import time
from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass
class RespuestaIA:
    texto: str
    proveedor: str          # principal, alternativo o predefinida (columna interaccion_ia.proveedor)
    version_modelo: str
    latencia_ms: int


class ErrorProveedor(Exception):
    """El proveedor no respondió a tiempo o devolvió un error."""


class ProveedorLLM(Protocol):
    nombre: str
    modelo: str

    def completar(self, sistema: str, mensaje: str) -> RespuestaIA: ...


class AdaptadorOpenAICompatible:
    """Sirve para Groq y cualquier API con el formato de chat de OpenAI."""

    def __init__(self, nombre: str, url: str, api_key: str, modelo: str, timeout: float = 8.0,
                 cliente: httpx.Client | None = None):
        # La clave se copia de una consola web: se quitan espacios o saltos de línea que se cuelan al pegarla.
        self.nombre, self.url, self.api_key, self.modelo, self.timeout = nombre, url, (api_key or "").strip(), modelo, timeout
        self._cliente = cliente or httpx.Client(timeout=timeout)

    def completar(self, sistema: str, mensaje: str) -> RespuestaIA:
        if not self.api_key:
            raise ErrorProveedor("No hay clave de API configurada.")
        inicio = time.perf_counter()
        cuerpo = {"model": self.modelo, "temperature": 0.3, "max_tokens": 350,
                  "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": mensaje}]}
        if "gpt-oss" in self.modelo:
            # Modelos de razonamiento: el razonamiento interno gasta tokens antes de la respuesta, por eso se pide
            # esfuerzo bajo, más tokens y que no se incluya en la respuesta (parámetros de Groq para gpt-oss).
            cuerpo.pop("max_tokens")
            cuerpo |= {"max_completion_tokens": 1024, "reasoning_effort": "low", "include_reasoning": False}
        try:
            r = self._cliente.post(self.url, headers={"Authorization": f"Bearer {self.api_key}"}, json=cuerpo)
            if r.status_code >= 400:
                # El mensaje del proveedor explica el rechazo (clave inválida, modelo retirado, límite de uso).
                raise ErrorProveedor(f"HTTP {r.status_code}: {r.text[:300]}")
            texto = r.json()["choices"][0]["message"]["content"].strip()
            if not texto:
                raise ErrorProveedor("Respuesta vacía del modelo.")
        except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError, AttributeError) as exc:
            raise ErrorProveedor(str(exc)) from exc
        return RespuestaIA(texto, self.nombre, self.modelo, int((time.perf_counter() - inicio) * 1000))
