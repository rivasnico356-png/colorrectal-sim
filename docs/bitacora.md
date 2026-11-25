# Bitácora del proyecto

Registro con fechas (hora de Colombia; las horas son aproximadas y la hora exacta está en cada corrida de GitHub Actions) de lo que se hace en el desarrollo y las pruebas, para preparar después los documentos (Informe de Pruebas y Calidad, matriz, actas). Cada entrada dice qué se hizo, con qué evidencia y su resultado. La más reciente va arriba.

## Fechas próximas

| Fecha | Qué |
|---|---|
| 15-11-2026 | GitBook publicado: https://colorrectal-sim.gitbook.io/colorrectal-sim-docs/ |
| 23 al 25-11-2026 | Prueba de usabilidad SUS con 5 personas (Plan de Pruebas) |
| 29-11-2026 | Entrega del Informe de Pruebas y Calidad |
| Hacia el 12-12-2026 | Vence la base de datos gratuita de Render (30 días desde su creación) |

## 24-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 19:55 | Disponibilidad del enlace público (RNF-002) calculada con el monitoreo: 38 de 38 muestras exitosas del 12-11 al 24-11 | GitHub Actions › Monitoreo de disponibilidad | 100 % (meta: más de 95 %) |
| 19:52 | PR #27: pruebas de gamificación (CP042, cambio de nivel, y reglas de insignias como pruebas unitarias puras) | PR #27 | Abierto; espera aprobación de María Camila o David |
| 19:43 | Plan de cierre con las tareas de cada integrante para el 24 y 25-11 | Documento en Claude Docs | Compartido con el equipo |
| 19:37 | PR #26 fusionado con la aprobación de Valentina: el caso de tamizaje se publica solo en la biblioteca, con imágenes de HyperKvasir en sus 3 etapas | PR #26; CI del commit e089f5c | Fusionado; Render lo publica al arrancar |
| 16:13 | PR #25 de Valentina fusionado: archivo `caso_tamizaje.json` con el caso de tamizaje de 3 etapas | PR #25 | Fusionado |

## 23-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 23:54 | Lecciones aprendidas entregadas en Moodle (35 lecciones de los 5 integrantes) | Moodle › Cargar Lecciones Aprendidas | Enviado para calificar |
| 18:50 | PR #24 de Valentina ajustado y fusionado: las imágenes de HyperKvasir se cargan en la base desde `preparar.py`; se quitaron un archivo de prueba y una ficha de texto guardada como .jpg | PR #24 | Fusionado; 76 pruebas aprobadas |
| 18:38 | PR #23 fusionado con la aprobación de Valentina: la escala de confianza se lee bien en pantallas anchas. Cierra el issue #18 | PR #23, issue #18 | Fusionado |
| 14:00 | Defecto reportado por Valentina: las etiquetas de la escala de confianza se partían letra por letra en pantallas anchas | Issue #18 | Corregido en el PR #23 |

## 22-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 22:17 | PR #22, #16 y #12 fusionados con la aprobación de María Camila: correcciones de la entrega del 15-11, mensajes claros al registrarse y bitácora del 15-11 | PR #22, #16, #12 | Fusionados |
| 22:15 | Matriz de Pruebas Unitarias corregida y entregada de nuevo en Moodle (CP012, CP013 y CP042, y códigos de requisito según la trazabilidad) | Moodle › Cargar Matriz de Pruebas Unitarias | Enviado para calificar |
| 17:02 | Ciclo 2 de pruebas ejecutado por María Camila Viveros | Corrida CI #192, commit 94ecce7 | 74 pruebas aprobadas, 0 fallidas; cobertura 90,76 % |

## 21-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 19:25 | PR #19, #20 y #21 de Juan Camilo fusionados: logo, arquitectura del sistema y del software v1.1, glosario médico y control de tamaño de letra | PR #19, #20, #21 | Fusionados |

## 17-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 10:03 | PR #14 de Juan Camilo (política de tratamiento de datos) y PR #15 de David (la CI falla si la cobertura baja del 70 %) fusionados | PR #14, #15 | Fusionados |
| Durante el día | Plan de acción: solicitudes de cambio SC-01 (cronograma), SC-02 (RF-010) y SC-03 (vínculo por correo), acta v1.1 y protección de las ramas `develop`, `qa` y `main` | Documentos del plan de acción; GitHub › Branches | Hecho; firmas del profesor pendientes |

