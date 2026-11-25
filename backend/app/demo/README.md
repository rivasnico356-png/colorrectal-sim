# Imágenes y Fuentes del Caso de Demostración

Imágenes de endoscopia del conjunto de datos público **HyperKvasir** (Borgli et al., 2020), licencia **CC BY 4.0**, el único dataset del proyecto. Aportadas desde el repositorio de HyperKvasir en OSF (PR #24).

## Referencia Clínica Base
* **Cita bibliográfica:** Aponte Martín, D. M., Gil Parada, F. L., Castaño Llano, R. de J., Bareño Silva, J., Ortíz Chamorro, A. X., Ibarra Burgos, J. A., Linares, J. D., Cañadas Garrido, R. A., Regino Otero, W. A., Concha Mejía, A., & Sabbagh, L. (2025). Guía colombiana de práctica clínica para el tamizaje de cáncer colorrectal adultos: actualización 2025. *Revista Colombiana de Gastroenterología, 40*(Supl. 2), 3–24. https://doi.org/10.22516/25007440.1451
* **Aplicación en la simulación:** 
  - **Etapa 1:** Definición del inicio de tamizaje en población de riesgo promedio a los 45 años.
  - **Etapa 2:** Evaluación de la calidad de preparación intestinal basada en la escala BBPS (*Boston Bowel Preparation Scale*).
  - **Etapa 3:** Vigilancia a 3 años tras resección completa de adenoma ≥ 10 mm (12 mm en el caso de estudio).

## Mapeo y Metadatos de Imágenes (HyperKvasir Dataset)

| Archivo local | Carpeta de origen en HyperKvasir | Contenido | Etapa del Caso | Licencia |
| :--- | :--- | :--- | :---: | :---: |
| `polipo_etapa1.jpg` (se toma de `modelos/ejemplo-kvasir.jpg`, variable `IMAGEN_DEMO`) | `polyps` | Pólipo identificado para tamizaje | 1 | CC BY 4.0 |
| `bbps_etapa2.jpg` (`preparacion-intestinal.jpg`) | `bbps-0-1` | Preparación intestinal (escala BBPS) | 2 | CC BY 4.0 |
| `reseccion_etapa3.jpg` (`reseccion.jpg`) | `dyed-resection-margins` | Zona de resección teñida | 3 | CC BY 4.0 |

`app/preparar.py` las guarda en la base de datos como recursos de las etapas correspondientes, con el dataset y la licencia (RF-002 2.2). `preparacion-intestinal.jpg` y `reseccion.jpg` también se usan en la etapa 2 del caso de demostración.

Pendiente: el nombre exacto de cada archivo dentro de su carpeta de HyperKvasir.

## Cita Académica del Dataset
Borgli, H., Thambawita, V., Smedsrud, P. H., Hicks, S., Jha, D., Eskeland, S. L., Randel, K. R., Pogorelov, K., Lux, M., Nguyen, D. T. D., Johansen, D., Griwodz, C., Stensland, H. K., Garcia-Ceja, E., Schmidt, P. T., Hammer, H. L., Riegler, M. A., Halvorsen, P., & de Lange, T. (2020). *HyperKvasir, a comprehensive multi-class image and video dataset for gastrointestinal endoscopy*. Scientific Data, 7(1), 283. https://doi.org/10.1038/s41597-020-00622-y
