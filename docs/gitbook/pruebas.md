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

## Flujo de ramas

```
feature/* → develop → qa → main
```

Los defectos se registran con la plantilla del repositorio y en Process Dashboard (TSP).
