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
| `polipo_etapa1.jpg` (`etapas/tamizaje_e1_polipo.jpg`) | `polyps` (imágenes segmentadas) | Pólipo identificado para tamizaje | 1 | CC BY 4.0 |
| `bbps_etapa2.jpg` (`etapas/tamizaje_e2_preparacion.jpg`) | `bbps-0-1` | Preparación intestinal (escala BBPS) | 2 | CC BY 4.0 |
| `reseccion_etapa3.jpg` (`etapas/tamizaje_e3_reseccion.jpg`) | `dyed-resection-margins` | Zona de resección teñida | 3 | CC BY 4.0 |

`app/preparar.py` las guarda en la base de datos como recursos de las etapas correspondientes, con el dataset y la licencia (RF-002 2.2). `preparacion-intestinal.jpg` y `reseccion.jpg` también se usan en la etapa 2 del caso de demostración.

El caso de demostración sigue usando `ejemplo-kvasir.jpg`, `preparacion-intestinal.jpg` y `reseccion.jpg`. Las etapas clínicas usan las fotos de `etapas/` (tabla siguiente).

## Fotos de las etapas clínicas (`etapas/`)

Desde la v1.0.2 cada una de las 10 etapas clínicas tiene **su propia foto** de HyperKvasir (Borgli et al., 2020), CC BY 4.0; ninguna se repite. Las extrajo el flujo `.github/workflows/imagenes-casos.yml` desde la fuente oficial (`datasets.simula.no`): las de preparación deficiente salen de `bbps-0-1`, las de resección de `dyed-resection-margins` y los pólipos de las imágenes segmentadas, elegidos entre la **partición de prueba** del modelo de visión (imágenes que no vio al entrenar). El origen exacto de cada archivo está en `etapas/manifiesto.json`. Si un caso ya estaba publicado en la demostración, `app/preparar.py` cambia su foto al arrancar sin borrar los intentos.

| Archivo | Origen en HyperKvasir | Partición del modelo |
| :--- | :--- | :--- |
| `etapas/tamizaje_e1_polipo.jpg` | `segmented-images/images/8edb3546-55a5-4b0f-8594-5525cde170b2.jpg` | prueba (Kvasir-SEG: cju8a3nhbpwnb0850d37fo2na.jpg) |
| `etapas/tamizaje_e2_preparacion.jpg` | `lower-gi-tract/quality-of-mucosal-views/bbps-0-1/1df65305-7d90-4c6e-81a3-1931610dadba.jpg` | — |
| `etapas/tamizaje_e3_reseccion.jpg` | `lower-gi-tract/therapeutic-interventions/dyed-resection-margins/852a2644-bf92-4a85-b5d0-61a1bf776b52.jpg` | — |
| `etapas/vision_e1_polipo.jpg` | `segmented-images/images/54d055a1-fb7f-4ee3-a453-6eaaf63bda1a.jpg` | prueba (Kvasir-SEG: cjyzu3reghjya0794w7pwoi50.jpg) |
| `etapas/vision_e2_preparacion.jpg` | `lower-gi-tract/quality-of-mucosal-views/bbps-0-1/9d23002b-4db9-43b6-bf96-a3b738bac0dc.jpg` | — |
| `etapas/vision_e3_reseccion.jpg` | `lower-gi-tract/therapeutic-interventions/dyed-resection-margins/0016b80d-1d3d-4fe0-ad7c-7a8e369352bb.jpg` | — |
| `etapas/senales_e1_polipo.jpg` | `segmented-images/images/27bd085b-97e2-4ddf-839b-a2473aee2faa.jpg` | prueba (Kvasir-SEG: cju3uz4o6gr9z0850lhxyxvsj.jpg) |
| `etapas/senales_e2_reseccion.jpg` | `lower-gi-tract/therapeutic-interventions/dyed-resection-margins/e047824d-8cbf-426a-8068-f7cc4ea3a254.jpg` | — |
| `etapas/senales_e3_polipo.jpg` | `segmented-images/images/4b9d3bc8-0e5c-46c1-92a2-e284fb000d3c.jpg` | prueba (Kvasir-SEG: cju8cdeazsm8h0801jxifmzur.jpg) |
| `etapas/senales_e4_preparacion.jpg` | `lower-gi-tract/quality-of-mucosal-views/bbps-0-1/00053206-b78e-4acd-b2ef-078130b71b26.jpg` | — |

## Caso 2: visión computacional (`caso_vision_polipos.json`)

Caso aportado por Valentina Ramírez (PR #36 a #38) y corregido en el PR #40. Fotos (desde la v1.0.2, una distinta por etapa; ver la tabla de `etapas/`):

| Nombre en el JSON | Archivo real | Etapa | Modelo de visión |
| :--- | :--- | :---: | :---: |
| `polipo_vision_etapa1.jpg` | `etapas/vision_e1_polipo.jpg`, pólipo | 1 | Sí |
| `preparacion_vision_etapa2.jpg` | `etapas/vision_e2_preparacion.jpg`, carpeta `bbps-0-1` | 2 | Sí (la IA se equivoca a propósito) |
| `reseccion_vision_etapa3.jpg` | `etapas/vision_e3_reseccion.jpg`, carpeta `dyed-resection-margins` | 3 | No |

Los porcentajes de confianza y el recuadro los calcula el modelo en el momento; el caso no trae cifras escritas a mano. La primera versión del caso se retira de la biblioteca porque sus tres archivos `.jpg` eran fichas de texto de OSF y no fotos. Pendiente de validación clínica.

## Caso 3: señales de alarma, antecedentes y resultados (`caso_senales_alarma.json`)

Caso de 4 etapas agregado en la v1.0.2 para completar los **10 escenarios de decisión** que fija el Acta de constitución («Se incluirá un conjunto inicial de 10 escenarios»). Cada escenario es un momento de decisión con imagen, recomendación de la IA y decisión del usuario: 3 en el caso de tamizaje, 3 en el Caso 2 y 4 en este caso. El caso de demostración tiene además 2 etapas de práctica sin contenido clínico, que no se cuentan.

| Etapa | Tema | Archivo real | Modelo de visión | IA |
| :---: | :--- | :--- | :---: | :--- |
| 1 | Señales de alarma: con síntomas no se espera la edad del tamizaje | `etapas/senales_e1_polipo.jpg`, pólipo | No | Correcta |
| 2 | Familiar de primer grado: empezar a los 40 años o 10 años antes de la edad del familiar | `etapas/senales_e2_reseccion.jpg`, carpeta `dyed-resection-margins` | No | **Equivocada a propósito** |
| 3 | Prueba inmunoquímica (FIT) positiva: se estudia con colonoscopia | `etapas/senales_e3_polipo.jpg`, pólipo | Sí | Correcta |
| 4 | Preparación inadecuada: los restos pueden ocultar pólipos | `etapas/senales_e4_preparacion.jpg`, carpeta `bbps-0-1` | No | Correcta |

Fuente: Aponte-Martín et al. (2025). Pendiente de validación clínica.

## Cita Académica del Dataset
Borgli, H., Thambawita, V., Smedsrud, P. H., Hicks, S., Jha, D., Eskeland, S. L., Randel, K. R., Pogorelov, K., Lux, M., Nguyen, D. T. D., Johansen, D., Griwodz, C., Stensland, H. K., Garcia-Ceja, E., Schmidt, P. T., Hammer, H. L., Riegler, M. A., Halvorsen, P., & de Lange, T. (2020). *HyperKvasir, a comprehensive multi-class image and video dataset for gastrointestinal endoscopy*. Scientific Data, 7(1), 283. https://doi.org/10.1038/s41597-020-00622-y
