# Datasets públicos

Las imágenes no se guardan en el repositorio. Cada integrante las descarga en una carpeta `data/` (ignorada por git).

| Dataset | Uso en el proyecto | Fuente | Licencia |
|---------|--------------------|--------|----------|
| HyperKvasir | Imágenes de los casos de simulación | https://datasets.simula.no/hyper-kvasir/ | Por verificar antes de publicar |
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