## 15-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 18:20 | Limpieza de ramas temporales del día: quedan solo `main`, `develop`, `qa` y `feature/desarrollo` | GitHub › Branches | Hecho |
| 18:19 | PR #11 fusionado en `develop`: aprobado por María Camila Viveros. Une los PR #7, #8 y #10, que se cerraron | PR #11 | GitBook y Render se actualizan solos |
| 18:16 | PR #6 de David Muñoz (volumen para los estudios y base solo en localhost) fusionado con la aprobación de María Camila. Queda pendiente la prueba manual con Docker (Nicolas) | PR #6 | Fusionado |
| 17:50 | HyperKvasir como único dataset: catálogo de la base con un solo dataset y licencia CC BY 4.0 verificada (`db/07_solo_hyperkvasir.sql`); el modelo de visión usa sus 1.000 imágenes segmentadas de pólipos | PR #10 → #11 · `docs/datasets.md` | 74 pruebas, cobertura 91 % |
| 17:30 | Retroalimentación del docente en Moodle aplicada al GitBook: identificación, alcance, tiempo y calidad, roles TSP, ejecución secuencial, hitos con duración cero y criterios TSP/ISO 25010, Valor Ganado, justificación, módulos pendientes de aprobación; página del modelo de visión en lenguaje sencillo; revisión completa de las 13 páginas | PR #7 → #11 | Pendientes: enlace de Instagantt, antecedentes e informe de uso de IA |
| 17:10 | Los 8 patrones del documento 1.3.2.2 implementados en el backend con los nombres del documento (Adapter, Factory Method, Strategy, Facade, State, Observer con 3 observadores, Chain of Responsibility y Template Method) | PR #8 → #11 · `tests/test_patrones.py` | CI en verde |
| 14:35 | Revisión de la retroalimentación del docente en Moodle (Gestión de Proyectos TI): notas y comentarios de diseño, arquitectura, base de datos, planeación y SRS | Moodle | Base para las correcciones del día |
| 13:45 | Invitación a GitBook de los 4 integrantes como editores | GitBook › Members | Hecho |
| 14:10 | GitBook actualizado con el estado real: enlace de la demostración en la portada, 23 tablas y scripts 05–06, arquitectura con despliegue en Render y correo por Brevo, variables nuevas, modelo MobileNetV2 (Dice 0,872) con sus limitaciones, 47 pruebas y 90 % de cobertura, roles PMBOK y TSP, herramientas y riesgos. Invitados a GitBook los 4 integrantes como editores | Rama `feature/gitbook-actualizado` con Pull Request | En revisión |
| 13:00 | Limpieza de ramas: quedan las permanentes `main`, `develop` y `qa`, más `feature/desarrollo` creada desde `develop` para el trabajo nuevo. Las 23 ramas temporales (docs/, feature/, fix/) ya estaban fusionadas en `develop` y se borraron desde GitHub › Branches | Revisión con `git merge-base --is-ancestor`; `git ls-remote` muestra solo 4 ramas | Hecho |
| 12:30 | GitBook publicado con Git Sync en la rama `develop` (espacio en español sobre `docs/gitbook/`). Se agregó `gitbook-docs.yaml`, que pide el nuevo Git Sync de sitios de GitBook | https://colorrectal-sim.gitbook.io/colorrectal-sim-docs/; commit f8128d4 | Publicado |

## 14-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 21:00 | PR #5 de David (supresión de la cuenta borra los estudios, RF-009 9.3) revisado y fusionado en `develop` | PR #5; commit 7ff2961 | Fusionado |

