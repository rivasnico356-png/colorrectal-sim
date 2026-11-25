"""Evalúa el modelo ONNX exportado en otro dataset (por ejemplo PolypGen) para medir la generalización.

Uso: python vision/evaluar.py --modelo vision/salidas/vision.onnx --imagenes data/polypgen/images --mascaras data/polypgen/masks
"""
import argparse
import json
from pathlib import Path

import numpy as np
import onnxruntime
from PIL import Image

from datos import pares, preparar_imagen


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--imagenes", required=True)
    ap.add_argument("--mascaras", required=True)
    ap.add_argument("--nombre", default="PolypGen")
    a = ap.parse_args()
    meta = json.loads(Path(a.modelo).with_suffix(".json").read_text())
    tamano, umbral = meta["tamano"], meta["umbral"]
    sesion = onnxruntime.InferenceSession(a.modelo, providers=["CPUExecutionProvider"])
    dices, ious = [], []
    for ruta_img, ruta_mask in pares(Path(a.imagenes), Path(a.mascaras)):
        x = preparar_imagen(Image.open(ruta_img), tamano)[None].astype(np.float32)
        p = 1 / (1 + np.exp(-sesion.run(None, {"imagen": x})[0][0, 0])) >= umbral
        y = np.asarray(Image.open(ruta_mask).convert("L").resize((tamano, tamano), Image.NEAREST)) > 127
        inter, suma = (p & y).sum(), p.sum() + y.sum()
        dices.append((2 * inter + 1e-6) / (suma + 1e-6))
        ious.append((inter + 1e-6) / (suma - inter + 1e-6))
    resultado = {"dataset": a.nombre, "imagenes": len(dices), "dice": round(float(np.mean(dices)), 4),
                 "iou": round(float(np.mean(ious)), 4)}
    meta.setdefault("generalizacion", []).append(resultado)
    Path(a.modelo).with_suffix(".json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(resultado)


if __name__ == "__main__":
    main()
