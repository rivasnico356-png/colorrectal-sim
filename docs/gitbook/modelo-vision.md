# Modelo de visión (IE-04, RF-003 3.4 y RF-010 10.3)

## Qué hace

Mira una imagen de colonoscopia y **marca con un recuadro la zona que se parece a un pólipo**. Junto al recuadro muestra un porcentaje de confianza: qué tanto se parece lo que ve a los ejemplos con que aprendió. No es la probabilidad de tener cáncer.

> Resultado experimental de apoyo a la detección e interpretación; no reemplaza la valoración de su médico.

## Con qué aprendió: HyperKvasir

El proyecto usa un solo dataset público: **HyperKvasir** (Borgli et al., 2020), del Hospital de Bærum (Noruega) y Simula Research Laboratory, con licencia CC BY 4.0.

| Dato | Valor |
|---|---|
| Dataset | **HyperKvasir**: imágenes y videos reales de endoscopia gastrointestinal |
| Parte usada para el modelo | Las **1.000 imágenes de pólipos con su máscara de segmentación**, marcadas a mano por expertos. Simula también publica esta parte por separado con el nombre Kvasir-SEG (Jha et al., 2020) |
| Fuente | https://datasets.simula.no/hyper-kvasir/ |
| Licencia | CC BY 4.0: se cita el artículo, se enlaza la licencia y se indica si las imágenes se modificaron |
| Reparto | 800 imágenes para entrenar, 100 para ajustar y 100 para el examen final, con semilla fija 2026 |

## Qué tipo de modelo es

Una **U-Net** con codificador **MobileNetV2**: un modelo liviano que primero reconoce formas en la imagen y luego ubica, punto por punto, dónde está el pólipo. Corre en un servidor normal, sin tarjeta gráfica. Se guardó en formato **ONNX** (un archivo de 26 MB) que el backend carga directamente.

## Cómo se entrenó

En **GitHub Actions**, sin instalar nada:

1. En GitHub, abre **Actions › Entrenar modelo de visión › Run workflow** sobre la rama `develop`.
2. El flujo descarga las 1.000 imágenes segmentadas de pólipos (publicadas por Simula como Kvasir-SEG), entrena 30 épocas en CPU (cerca de 1,5 horas) y comprueba que el modelo ONNX carga bien.
3. Publica el resultado en el release **modelo-vision** del repositorio: `vision.onnx`, `vision.json`, `particiones.json`, la huella SHA-256 del dataset y una imagen de ejemplo.
4. La demostración en Render descarga esos archivos cada vez que se construye.

## Cómo le fue

Versión `polipos-unet-mobilenet_v2-20261112`, evaluada con las **100 imágenes del examen final**, que el modelo nunca vio al entrenar:

| Métrica | Resultado | Qué significa |
|---|---|---|
| Dice | **0,872** | La zona que marca el modelo y la que marcó el experto coinciden en cerca de un 87 % |
| IoU | **0,805** | La misma coincidencia, medida de forma más estricta |

## Limitaciones

* **Reparto por imagen, no por paciente:** el dataset no dice de qué paciente es cada imagen. Si dos imágenes del mismo paciente quedaron una para entrenar y otra para el examen, el resultado puede ser algo más alto de lo real.
* No se ha probado con imágenes de otros hospitales ni se ha medido cuánto tarda en responder en el servidor.
* No reemplaza la valoración médica ni dice si una lesión es cáncer: solo señala una zona.

## Usarlo en el entorno local

Descarga `vision.onnx` y `vision.json` del release **modelo-vision** y cópialos a `backend/modelos/`. Sin ellos la plataforma funciona igual y avisa que el modelo no está disponible. En PowerShell, dentro de la carpeta `colorrectal-sim`:

```powershell
mkdir backend\modelos -Force
$r = "https://github.com/rivasnico356-png/colorrectal-sim/releases/download/modelo-vision"
Invoke-WebRequest "$r/vision.onnx" -OutFile backend\modelos\vision.onnx
Invoke-WebRequest "$r/vision.json" -OutFile backend\modelos\vision.json
docker compose up -d --build
```

## Reproducibilidad (Plan de Calidad, C-06)

`vision.json` guarda la versión del modelo, la semilla, los hiperparámetros, las versiones de las librerías y las métricas. `particiones.json` dice qué imagen quedó en cada parte. Con la misma semilla y los mismos datos se obtiene el mismo reparto.
