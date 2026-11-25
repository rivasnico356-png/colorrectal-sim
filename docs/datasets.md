# Datasets públicos

Las imágenes no se guardan en el repositorio. Cada integrante las descarga en una carpeta `data/` (ignorada por git).

El proyecto usa **un solo dataset: HyperKvasir**.

| Dataset | Uso en el proyecto | Fuente | Licencia |
|---------|--------------------|--------|----------|
| HyperKvasir | Imágenes y videos de los casos de simulación; sus 1.000 imágenes segmentadas de pólipos entrenan el modelo de visión | https://datasets.simula.no/hyper-kvasir/ (descarga completa en https://osf.io/mh9sj) | CC BY 4.0, verificada el 15-11-2026 |

Reglas:
- Antes de usar un dataset, el responsable confirma la licencia y anota aquí el texto exacto y la cita APA.
- Las particiones de entrenamiento, validación y prueba usan semillas fijas y se documentan en este archivo.
- Ninguna imagen se presenta como de un paciente real de la plataforma.

## Imágenes segmentadas de pólipos (Kvasir-SEG)

- Son la parte segmentada de HyperKvasir: 1.000 imágenes de pólipos con máscara. Simula también las publica por separado como Kvasir-SEG, y de esa página las descarga el flujo de entrenamiento.

- 1.000 imágenes de pólipos con su máscara de segmentación, en dos carpetas con el mismo nombre de archivo (46,2 MB).
- Texto de uso (fuente oficial): «The use of the Kvasir-SEG dataset is restricted for research and educational purposes. The use of the Kvasir-SEG dataset for commercial purposes is forbidden without prior written permission.»
- Colorrectal-Sim es un proyecto educativo sin fines comerciales, por eso puede usarlo.
- Se descarga en el flujo «Entrenar modelo de visión» de GitHub Actions; su huella SHA-256 y las particiones (semilla 2026, 80/10/10) quedan publicadas junto al modelo en el release `modelo-vision`.

Cita APA:

Jha, D., Smedsrud, P. H., Riegler, M. A., Halvorsen, P., de Lange, T., Johansen, D., y Johansen, H. D. (2020). Kvasir-SEG: A segmented polyp dataset. En *MultiMedia Modeling: 26th International Conference, MMM 2020* (pp. 451–462). Springer. https://doi.org/10.1007/978-3-030-37734-2_37

## HyperKvasir

- 110.079 imágenes y 374 videos de endoscopia gastrointestinal del Hospital de Bærum (Noruega); 10.662 imágenes etiquetadas en 23 clases y 1.000 imágenes de pólipos segmentadas.
- Licencia (página oficial del proyecto en OSF, de Simula Research Laboratory): «License: CC-By Attribution 4.0 International». Se da el crédito, se enlaza la licencia (https://creativecommons.org/licenses/by/4.0/) y se indica si las imágenes se modificaron.
- En cada recurso de un caso se escribe en la fuente: «HyperKvasir (Borgli et al., 2020), CC BY 4.0».
- Ojo: Kvasir-VQA, derivado de HyperKvasir, tiene otra licencia (CC BY-NC 4.0) y no se usa.

Cita APA:

Borgli, H., Thambawita, V., Smedsrud, P. H., Hicks, S., Jha, D., Eskeland, S. L., Randel, K. R., Pogorelov, K., Lux, M., Nguyen, D. T. D., Johansen, D., Griwodz, C., Stensland, H. K., Garcia-Ceja, E., Schmidt, P. T., Hammer, H. L., Riegler, M. A., Halvorsen, P., y de Lange, T. (2020). HyperKvasir, a comprehensive multi-class image and video dataset for gastrointestinal endoscopy. *Scientific Data, 7*, Artículo 283. https://doi.org/10.1038/s41597-020-00622-y
