# Datasets públicos

Las imágenes no se guardan en el repositorio. Cada integrante las descarga en una carpeta `data/` (ignorada por git).

| Dataset | Uso en el proyecto | Fuente | Licencia |
|---------|--------------------|--------|----------|
| HyperKvasir | Imágenes de los casos de simulación | https://datasets.simula.no/hyper-kvasir/ (descarga en https://osf.io/mh9sj) | Verificada el 15-11-2026: CC BY 4.0; se debe citar el artículo, enlazar la licencia e indicar si se modificaron las imágenes |
| Kvasir-SEG | Entrenamiento del modelo de visión | https://datasets.simula.no/kvasir-seg | Verificada el 12-11-2026: uso restringido a fines de investigación y educativos; uso comercial prohibido sin permiso escrito; toda publicación debe citar el artículo del dataset |
| CVC-ClinicDB | Entrenamiento y validación del modelo | https://polyp.grand-challenge.org/CVCClinicDB/ | Por verificar antes de publicar |
| PolypGen | Prueba de generalización entre centros | https://www.synapse.org/ (PolypGen) | Por verificar antes de publicar |

Reglas:
- Antes de usar un dataset, el responsable confirma la licencia y anota aquí el texto exacto y la cita APA.
- Las particiones de entrenamiento, validación y prueba usan semillas fijas y se documentan en este archivo.
- Ninguna imagen se presenta como de un paciente real de la plataforma.

## Kvasir-SEG

- 1.000 imágenes de pólipos con su máscara de segmentación, en dos carpetas con el mismo nombre de archivo (46,2 MB).
- Texto de uso (fuente oficial): «The use of the Kvasir-SEG dataset is restricted for research and educational purposes. The use of the Kvasir-SEG dataset for commercial purposes is forbidden without prior written permission.»
- Colorrectal-Sim es un proyecto educativo sin fines comerciales, por eso puede usarlo.
- Se descarga en el flujo «Entrenar modelo de visión» de GitHub Actions; su huella SHA-256 y las particiones (semilla 2026, 80/10/10) quedan publicadas junto al modelo en el release `modelo-vision`.

Cita APA:

Jha, D., Smedsrud, P. H., Riegler, M. A., Halvorsen, P., de Lange, T., Johansen, D., y Johansen, H. D. (2020). Kvasir-SEG: A segmented polyp dataset. En *MultiMedia Modeling: 26th International Conference, MMM 2020* (pp. 451–462). Springer. https://doi.org/10.1007/978-3-030-37734-2_37

## HyperKvasir

- 110.079 imágenes y 374 videos de endoscopia gastrointestinal del Hospital de Bærum (Noruega); 10.662 imágenes etiquetadas en 23 clases.
- Licencia (página oficial del proyecto en OSF, de Simula Research Laboratory): «License: CC-By Attribution 4.0 International». Permite usar, compartir y adaptar las imágenes dando el crédito, enlazando la licencia (https://creativecommons.org/licenses/by/4.0/) e indicando si se hicieron cambios.
- Uso en el proyecto: imágenes y videos de los casos clínicos que cargan los profesionales. En cada recurso se registra el dataset de origen y, si la imagen se recortó o se le hizo otro cambio, se indica en la fuente.
- Ojo: Kvasir-VQA, un dataset derivado de HyperKvasir, tiene otra licencia (CC BY-NC 4.0). No se usa en el proyecto.

Cita APA:

Borgli, H., Thambawita, V., Smedsrud, P. H., Hicks, S., Jha, D., Eskeland, S. L., Randel, K. R., Pogorelov, K., Lux, M., Nguyen, D. T. D., Johansen, D., Griwodz, C., Stensland, H. K., Garcia-Ceja, E., Schmidt, P. T., Hammer, H. L., Riegler, M. A., Halvorsen, P., y de Lange, T. (2020). HyperKvasir, a comprehensive multi-class image and video dataset for gastrointestinal endoscopy. *Scientific Data, 7*, Artículo 283. https://doi.org/10.1038/s41597-020-00622-y
