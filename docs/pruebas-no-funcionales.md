# Resultados de las pruebas no funcionales

Ejecutadas el 11/11/2026 con el flujo **Pruebas no funcionales** de GitHub Actions sobre la versión 0.5 (`develop` = `qa`). Desde el commit f00ac55 los flujos corren en Ubuntu 24.04, porque Playwright 1.48 no instala sus dependencias en Ubuntu 26.04.
Los reportes completos (HTML y CSV) quedan como artefactos de cada corrida en la pestaña *Actions*.

| Corrida | Commit | Qué incluye |
|---|---|---|
| [43135272242](https://github.com/rivasnico356-png/colorrectal-sim/actions/runs/43135272242) | 55bbe30 | Carga, estrés, seguridad y accesibilidad |
| [43139845153](https://github.com/rivasnico356-png/colorrectal-sim/actions/runs/43139845153) | 8118158 | Sistema de punta a punta en 5 navegadores con axe en cada pantalla |
| [43139882779](https://github.com/rivasnico356-png/colorrectal-sim/actions/runs/43139882779) | 8118158 | Seguridad repetida tras las correcciones |
| [43135084289](https://github.com/rivasnico356-png/colorrectal-sim/actions/runs/43135084289) | c9c14e9 | Seguridad y accesibilidad (la carga falló por datos sintéticos con dominio inválido; se corrigió) |

## Carga (RNF-001) · Locust, 30 usuarios concurrentes durante 10 minutos

| Operación | Peticiones | Fallas | p90 |
|---|---|---|---|
| Ver etapa | 8.868 | 0 | 7 ms |
| Catálogo | 7.374 | 0 | 5 ms |
| Decidir | 5.912 | 0 | 9 ms |
| Tutor | 5.912 | 0 | 13 ms |
| Iniciar intento | 2.956 | 0 | 5 ms |
| Progreso | 1.450 | 0 | 6 ms |
| Registro | 30 | 0 | 350 ms |
| Inicio de sesión | 30 | 0 | 290 ms |
| **Total** | **32.532** | **0 (0 %)** | **10 ms** |

**Resultado: cumple RNF-001** (p90 menor a 3 s y menos de 1 % de errores).

## Estrés · Locust, de 30 a 150 usuarios en escalones de 30 (60 s cada uno) y recuperación con 30

| Total de peticiones | Fallas | p90 global | p90 más alto |
|---|---|---|---|
| 51.836 | 0 (0 %) | 31 ms | Registro 1.700 ms e inicio de sesión 1.400 ms |

Con 150 usuarios (5 veces la carga del requisito) no se alcanzó el punto de quiebre. Las operaciones más lentas son el registro y el inicio de sesión, por el cálculo intencionalmente costoso del hash de la contraseña (bcrypt). Después del estrés la API respondió normalmente (`/salud`).

## Seguridad

| Prueba | Resultado | Acción |
|---|---|---|
| OWASP ZAP sobre la API (OpenAPI) | 0 fallas, 118 reglas aprobadas, 2 avisos: faltaban las cabeceras `X-Content-Type-Options` y `Cross-Origin-Resource-Policy` | Se agregaron esas cabeceras, `X-Frame-Options` y `Referrer-Policy`, con prueba automática (`test_cabeceras_de_seguridad`) |
| pip-audit (dependencias de Python) | 133 avisos conocidos en 6 paquetes (versiones fijadas en 2024) | Se actualizaron FastAPI 0.162.5, Starlette 1.10.0, PyJWT 2.15.1, python-multipart 0.0.33, cryptography 50.0.2, Pillow 13.0.0 y pydicom 3.0.2; las 38 pruebas pasan |
| npm audit (dependencias de producción del frontend) | 0 vulnerabilidades | Las herramientas de compilación se actualizan a la última versión 5.x de Vite |
| gitleaks (secretos en el repositorio) | 0 secretos | — |

### Repetición tras las correcciones (corrida 43139882779, commit 8118158)

| Prueba | Resultado |
|---|---|
| OWASP ZAP sobre la API | 0 fallas, 0 avisos, 120 reglas aprobadas. En la repetición intermedia (43139144736) quedó un aviso: ZAP solo acepta `Cross-Origin-Resource-Policy: same-origin`; se dejó `same-origin` en la API y `same-site` solo en `/media`, que el frontend muestra con `<img>` y `<video>` desde otro puerto |
| pip-audit | Sin vulnerabilidades conocidas |
| npm audit (producción) | 0 vulnerabilidades. La instalación completa reporta 2 avisos (1 moderado, 1 alto) en herramientas de desarrollo que no se incluyen en la aplicación compilada |

## Accesibilidad y compatibilidad (RNF-005, RNF-008) · Lighthouse 12 sobre la pantalla de inicio

| Vista | Accesibilidad | Buenas prácticas | Rendimiento |
|---|---|---|---|
| Escritorio | 100 | 96 | 100 |
| Móvil | 100 | 96 | 100 |

## Sistema de punta a punta y accesibilidad por pantalla (RNF-005, RNF-008) · Playwright 1.48 y axe-core 4.10

La prueba `e2e/pruebas/flujo-usuario.spec.ts` recorre el flujo completo de la persona usuaria con el caso sintético: registro, inicio de sesión, catálogo, aviso de alcance, dos etapas con consulta al tutor, decisión y retroalimentación, resumen, progreso, estudios propios y privacidad. En cada pantalla revisa WCAG 2.1 A y AA con axe y falla si hay errores críticos. En la etapa también verifica que la página no se desborde a lo ancho.

| Navegador | Resultado | Hallazgos de axe (10 pantallas) |
|---|---|---|
| Chrome (escritorio) | Pasa | Ninguno |
| Firefox (escritorio) | Pasa | Ninguno |
| Safari, motor WebKit (escritorio) | Pasa | Ninguno |
| Chrome Android (Pixel 5) | Pasa | Ninguno |
| Safari iPhone (iPhone 12) | Pasa | Ninguno |

Defectos encontrados y corregidos en el camino:

| Corrida | Hallazgo | Corrección |
|---|---|---|
| [43138423496](https://github.com/rivasnico356-png/colorrectal-sim/actions/runs/43138423496) | Error crítico de axe en *Mis estudios*: el campo de archivo no tenía etiqueta (en los 5 navegadores) | Etiqueta “Archivo del estudio”; también se etiquetó el campo de archivo del editor de casos |
| [43138423496](https://github.com/rivasnico356-png/colorrectal-sim/actions/runs/43138423496) | En Safari iPhone el botón “¿Por qué sugiere esto?” quedaba fuera de la pantalla | Las columnas y rejillas ya no se ensanchan por contenido largo (`min-width: 0`, imágenes y videos con ancho máximo); la prueba verifica que no haya desborde horizontal |

Edge usa el mismo motor que Chrome (Chromium), por eso no se prueba aparte. Las pruebas en teléfonos son emulaciones de Playwright (tamaño de pantalla, toque y agente de usuario); falta confirmarlas en un teléfono físico durante la prueba de usabilidad.

## Alcance y limitaciones

Las pruebas se ejecutaron en servidores de GitHub Actions (2 procesos de la API y PostgreSQL 16 en la misma máquina), sin red externa de por medio y con el tutor en modo de explicación predefinida (sin llamadas al proveedor de IA). Los tiempos en un servidor real pueden ser mayores; el criterio de 3 s deja margen amplio. Los datos fueron sintéticos y se crearon solo para estas pruebas.
