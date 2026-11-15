# Gestión del proyecto

* **Marco:** la Guía del PMBOK (Project Management Institute, 2017) para la dirección del proyecto y el Team Software Process (Humphrey, 2000) para el desarrollo, con registro de tiempos y defectos en Process Dashboard.
* **Ciclos de desarrollo:** ciclo 1 (v0.5), ciclo 2 (v0.9) y ciclo 3 (Release 1.0), seguidos de pruebas y cierre hasta el 29/11/2026.
* **Herramientas:** GitHub (código, GitHub Actions para integración continua y defectos), Instagantt (cronograma), Figma (prototipo), Process Dashboard (tiempos y defectos TSP), GitBook (esta documentación), Render (demostración pública), Groq (tutor de IA) y Brevo (correo).
* **Control de versiones:** ramas permanentes `develop` (integración y demostración pública), `qa` (pruebas antes de cada entrega) y `main` (vacía por indicación del docente hasta la Release 1.0). Cada tarea se trabaja en una rama temporal `feature/…` que entra a `develop` por Pull Request revisado por otro integrante y se borra al fusionarse. Cada versión se marca con un tag.

```
feature/* → develop → qa → main
```
* **Calidad:** objetivos C-01 a C-09 del Plan de Gestión de la Calidad.
* **Riesgos técnicos vigentes:** Render gratuito se duerme tras 15 minutos sin uso y su base vence hacia el 12/12/2026; Groq retiró los modelos Llama el 16/08/2026 (se pasó a `gpt-oss`); Render bloquea SMTP (se pasó a Brevo).
