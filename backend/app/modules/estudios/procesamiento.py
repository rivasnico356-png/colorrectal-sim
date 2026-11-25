"""Patrón Template Method (1.3.2.2, sección 7): procesamiento de imágenes con pasos fijos (RF-003 3.4, RF-010).

ProcesadorImagen.procesar fija el orden: control de calidad → desidentificación → normalización → análisis → registro.
Las subclases redefinen solo los pasos que cambian (control de calidad, desidentificación y el análisis, que es abstracto):
- ProcesadorCasoSimulado: imágenes de datasets públicos de los casos; no tienen datos personales.
- ProcesadorEstudioPropio: estudios que carga la persona; se quitan los metadatos EXIF y DICOM antes de todo.
Como el orden está en la clase base, la desidentificación no se puede saltar por error.
"""
import io
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.errores import ErrorNegocio
from app.modules.estudios import seguridad
from app.modules.estudios.vision import ModeloVision, ResultadoVision, obtener_modelo

registro = logging.getLogger("colorrectal.vision")


@dataclass
class ImagenProcesada:
    imagen: bytes                       # imagen lista para guardar (PNG sin metadatos en los estudios propios)
    advertencia_texto: bool             # el DICOM declara texto sobreimpreso
    resultado: ResultadoVision | None   # None si el modelo de visión no está disponible


class ProcesadorImagen(ABC):
    def __init__(self, modelo: ModeloVision | None = None, usar_modelo_por_defecto: bool = True):
        self.modelo = modelo if modelo is not None or not usar_modelo_por_defecto else obtener_modelo()

    def procesar(self, nombre: str, contenido: bytes) -> ImagenProcesada:
        """Método plantilla: el orden de los pasos es el mismo para toda fuente de imágenes."""
        self.control_calidad(nombre, contenido)
        limpia, advertencia = self.desidentificar(nombre, contenido)
        normalizada = self.normalizar(limpia)
        resultado = self.analizar(normalizada)
        self.registrar(resultado)
        return ImagenProcesada(limpia, advertencia, resultado)

    @abstractmethod
    def control_calidad(self, nombre: str, contenido: bytes) -> None: ...

    @abstractmethod
    def desidentificar(self, nombre: str, contenido: bytes) -> tuple[bytes, bool]: ...

    def normalizar(self, imagen: bytes) -> bytes:
        """Comprueba que sea una imagen legible; el modelo la redimensiona y normaliza a su tamaño de entrada."""
        from PIL import Image

        try:
            Image.open(io.BytesIO(imagen)).verify()
        except Exception as exc:
            raise ErrorNegocio("No pudimos leer la imagen. Verifica que el archivo no esté dañado.", 422) from exc
        return imagen

    @abstractmethod
    def analizar(self, imagen: bytes) -> ResultadoVision | None:
        """Paso abstracto: cada fuente de imágenes decide cómo se analiza."""

    def _modelo_vision(self, imagen: bytes) -> ResultadoVision | None:
        return self.modelo.analizar(imagen) if self.modelo is not None else None

    def registrar(self, resultado: ResultadoVision | None) -> None:
        """RNF-007: deja en el registro del servidor la versión del modelo que produjo cada resultado."""
        if resultado is not None:
            registro.info("%s: %s (%.2f %%) con %s", type(self).__name__, resultado.clasificacion, resultado.confianza,
                          resultado.version_modelo)


class ProcesadorCasoSimulado(ProcesadorImagen):
    """Imágenes de los casos (Kvasir-SEG y otros datasets públicos), ya validadas al cargarlas en el editor."""

    def control_calidad(self, nombre: str, contenido: bytes) -> None:
        if not contenido:
            raise ErrorNegocio("La etapa no tiene imagen.", 422)

    def desidentificar(self, nombre: str, contenido: bytes) -> tuple[bytes, bool]:
        return contenido, False  # datasets públicos anonimizados en su origen: no hay datos personales que quitar

    def analizar(self, imagen: bytes) -> ResultadoVision | None:
        """Región de interés, clasificación y confianza del modelo sobre la imagen del dataset (RF-003 3.4).
        Las regiones de los casos no se guardan precalculadas en la base, así que se obtienen del modelo."""
        return self._modelo_vision(imagen)


class ProcesadorEstudioPropio(ProcesadorImagen):
    """Estudios de la persona (RF-010 10.2 y RNF-003)."""

    def control_calidad(self, nombre: str, contenido: bytes) -> None:
        from pathlib import Path

        if Path(nombre).suffix.lower() not in seguridad.EXTENSIONES:
            raise ErrorNegocio("Formato no permitido. Usa JPG, PNG o DICOM (.dcm).", 415)
        if len(contenido) > seguridad.MAX_BYTES:
            raise ErrorNegocio("El archivo supera el tamaño máximo de 20 MB.", 413)

    def desidentificar(self, nombre: str, contenido: bytes) -> tuple[bytes, bool]:
        return seguridad.desidentificar(nombre, contenido)  # PNG nuevo sin EXIF ni etiquetas DICOM

    def analizar(self, imagen: bytes) -> ResultadoVision | None:
        """El modelo de visión (IE-04) analiza el estudio ya desidentificado (RF-010 10.3)."""
        return self._modelo_vision(imagen)
