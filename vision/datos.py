"""Lectura de datasets públicos de segmentación de pólipos (Kvasir-SEG, CVC-ClinicDB, PolypGen).

Cada dataset se descarga desde su fuente oficial a una carpeta local (nunca al repositorio) con dos subcarpetas:
una de imágenes y otra de máscaras, emparejadas por nombre de archivo.
"""
import random
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

EXTENSIONES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
MEDIA = np.array([0.485, 0.456, 0.406], dtype=np.float32)
DESVIACION = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def pares(imagenes: Path, mascaras: Path) -> list[tuple[Path, Path]]:
    """Empareja cada imagen con la máscara del mismo nombre (sin importar la extensión)."""
    por_nombre = {p.stem: p for p in mascaras.iterdir() if p.suffix.lower() in EXTENSIONES}
    salida = [(p, por_nombre[p.stem]) for p in sorted(imagenes.iterdir()) if p.suffix.lower() in EXTENSIONES and p.stem in por_nombre]
    if not salida:
        raise FileNotFoundError(f"No se encontraron pares imagen–máscara en {imagenes} y {mascaras}")
    return salida


def particionar(lista: list, semilla: int, proporciones=(0.8, 0.1, 0.1)) -> dict[str, list]:
    """Partición reproducible entrenamiento / validación / prueba con semilla fija (Plan de Calidad, C-06)."""
    lista = sorted(lista)
    random.Random(semilla).shuffle(lista)
    n = len(lista)
    a, b = int(n * proporciones[0]), int(n * (proporciones[0] + proporciones[1]))
    return {"entrenamiento": lista[:a], "validacion": lista[a:b], "prueba": lista[b:]}


def preparar_imagen(img: Image.Image, tamano: int) -> np.ndarray:
    x = np.asarray(img.convert("RGB").resize((tamano, tamano), Image.BILINEAR), dtype=np.float32) / 255.0
    return ((x - MEDIA) / DESVIACION).transpose(2, 0, 1)


class DatasetPolipos(Dataset):
    def __init__(self, pares_lista: list[tuple[Path, Path]], tamano: int = 352, aumentar: bool = False):
        self.pares, self.tamano, self.aumentar = pares_lista, tamano, aumentar

    def __len__(self) -> int:
        return len(self.pares)

    def __getitem__(self, i: int):
        ruta_img, ruta_mask = self.pares[i]
        img = Image.open(ruta_img)
        mask = Image.open(ruta_mask).convert("L").resize((self.tamano, self.tamano), Image.NEAREST)
        x = preparar_imagen(img, self.tamano)
        y = (np.asarray(mask, dtype=np.float32) > 127).astype(np.float32)[None]
        if self.aumentar:
            if random.random() < 0.5:
                x, y = x[:, :, ::-1], y[:, :, ::-1]
            if random.random() < 0.5:
                x, y = x[:, ::-1, :], y[:, ::-1, :]
        return torch.from_numpy(x.copy()), torch.from_numpy(y.copy())
