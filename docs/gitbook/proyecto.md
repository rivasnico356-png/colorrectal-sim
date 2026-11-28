# Problema, objetivo y alcance

## Problema

**¿Cuál es el problema?** Las personas que reciben información sobre el cáncer colorrectal suelen encontrarse con imágenes y términos médicos difíciles de entender, y con herramientas de inteligencia artificial cuyos resultados aceptan sin cuestionarlos. Hace falta un espacio seguro para aprender a interpretar imágenes de colonoscopia y a usar la IA con criterio, sin exponer datos personales.

## Justificación

* **Para la persona usuaria:** entender sus propios estudios y la información de su enfermedad le permite conversar mejor con su médico. Un simulador deja practicar con casos y recibir retroalimentación sin riesgo, algo que una consulta médica no ofrece.
* **Para el uso de la IA:** las herramientas de IA ya están al alcance de cualquier persona y sus respuestas pueden ser erróneas. El simulador incluye sugerencias de la IA equivocadas a propósito para enseñar a verificarlas, y registra si la persona las sigue o las detecta.
* **Para la privacidad:** la práctica se hace con imágenes del dataset público y anonimizado HyperKvasir, y los estudios propios se desidentifican y cifran, según la Ley 1581 de 2012.
* **Para la ingeniería de software:** el proyecto integra un modelo de visión, un agente de IA con respaldo y una aplicación web, con prácticas medibles de calidad (TSP, pruebas automáticas e integración continua) dentro de la línea ONCO-SIM de la convocatoria ONCO-AI_USC 2026 B.

## Objetivo

Construir una plataforma web de simulación en la que la persona resuelve casos por etapas con imágenes del dataset público HyperKvasir, recibe la sugerencia de un agente tutor de IA (que a veces se equivoca a propósito para enseñar a cuestionarla) y obtiene retroalimentación inmediata, mientras se registra cómo toma decisiones junto a la IA.

## Alcance de la Release 1.0

**Incluido:** registro con autorizaciones de la Ley 1581 de 2012 (Congreso de la República de Colombia, 2012), biblioteca de casos con revisión y publicación por un profesional distinto del autor (10 escenarios de decisión en tres casos clínicos), simulación por etapas, tutor de IA con respaldo, evaluación y gamificación, progreso, vínculo con el profesional de la salud, exportación seudonimizada, estudios propios desidentificados y cifrados, y un modelo de visión experimental.

**Excluido:** uso en la atención clínica, datos de pacientes reales identificables, integración con historias clínicas y cualquier indicación de tratamiento.

## Requisitos

El SRS del proyecto (ISO/IEC/IEEE 29148, versión 1.2) define 10 requisitos funcionales con 48 sub-requisitos y 8 no funcionales. El estado de cada uno en el código está en [`docs/estado-requisitos.md`](https://github.com/rivasnico356-png/colorrectal-sim/blob/develop/docs/estado-requisitos.md).

| Requisito | Tema |
|---|---|
| RF-001 | Usuarios, autenticación, roles y vínculo con el profesional |
| RF-002 | Casos clínicos, recursos multimedia, revisión y catálogo |
| RF-003 | Simulación por etapas |
| RF-004 | Agente tutor de IA |
| RF-005 | Evaluación y retroalimentación |
| RF-006 | Niveles e insignias |
| RF-007 | Registro de la interacción humano-IA |
| RF-008 | Historial, progreso y panel del profesional |
| RF-009 | Privacidad y derechos del titular |
| RF-010 | Estudios propios |
