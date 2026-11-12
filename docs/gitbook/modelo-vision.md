# Modelo de visión (IE-04, RF-003 3.4 y RF-010 10.3)

Modelo experimental que marca regiones compatibles con pólipos en imágenes de colonoscopia. Es una **U-Net con codificador
ResNet-34** entrenada con datasets públicos y exportada a ONNX para que el backend la use sin GPU.

> Resultado experimental de apoyo a la detección e interpretación; no reemplaza la valoración de su médico.

## 1. Descargar los datasets (fuera del repositorio)

| Dataset | Uso | Fuente oficial |
|---------|-----|----------------|
| Kvasir-SEG | Entrenamiento | https://datasets.simula.no/kvasir-seg/ |
| CVC-ClinicDB (Bernal et al., 2015) | Entrenamiento | https://polyp.grand-challenge.org/CVCClinicDB/ |
| PolypGen | Prueba de generalización | Synapse (proyecto PolypGen) |

Antes de usar cada uno, verifica su licencia en la fuente y anótala en `docs/datasets.md` con su cita APA.
Las imágenes van en `data/`, que está en `.gitignore`.

## 2. Entrenar en Google Colab

1. Abre un cuaderno nuevo y elige **Entorno de ejecución → Cambiar tipo → GPU**.
2. Ejecuta:

```bash
!git clone https://github.com/rivasnico356-png/colorrectal-sim.git
%cd colorrectal-sim
!pip install -r vision/requirements.txt
# Sube o descarga los datasets a data/ y luego:
!cd vision && python entrenar.py \
    --imagenes ../data/kvasir-seg/images --mascaras ../data/kvasir-seg/masks \
    --imagenes "../data/cvc-clinicdb/Original" --mascaras "../data/cvc-clinicdb/Ground Truth" \
    --epocas 40 --salida salidas
!cd vision && python evaluar.py --modelo salidas/vision.onnx \
    --imagenes ../data/polypgen/images --mascaras ../data/polypgen/masks
```

3. Descarga `vision/salidas/vision.onnx` y `vision/salidas/vision.json`.

## 3. Usarlo en la plataforma

Copia los dos archivos a `backend/modelos/` (o a la ruta de `MODELO_VISION_RUTA`). El backend lo carga solo; si no está,
la plataforma funciona igual y muestra que el modelo no está disponible.

## Reproducibilidad (Plan de Calidad, C-06)

`vision.json` guarda la versión del modelo, la semilla, las particiones, los hiperparámetros, las versiones de las
librerías y las métricas (Dice e IoU) en prueba y en PolypGen. `particiones.json` lista qué imagen quedó en cada partición.
Con la misma semilla y los mismos datos se obtiene la misma partición.
