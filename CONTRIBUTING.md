# Guía de contribución

Esta guía explica cómo trabaja el equipo **Medical programmers** en el repositorio de Colorrectal-Sim.

## Ramas

| Rama | Uso |
|------|-----|
| `main` | Versión estable. Solo recibe cambios desde `qa` cuando las pruebas de aceptación pasan (v0.5, v0.9, v1.0). |
| `qa` | Pruebas de calidad. Recibe `develop` al final de cada ciclo; aquí se ejecuta el plan de pruebas y se registran los defectos. |
| `develop` | Integración del ciclo en curso. |
| `feature/<id>-<descripcion>` | Una tarea del cronograma, por ejemplo `feature/rf004-tutor-ia`. |
| `fix/<id>-<descripcion>` | Corrección de un defecto, por ejemplo `fix/42-bloqueo-login`. |

`main`, `qa` y `develop` están protegidas: no se hace `push` directo, todo entra por Pull Request.

## Flujo de trabajo

1. Toma una tarea del tablero y crea tu rama desde `develop`.
2. Haz commits pequeños con el formato `tipo(módulo): descripción`, por ejemplo `feat(tutor): agrega cadena de respaldo`.
   Tipos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`.
3. Ejecuta las pruebas en local (`pytest` y `ruff check .` en `backend/`, `npm run build` en `frontend/`).
4. Abre un Pull Request hacia `develop` y completa la plantilla.
5. Otro integrante revisa el PR. Se fusiona cuando la revisión está aprobada y la CI pasa.

## Paso a pruebas y a producción

```
feature/* ──PR──> develop ──PR (fin de ciclo)──> qa ──PR (pruebas aprobadas)──> main
```

- **develop → qa:** al cerrar cada ciclo, el líder abre el PR. El responsable de pruebas ejecuta en `qa` los casos del plan de pruebas.
- **Defectos en qa:** se reportan con la plantilla de defecto, se corrigen en una rama `fix/*` que sale de `develop` y vuelven a pasar por `develop → qa`.
- **qa → main:** cuando los casos del ciclo pasan, el responsable de pruebas aprueba el PR y se etiqueta la versión (`v0.5`, `v0.9`, `v1.0`).

## Registro TSP

Cada integrante registra en Process Dashboard el tiempo por fase (diseño, código, revisión, pruebas) y cada defecto encontrado,
con la fase donde se inyectó y donde se eliminó. El número del PR o del issue va en el comentario del registro.

## Reglas del proyecto

- Las claves y contraseñas van solo en variables de entorno (`.env`), nunca en el código.
- Las imágenes de los datasets públicos se descargan fuera del repositorio (ver `docs/datasets.md`).
- No se usan datos inventados de pacientes.
- Todo texto que vea la persona usuaria se escribe en español claro y sin tecnicismos innecesarios.
