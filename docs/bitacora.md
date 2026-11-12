# Bitácora del proyecto

Registro con fechas (hora de Colombia; las horas son aproximadas y la hora exacta está en cada corrida de GitHub Actions) de lo que se hace en el desarrollo y las pruebas, para preparar después los documentos (Informe de Pruebas y Calidad, matriz, actas). Cada entrada dice qué se hizo, con qué evidencia y su resultado. La más reciente va arriba.

## Fechas próximas

| Fecha | Qué |
|---|---|
| 15-11-2026 | Publicar el GitBook (pendiente: cuenta de GitBook de Nicolás) |
| 23 al 25-11-2026 | Prueba de usabilidad SUS con 5 personas (Plan de Pruebas) |
| 29-11-2026 | Entrega del Informe de Pruebas y Calidad |
| Hacia el 12-12-2026 | Vence la base de datos gratuita de Render (30 días desde su creación) |

## 12-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 14:20 | Defecto: Groq retiró los modelos del tutor (`llama-3.3-70b-versatile` y `llama-3.1-8b-instant`, 16-08-2026). Se cambian por `openai/gpt-oss-120b` y `openai/gpt-oss-20b` con razonamiento bajo | Página de modelos retirados de Groq; rama fix/modelos-groq | En revisión de CI |
| 14:05 | Inicia el monitoreo de disponibilidad del enlace público (RNF-002): una consulta cada 2 horas | `.github/workflows/monitoreo.yml` | Muestras en la pestaña Actions › Monitoreo de disponibilidad |
| 13:50 | Borrador del protocolo de la prueba SUS (consentimiento, 6 tareas, cuestionario, tabla de resultados) | Documento en Claude Docs | Borrador; se aplica del 23 al 25-11 |
| 13:30 | Ciclo 2 (regresión) de la Matriz de Pruebas Unitarias: 48 casos repetidos y 4 nuevos (CP049–CP052) | Corrida 43275023226, commit 067dc1d | 52 de 52 exitosos |
| 13:15 | Copia local en el PC de Nicolás actualizada con `git pull` y `docker compose up -d --build` | Registro del backend en Docker Desktop | Script 05 aplicado; 3 contenedores en funcionamiento |
| 13:05 | Etiqueta `v0.5.0` (fin del Ciclo 1) | `git push` rechazado con error 403 | Pendiente: crearla desde GitHub › Releases |
| 13:00 | Imágenes y videos de los casos guardados en la base (db/05), con peticiones parciales para el video | Commit 067dc1d; corrida 43275023226 (41 pruebas aprobadas, cobertura 89 %) | Desplegado en Render: «Esquema: 05_recursos_en_base.sql aplicado» |
| 11:10 | Administrador del enlace público cambiado desde las variables de Render | Despliegue dep-dbqu9aoae00c73deikc0 | «Administrador inicial creado» |
| 11:00 | Defecto: el administrador no podía entrar al enlace público. Corrección: la contraseña de la variable se limpia y se sincroniza al arrancar | Commit 32d2304; prueba CP051 | Corregido |
| 10:55 | Enlace público de demostración en Render (plan gratuito): https://colorrectal-sim.onrender.com | Commit 0ed05b9; corrida de CI 43250024669 (41 pruebas aprobadas) | En línea; esquema, administrador y caso de demostración creados al arrancar |

## 11-11-2026

| Hora | Qué | Evidencia | Resultado |
|---|---|---|---|
| 22:30 | Simulador instalado en el PC de Nicolás con Docker Desktop (se instalaron WSL y Git) | Docker Desktop | Funciona en http://localhost:5173 |
| 21:50 | Seguridad repetida tras las correcciones | Corrida 43139882779, commit 8118158 | OWASP ZAP: 0 fallas, 0 avisos, 120 reglas; pip-audit y npm audit (producción): 0 vulnerabilidades |
| 21:50 | Pruebas de sistema de punta a punta con revisión de accesibilidad (axe) en 5 navegadores | Corrida 43139845153, commit 8118158 | 5 de 5 aprobadas; 0 hallazgos de axe en 10 pantallas |
| 21:30 | Defecto: aviso de ZAP por `Cross-Origin-Resource-Policy` | Corrida 43139144736; commit 8118158 | Corregido |
| 21:10 | Defectos encontrados por las pruebas de sistema: campo de archivo sin etiqueta en *Mis estudios* (crítico de axe, 5 navegadores) y botón fuera de la pantalla en Safari iPhone | Corrida 43138423496; commit 9cfaddb | Corregidos |
| 21:00 | Las pruebas de sistema no se instalaban en Ubuntu 26; los flujos se fijan en Ubuntu 24.04 | Corrida 43137928564; commit f00ac55 | Corregido |
| Tarde | Pruebas no funcionales: carga (30 usuarios, 10 min), estrés (hasta 150 usuarios), seguridad y accesibilidad | Corrida 43135272242, commit 55bbe30 | Carga: 32.532 peticiones, 0 fallas, p90 10 ms. Estrés: 51.836 peticiones, 0 fallas, p90 31 ms. Lighthouse: accesibilidad 100 |
| Durante el día | Ciclo 1 de la Matriz de Pruebas Unitarias (48 casos) | Corrida 43133324656 | 37 pruebas aprobadas, cobertura 91 % |
