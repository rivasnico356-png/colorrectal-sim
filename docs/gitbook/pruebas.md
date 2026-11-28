# Pruebas y calidad

## Integración continua

Cada cambio en GitHub ejecuta tres revisiones automáticas: **backend** (estilo con ruff y pruebas con cobertura sobre PostgreSQL 16; la revisión falla si la cobertura baja del 70 %), **frontend** (compilación) y **secretos** (gitleaks). Los cambios entran a `develop` por Pull Request revisado por otro integrante y con las tres revisiones en verde.

## Resultados

| Indicador | Ciclo 1 (11/11/2026) | Ciclo 2 (22/11/2026) | Ciclo 3 (25/11/2026) | Cierre (28/11/2026) |
|---|---|---|---|---|
| Pruebas automáticas del backend | 37 aprobadas | 74 aprobadas | 83 aprobadas | 89 aprobadas, 0 fallidas |
| Cobertura del backend | 91 % | 90,76 % | 90,83 % | 91 % |
| Casos de la Matriz de Pruebas Unitarias (42) | 30 aprobados, 7 parciales, 5 sin ejecutar | 41 aprobados | 42 aprobados | 42 aprobados |

Los ciclos 2 y 3 los ejecutó María Camila Viveros (tester). La matriz con el detalle de cada caso está en la carpeta de pruebas del equipo.

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

Además, un monitoreo automático (`monitoreo.yml`) revisa cada 2 horas que la demostración pública responda.

El detalle, con los defectos que se encontraron y cómo se corrigieron, está en `docs/pruebas-no-funcionales.md` del repositorio.

## Usabilidad (SUS)

Cinco personas usaron la plataforma y respondieron el cuestionario SUS entre el 25 y el 27/11/2026. Puntajes: 82,5; 92,5; 52,5; 82,5 y 32,5. **Promedio: 68,5** (criterio C-04: SUS ≥ 68), por lo que RNF-004 se cumple.

## Pendiente después del cierre

| Prueba | Motivo |
|---|---|
| Latencia de inferencia del modelo de visión en el servidor | No se midió por separado de la carga del estudio |
| Generalización del modelo con un dataset externo (por ejemplo, PolypGen) | Exige registro; queda como recomendación |

El Informe de Pruebas y Calidad del proyecto (29/11/2026) reúne todos los resultados.

## Flujo de ramas

```
feature/* → develop → qa → main
```

Los defectos se registran con la plantilla del repositorio y en Process Dashboard (TSP).
