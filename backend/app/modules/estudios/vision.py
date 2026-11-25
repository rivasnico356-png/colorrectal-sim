"""IE-04: adaptador del modelo de visión (segmentación de pólipos exportada a ONNX).

El modelo se entrena con vision/entrenar.py sobre datasets públicos y se copia a MODELO_VISION_RUTA.
Si el archivo no existe, la plataforma funciona igual y muestra que el modelo no está disponible.
"""
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.core.config import get_settings

CON_REGION = "región compatible con pólipo"
SIN_REGION = "sin región sospechosa visible"


@dataclass
class ResultadoVision:
    roi: dict | None          # rectángulo normalizado {x, y, ancho, alto} entre 0 y 1
    clasificacion: str
    confianza: float          # porcentaje 0 a 100
    version_modelo: str


class ModeloVision(Protocol):
    version: str

    def analizar(self, imagen: bytes) -> ResultadoVision: ...


def resultado_desde_mascara(prob, version: str, umbral: float = 0.5, area_minima: float = 0.005) -> ResultadoVision:
    """Convierte el mapa de probabilidad (alto x ancho, valores 0..1) en región, clasificación y confianza."""
    import numpy as np

    mascara = prob >= umbral
    if mascara.mean() < area_minima:
        return ResultadoVision(None, SIN_REGION, round(float((1 - prob.max()) * 100), 2), version)
    filas, columnas = np.where(mascara)
    alto, ancho = prob.shape
    roi = {"x": round(columnas.min() / ancho, 4), "y": round(filas.min() / alto, 4),
           "ancho": round((columnas.max() - columnas.min() + 1) / ancho, 4), "alto": round((filas.max() - filas.min() + 1) / alto, 4)}
    return ResultadoVision(roi, CON_REGION, round(float(prob[mascara].mean() * 100), 2), version)


class ModeloOnnx:
    def __init__(self, ruta: Path):
        import onnxruntime

        meta_ruta = ruta.with_suffix(".json")
        meta = json.loads(meta_ruta.read_text()) if meta_ruta.exists() else {}
        self.version = meta.get("version", ruta.stem)
        self.tamano = int(meta.get("tamano", 352))
        self.umbral = float(meta.get("umbral", 0.5))
        self.sesion = onnxruntime.InferenceSession(str(ruta), providers=["CPUExecutionProvider"])
        self.entrada = self.sesion.get_inputs()[0].name

    def analizar(self, imagen: bytes) -> ResultadoVision:
        import numpy as np
        from PIL import Image

        img = Image.open(io.BytesIO(imagen)).convert("RGB").resize((self.tamano, self.tamano))
        x = (np.asarray(img, dtype=np.float32) / 255.0 - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        x = x.transpose(2, 0, 1)[None].astype(np.float32)
        logits = self.sesion.run(None, {self.entrada: x})[0][0, 0]
        prob = 1 / (1 + np.exp(-logits))
        return resultado_desde_mascara(prob, self.version, self.umbral)


_modelo: ModeloVision | None = None
_cargado = False


def obtener_modelo() -> ModeloVision | None:
    global _modelo, _cargado
    if not _cargado:
        ruta = Path(get_settings().modelo_vision_ruta)
        try:
            _modelo = ModeloOnnx(ruta) if ruta.exists() else None
        except Exception:  # un modelo dañado no debe detener la plataforma
            _modelo = None
        _cargado = True
    return _modelo


def fijar_modelo(modelo: ModeloVision | None) -> None:
    """Permite usar otro modelo (por ejemplo, en pruebas)."""
    global _modelo, _cargado
    _modelo, _cargado = modelo, True