## 12-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 19:10 | Defecto: el correo de recuperación de contraseña no llegaba. Causa: no había servidor de correo y el plan gratuito de Render bloquea SMTP desde septiembre de 2025. Se agrega el envío por la API HTTPS de Brevo | Changelog de Render; rama fix/correo-por-api | Falta la cuenta de Brevo y el remitente verificado |
| 16:45 | Modelo de visión entrenado: U-Net con MobileNetV2, Kvasir-SEG 800/100/100, semilla 2026, 30 épocas en CPU. Prueba: Dice 0,872, IoU 0,805. ONNX de 26 MB verificado con onnxruntime y publicado en el release `modelo-vision` | Corrida 43298585293 (prueba corta previa: 43297514297, 1 época, Dice 0,658) | Hecho |
| 15:35 | Rama `main` vaciada por indicación del profesor: queda solo un README y recibe la versión 1.0 al cierre. La rama principal de GitHub sigue siendo `develop` | Commit 719af89 en `main` (el historial anterior se conserva) | Hecho |
| 15:20 | Licencia de Kvasir-SEG verificada en la fuente oficial (uso educativo permitido, con cita). Se agrega el flujo «Entrenar modelo de visión» en GitHub Actions (CPU, U-Net con MobileNetV2) | https://datasets.simula.no/kvasir-seg; `.github/workflows/entrenar-vision.yml` | En curso |
| 14:55 | Tutor con IA real en el enlace público: responde `openai/gpt-oss-120b` en 767 ms (1,7 s con la red). Se ajusta para responder en texto plano (prompt tutor-v0.3) | Prueba en https://colorrectal-sim.onrender.com; commits 8e900ed y siguiente | Funciona |
| 14:45 | Defecto: la variable `IA_API_KEY` no existía en Render (el tutor usaba la explicación predefinida). Se agrega el registro del motivo de falla del proveedor | Registro de Render: «No hay clave de API configurada»; commit 8e900ed | Corregido al crear la variable |
| 14:20 | Defecto: Groq retiró los modelos del tutor (`llama-3.3-70b-versatile` y `llama-3.1-8b-instant`, 16-08-2026). Se cambian por `openai/gpt-oss-120b` y `openai/gpt-oss-20b` con razonamiento bajo | Página de modelos retirados de Groq; commit 78f84fc; corrida 43285732686 | CI aprobado (42 pruebas); falta la clave de Groq en Render para probarlo en vivo |
| 14:05 | Inicia el monitoreo de disponibilidad del enlace público (RNF-002): una consulta cada 2 horas | `.github/workflows/monitoreo.yml` | Muestras en la pestaña Actions › Monitoreo de disponibilidad |
| 13:50 | Borrador del protocolo de la prueba SUS (consentimiento, 6 tareas, cuestionario, tabla de resultados) | Documento en Claude Docs | Borrador; se aplica del 23 al 25-11 |
| 13:30 | Ciclo 2 (regresión) de la Matriz de Pruebas Unitarias: 48 casos repetidos y 4 nuevos (CP049–CP052) | Corrida 43275023226, commit 067dc1d | 52 de 52 exitosos |
| 13:15 | Copia local en el PC de Nicolas actualizada con `git pull` y `docker compose up -d --build` | Registro del backend en Docker Desktop | Script 05 aplicado; 3 contenedores en funcionamiento |
| 13:05 | Etiqueta `v0.5.0` (fin del Ciclo 1) | `git push` rechazado con error 403 | Pendiente: crearla desde GitHub › Releases |
| 13:00 | Imágenes y videos de los casos guardados en la base (db/05), con peticiones parciales para el video | Commit 067dc1d; corrida 43275023226 (41 pruebas aprobadas, cobertura 89 %) | Desplegado en Render: «Esquema: 05_recursos_en_base.sql aplicado» |
| 11:10 | Administrador del enlace público cambiado desde las variables de Render | Despliegue dep-dbqu9aoae00c73deikc0 | «Administrador inicial creado» |
| 11:00 | Defecto: el administrador no podía entrar al enlace público. Corrección: la contraseña de la variable se limpia y se sincroniza al arrancar | Commit 32d2304; prueba CP051 | Corregido |
| 10:55 | Enlace público de demostración en Render (plan gratuito): https://colorrectal-sim.onrender.com | Commit 0ed05b9; corrida de CI 43250024669 (41 pruebas aprobadas) | En línea; esquema, administrador y caso de demostración creados al arrancar |

## 11-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 22:30 | Simulador instalado en el PC de Nicolas con Docker Desktop (se instalaron WSL y Git) | Docker Desktop | Funciona en http://localhost:5173 |
| 21:50 | Seguridad repetida tras las correcciones | Corrida 43139882779, commit 8118158 | OWASP ZAP: 0 fallas, 0 avisos, 120 reglas; pip-audit y npm audit (producción): 0 vulnerabilidades |
| 21:50 | Pruebas de sistema de punta a punta con revisión de accesibilidad (axe) en 5 navegadores | Corrida 43139845153, commit 8118158 | 5 de 5 aprobadas; 0 hallazgos de axe en 10 pantallas |
| 21:30 | Defecto: aviso de ZAP por `Cross-Origin-Resource-Policy` | Corrida 43139144736; commit 8118158 | Corregido |
| 21:10 | Defectos encontrados por las pruebas de sistema: campo de archivo sin etiqueta en *Mis estudios* (crítico de axe, 5 navegadores) y botón fuera de la pantalla en Safari iPhone | Corrida 43138423496; commit 9cfaddb | Corregidos |
| 21:00 | Las pruebas de sistema no se instalaban en Ubuntu 26; los flujos se fijan en Ubuntu 24.04 | Corrida 43137928564; commit f00ac55 | Corregido |
| Tarde | Pruebas no funcionales: carga (30 usuarios, 10 min), estrés (hasta 150 usuarios), seguridad y accesibilidad | Corrida 43135272242, commit 55bbe30 | Carga: 32.532 peticiones, 0 fallas, p90 10 ms. Estrés: 51.836 peticiones, 0 fallas, p90 31 ms. Lighthouse: accesibilidad 100 |
| Durante el día | Ciclo 1 de la Matriz de Pruebas Unitarias (48 casos) | Corrida 43133324656 | 37 pruebas aprobadas, cobertura 91 % |
