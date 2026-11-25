# Imágenes y Fuentes del Caso de Demostración

Imágenes de endoscopia del conjunto de datos público **HyperKvasir** (Borgli et al., 2020), licencia **CC BY 4.0**, el único dataset del proyecto. Aportadas desde el repositorio de HyperKvasir en OSF (PR #24).

## Referencia Clínica Base
* **Cita bibliográfica:** Aponte-Martín, D., et al. (2025). *Recomendaciones para el tamizaje y seguimiento del cáncer colorrectal en Colombia*. Revista Colombiana de Gastroenterología / Guías de Práctica Clínica.
* **Aplicación en la simulación:** 
  - **Etapa 1:** Definición del inicio de tamizaje en población de riesgo promedio a los 45 años.
  - **Etapa 2:** Evaluación de la calidad de preparación intestinal basada en la escala BBPS (*Boston Bowel Preparation Scale*).
  - **Etapa 3:** Vigilancia a 3 años tras resección completa de adenoma ≥ 10 mm (12 mm en el caso de estudio).

## Mapeo y Metadatos de Imágenes (HyperKvasir Dataset)

| Archivo Local | Nombre Original en HyperKvasir | Contenido | Etapa del Caso | Licencia |
| :--- | :--- | :--- | :---: | :---: |
| `polipo_etapa1.jpg` | `polyps` | Pólipo identificado para tamizaje | 1 | CC BY 4.0 |
| `bbps_etapa2.jpg` (`preparacion-intestinal.jpg`) | `bbps-0-1` | Preparación intestinal (escala BBPS) | 2 | CC BY 4.0 |
| `reseccion_etapa3.jpg` (`reseccion.jpg`) | `dyed-resection-margins` | Zona de resección teñida | 3 | CC BY 4.0 |

`app/preparar.py` las guarda en la base de datos como recursos de las etapas correspondientes, con el dataset y la licencia (RF-002 2.2).

## Cita Académica del Dataset
Borgli, H., Thambawita, V., Smedsrud, P. H., Hicks, S., Jha, D., Eskeland, S. L., Randel, K. R., Pogorelov, K., Lux, M., Nguyen, D. T. D., Johansen, D., Griwodz, C., Stensland, H. K., Garcia-Ceja, E., Schmidt, P. T., Hammer, H. L., Riegler, M. A., Halvorsen, P., & de Lange, T. (2020). *HyperKvasir, a comprehensive multi-class image and video dataset for gastrointestinal endoscopy*. Scientific Data, 7(1), 283. https://doi.org/10.1038/s41597-020-00622-y
