# Pruebas y calidad

## Integración continua

Cada cambio en GitHub ejecuta tres revisiones automáticas: **backend** (estilo con ruff y pruebas con cobertura sobre PostgreSQL 16), **frontend** (compilación) y **secretos** (gitleaks). Las ramas `main` y `develop` solo aceptan cambios por Pull Request con las tres en verde.

## Resultado del ciclo 1 (11/11/2026)

| Indicador | Valor |
|---|---|
| Pruebas automáticas | 37 aprobadas, 0 fallidas |
| Casos en la Matriz de Pruebas Unitarias | 48 |
| Cobertura del backend | 91 % |

## Tipos de prueba del plan

Funcionales: unitarias, integración, sistema, aceptación y regresión. No funcionales: rendimiento, carga, estrés, seguridad, usabilidad (SUS) y compatibilidad, basadas en el modelo de calidad de la ISO/IEC 25010 (International Organization for Standardization, 2023) y con los criterios del Plan de Gestión de la Calidad (por ejemplo, percentil 90 menor a 3 s con 30 usuarios y SUS mayor o igual a 68).

## Pruebas no funcionales ejecutadas (11/11/2026)

| Prueba | Herramienta | Resultado |
|---|---|---|
| Carga, 30 usuarios por 10 minutos | Locust | 32.532 peticiones, 0 fallas, percentil 90 de 10 ms |
| Estrés, hasta 150 usuarios | Locust | 51.836 peticiones, 0 fallas; la API se recuperó |
| Seguridad de la API | OWASP ZAP | 0 fallas y 0 avisos en 120 reglas |
| Dependencias | pip-audit y npm audit | Sin vulnerabilidades conocidas en lo que usa la aplicación |
| Sistema de punta a punta | Playwright | Flujo completo aprobado en Chrome, Firefox, Safari, Chrome Android y Safari iPhone |
| Accesibilidad | axe y Lighthouse | Sin hallazgos en las 10 pantallas del flujo; Lighthouse 100 en accesibilidad |

El detalle, con los defectos que se encontraron y cómo se corrigieron, está en `docs/pruebas-no-funcionales.md` del repositorio.

## Flujo de ramas

```
feature/* → develop → qa → main
```

Los defectos se registran con la plantilla del repositorio y en Process Dashboard (TSP).
