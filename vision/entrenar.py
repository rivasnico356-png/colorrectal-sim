"""Entrena el modelo experimental de segmentación de pólipos y lo exporta a ONNX para la plataforma (IE-04).

Uso (Google Colab con GPU):
    python vision/entrenar.py --imagenes data/kvasir-seg/images --mascaras data/kvasir-seg/masks \
        --imagenes data/cvc-clinicdb/Original --mascaras data/cvc-clinicdb/"Ground Truth" --epocas 40

Salida en vision/salidas/: modelo.pt, vision.onnx, vision.json (versión, métricas, semillas, particiones y librerías).
"""
import argparse
import json
import platform
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import segmentation_models_pytorch as smp
import torch
from torch.utils.data import DataLoader

from datos import DatasetPolipos, pares, particionar


def fijar_semillas(semilla: int) -> None:
    random.seed(semilla)
    np.random.seed(semilla)
    torch.manual_seed(semilla)
    torch.cuda.manual_seed_all(semilla)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def metricas(logits: torch.Tensor, y: torch.Tensor, umbral: float = 0.5) -> tuple[float, float]:
    """Dice e IoU por lote."""
    p = (torch.sigmoid(logits) >= umbral).float()
    inter = (p * y).sum(dim=(1, 2, 3))
    union = p.sum(dim=(1, 2, 3)) + y.sum(dim=(1, 2, 3))
    dice = ((2 * inter + 1e-6) / (union + 1e-6)).mean().item()
    iou = ((inter + 1e-6) / (union - inter + 1e-6)).mean().item()
    return dice, iou


def evaluar(modelo, cargador, dispositivo) -> dict:
    modelo.eval()
    dices, ious = [], []
    with torch.no_grad():
        for x, y in cargador:
            d, i = metricas(modelo(x.to(dispositivo)), y.to(dispositivo))
            dices.append(d)
            ious.append(i)
    return {"dice": round(float(np.mean(dices)), 4), "iou": round(float(np.mean(ious)), 4)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--imagenes", action="append", required=True, help="Carpeta de imágenes (se puede repetir por dataset)")
    ap.add_argument("--mascaras", action="append", required=True, help="Carpeta de máscaras, en el mismo orden")
    ap.add_argument("--datasets", nargs="*", default=["Kvasir-SEG", "CVC-ClinicDB"], help="Nombres para el registro")
    ap.add_argument("--epocas", type=int, default=40)
    ap.add_argument("--lote", type=int, default=8)
    ap.add_argument("--tamano", type=int, default=352)
    ap.add_argument("--tasa", type=float, default=1e-4)
    ap.add_argument("--semilla", type=int, default=2026)
    ap.add_argument("--salida", default="vision/salidas")
    ap.add_argument("--version", default=f"polipos-unet-r34-{datetime.now():%Y%m%d}")
    a = ap.parse_args()

    fijar_semillas(a.semilla)
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    todos = [par for im, ma in zip(a.imagenes, a.mascaras, strict=True) for par in pares(Path(im), Path(ma))]
    particiones = particionar(todos, a.semilla)
    (salida / "particiones.json").write_text(json.dumps({k: [str(p[0]) for p in v] for k, v in particiones.items()}, indent=1))

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    cargar = {k: DataLoader(DatasetPolipos(v, a.tamano, aumentar=(k == "entrenamiento")), batch_size=a.lote,
                            shuffle=(k == "entrenamiento"), num_workers=2) for k, v in particiones.items()}
    modelo = smp.Unet(encoder_name="resnet34", encoder_weights="imagenet", in_channels=3, classes=1).to(dispositivo)
    perdida_dice = smp.losses.DiceLoss(mode="binary")
    perdida_bce = torch.nn.BCEWithLogitsLoss()
    optim = torch.optim.Adam(modelo.parameters(), lr=a.tasa)
    mejor, historial = -1.0, []

    for epoca in range(1, a.epocas + 1):
        modelo.train()
        for x, y in cargar["entrenamiento"]:
            x, y = x.to(dispositivo), y.to(dispositivo)
            optim.zero_grad()
            logits = modelo(x)
            (perdida_dice(logits, y) + perdida_bce(logits, y)).backward()
            optim.step()
        val = evaluar(modelo, cargar["validacion"], dispositivo)
        historial.append({"epoca": epoca, **val})
        print(f"Época {epoca}: Dice validación {val['dice']}  IoU {val['iou']}")
        if val["dice"] > mejor:
            mejor = val["dice"]
            torch.save(modelo.state_dict(), salida / "modelo.pt")

    modelo.load_state_dict(torch.load(salida / "modelo.pt", map_location=dispositivo))
    prueba = evaluar(modelo, cargar["prueba"], dispositivo)
    print(f"Prueba: {prueba}")

    modelo.eval().to("cpu")
    ejemplo = torch.zeros(1, 3, a.tamano, a.tamano)
    torch.onnx.export(modelo, ejemplo, salida / "vision.onnx", input_names=["imagen"], output_names=["logits"], opset_version=17)
    meta = {
        "version": a.version, "tamano": a.tamano, "umbral": 0.5, "arquitectura": "U-Net con codificador ResNet-34",
        "datasets": a.datasets, "imagenes_por_particion": {k: len(v) for k, v in particiones.items()},
        "semilla": a.semilla, "epocas": a.epocas, "lote": a.lote, "tasa_aprendizaje": a.tasa,
        "metricas_prueba": prueba, "historial_validacion": historial,
        "librerias": {"python": platform.python_version(), "torch": torch.__version__, "smp": smp.__version__},
        "uso": "Resultado experimental de apoyo a la detección e interpretación; no reemplaza la valoración de su médico.",
    }
    (salida / "vision.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"Modelo exportado en {salida / 'vision.onnx'}")


if __name__ == "__main__":
    main()
