# Modelo de visión (IE-04, RF-003 3.4 y RF-010 10.3)

Modelo experimental que marca regiones compatibles con pólipos en imágenes de colonoscopia. Es una **U-Net** con un
codificador preentrenado en ImageNet (MobileNetV2 en la versión publicada; ResNet-34 si se entrena con GPU), entrenada con
datasets públicos y exportada a ONNX para que el backend la use sin GPU.

> Resultado experimental de apoyo a la detección e interpretación; no reemplaza la valoración de su médico.

## 1. Descargar los datasets (fuera del repositorio)

| Dataset | Uso | Fuente oficial |
|---------|-----|----------------|
| Kvasir-SEG | Entrenamiento | https://datasets.simula.no/kvasir-seg/ |
| CVC-ClinicDB | Entrenamiento | https://polyp.grand-challenge.org/CVCClinicDB/ |
| PolypGen | Prueba de generalización | Synapse (proyecto PolypGen) |

Antes de usar cada uno, verifica su licencia en la fuente y anótala en `docs/datasets.md` con su cita APA.
Las imágenes van en `data/`, que está en `.gitignore`.

## 2. Entrenar en GitHub Actions (versión publicada)

1. En GitHub, pestaña **Actions › Entrenar modelo de visión › Run workflow** (rama `develop`).
2. Valores por defecto: 25 épocas, imágenes de 256 px, codificador `mobilenet_v2`, publicar = sí. Con 30 épocas tarda
   cerca de 1,5 horas en CPU.
3. El flujo descarga Kvasir-SEG de su fuente oficial (`vision/descargar_kvasir.sh`), entrena con semilla 2026 y
   particiones 80/10/10, comprueba que el ONNX carga con onnxruntime y publica en el release **modelo-vision**:
   `vision.onnx`, `vision.json`, `particiones.json`, la huella SHA-256 del dataset y una imagen de ejemplo de la
   partición de prueba (`ejemplo-kvasir.jpg`).
4. El despliegue en Render (`despliegue/Dockerfile`) descarga esos archivos del release en cada construcción.

Versión publicada: `polipos-unet-mobilenet_v2-20261112` (12-11-2026, corrida 43298585293). Prueba con 100 imágenes que
el modelo no vio al entrenar: **Dice 0,872 · IoU 0,805**. Pendiente: medirlo en PolypGen (otros centros).

## 3. Entrenar en Google Colab (con GPU, opcional)

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

## 4. Usarlo en la plataforma

Descarga `vision.onnx` y `vision.json` del release **modelo-vision** en GitHub y cópialos a `backend/modelos/` (o a la
ruta de `MODELO_VISION_RUTA`). El backend lo carga solo; si no está,
la plataforma funciona igual y muestra que el modelo no está disponible.

En el PC con Docker (PowerShell, dentro de la carpeta `colorrectal-sim`):

```powershell
mkdir backend\modelos -Force
$r = "https://github.com/rivasnico356-png/colorrectal-sim/releases/download/modelo-vision"
Invoke-WebRequest "$r/vision.onnx" -OutFile backend\modelos\vision.onnx
Invoke-WebRequest "$r/vision.json" -OutFile backend\modelos\vision.json
docker compose up -d --build
```

## Reproducibilidad (Plan de Calidad, C-06)

`vision.json` guarda la versión del modelo, la semilla, las particiones, los hiperparámetros, las versiones de las
librerías y las métricas (Dice e IoU) en prueba y en PolypGen. `particiones.json` lista qué imagen quedó en cada partición.
Con la misma semilla y los mismos datos se obtiene la misma partición.
