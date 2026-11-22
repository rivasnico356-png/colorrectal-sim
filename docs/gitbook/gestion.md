# Gestión del proyecto

## Identificación

| Campo | Valor |
|---|---|
| **Nombre del proyecto** | Colorrectal-Sim: plataforma web de simulación para la detección e interpretación del cáncer colorrectal mediante imágenes médicas multimodales |
| **Convocatoria** | ONCO-AI_USC 2026 B, línea 2 ONCO-SIM (Universidad Santiago de Cali) |
| **Propietario del proyecto** | Jair Enrique Sanclemente Castro, docente de Gestión de Proyectos TI |
| **Director del proyecto** | Nicolas Rivas Castillo |
| **Dónde están los documentos** | Documentos de gestión (Acta, planes, EDT, cronograma, SRS, diseño): carpeta del equipo en OneDrive y entregas en Moodle. Documentación técnica: esta página de GitBook. Código, pruebas y control de cambios: repositorio público en GitHub |

## Marco de trabajo

La dirección del proyecto sigue la Guía del PMBOK, 6.ª edición (Project Management Institute, 2017), y el desarrollo sigue el Team Software Process (Humphrey, 2000). Cada integrante registra sus tiempos y defectos en Process Dashboard.

| Integrante | Rol PMBOK | Rol TSP |
|---|---|---|
| Nicolas Rivas Castillo | Director del proyecto | Líder del equipo y gerente de planeación |
| Valentina Ramírez Solano | Analista | Gerente de proceso |
| Juan Camilo Paredes Ramírez | Diseñador | Gerente de diseño |
| David Steven Muñoz Rojas | Desarrollador | Gerente de soporte |
| María Camila Viveros Hurtado | Tester | Gerente de calidad |

## Alcance, tiempo y calidad

* **Alcance:** lo incluido y lo excluido de la Release 1.0 está en [Problema, objetivo y alcance](proyecto.md). La EDT tiene 30 paquetes de trabajo y 660 horas planeadas; el diccionario de la EDT usa exactamente los mismos códigos, nombres y paquetes que la EDT.
* **Tiempo:** tres ciclos TSP en secuencia y los hitos de la tabla de abajo.
* **Calidad:** los objetivos C-01 a C-09 del Plan de Gestión de la Calidad.

### Secuencia de la ejecución

Las actividades de la ejecución son **secuenciales**: cada fase empieza cuando termina la anterior (relación fin a inicio), y cada ciclo cierra con su postmortem antes de abrir el siguiente.

```
Diseño → Ciclo 1 (v0.5) → Ciclo 2 (v0.9) → Ciclo 3 (Release 1.0) → Pruebas de sistema y SUS → Cierre
```

Dentro de cada ciclo, el orden también es fijo: planeación del ciclo → construcción → revisión e inspección → pruebas unitarias e integración continua → postmortem.

### Hitos

Un hito marca un momento de control: tiene **duración cero** y no es una actividad de trabajo (Project Management Institute, 2017). Su criterio de aceptación se mide con las métricas de TSP del equipo y con las características de calidad del producto de la norma ISO/IEC 25010 (International Organization for Standardization, 2023).

| Hito | Fecha de la línea base | Criterio de aceptación | Métrica TSP | Característica ISO/IEC 25010 |
|---|---|---|---|---|
| 001 Registro de ideas entregado | 13/09/2026 | Documento entregado y revisado por el docente | — | — |
| 002 Acta de constitución aprobada | 04/10/2026 | Aprobación del propietario registrada en el acta | — | — |
| 003 Plan para la dirección aprobado | 19/10/2026 | Alcance, EDT, cronograma y calidad aprobados | — | — |
| 004 Decisión sobre RF-010 (estudios propios) | 23/10/2026 | Decisión del propietario registrada; si se aprueba, se actualizan la matriz, la EDT y la línea base | — | Seguridad (confidencialidad) |
| 005 Requisitos aprobados | 19/10/2026 | SRS y matriz de trazabilidad inspeccionados; tag v0.1 | Defectos de requisitos registrados en la inspección | Adecuación funcional (completitud) |
| 006 Diseño y arquitectura aprobados | 25/10/2026 | Revisión de diseño TSP y aprobación del docente | Defectos de diseño por inspección registrados | Mantenibilidad (modularidad) |
| 007 Cierre del ciclo 1 · v0.5 | 01/11/2026 | Tag v0.5, release y postmortem | Densidad de defectos en pruebas de sistema ≤ 1 por KLOC; rendimiento de remoción ≥ 70 %; cobertura ≥ 70 % | Adecuación funcional; fiabilidad |
| 008 Modelo de visión entrenado y evaluado | 07/11/2026 | Entrenamiento reproducible y métricas publicadas (C-06) | Defectos del flujo de entrenamiento en LOGD | Adecuación funcional (corrección) |
| 009 Cierre del ciclo 2 · v0.9 | 08/11/2026 | Tag v0.9, release y postmortem | Densidad ≤ 1 por KLOC; rendimiento de remoción ≥ 70 % | Eficiencia de desempeño (percentil 90 < 3 s) |
| 010 Release 1.0 | 13/11/2026 | 100 % de los requisitos Must; 0 defectos críticos abiertos | Densidad ≤ 1 por KLOC; 0 secretos en el repositorio | Seguridad; compatibilidad |
| 011 Pruebas y validación concluidas | 15/11/2026 | Informe de pruebas con SUS ≥ 68 y sin errores críticos WCAG 2.1 AA | 100 % de los casos de prueba ejecutados | Capacidad de interacción (usabilidad); fiabilidad (disponibilidad > 95 %) |
| 012 Documentación completa | 22/11/2026 | Manual de usuario, informe final y GitBook publicados | — | — |
| 013 Sustentación y cierre | 29/11/2026 | Acta de cierre firmada por el propietario | Postmortem final del proyecto | — |

{% hint style="warning" %}
Las fechas son las de la línea base del 10/10/2026. Los hitos 007 a 011 se reprogramaron en la práctica: el primer commit es del 09/11/2026. La solicitud de cambio del cronograma (tarea N3 del plan de acción) fija las fechas nuevas; cuando el propietario la apruebe, esta tabla se actualiza.
{% endhint %}

### Cronograma y valor ganado

* **Herramienta:** el cronograma se lleva en Instagantt, con las actividades de la EDT, sus dependencias fin a inicio y los hitos de duración cero.
* **Estimación:** cada tarea se estima con los datos históricos de horas de los integrantes en Process Dashboard. Si las horas reales se desvían más de ±20 % del plan, se ajustan las estimaciones del ciclo siguiente.
* **Avance semanal con Valor Ganado (EVM):**
  * El valor planeado (VP) de cada tarea es su porcentaje de las horas planeadas del ciclo.
  * Una tarea suma valor ganado (VG) solo cuando está terminada, con la regla 0/100.
  * Cada semana se calcula la desviación como VG acumulado − VP acumulado. Si llega a −10 puntos porcentuales o menos, se replanea en la reunión semanal; si afecta una entrega, se tramita una solicitud de cambio.
  * El informe semanal (WEEK) de Process Dashboard deja el registro.

## Control de versiones

Hay tres ramas permanentes:

* `develop`: integración y demostración pública.
* `qa`: pruebas antes de cada entrega.
* `main`: vacía por indicación del docente hasta la Release 1.0.

Cada tarea se trabaja en una rama temporal `feature/…`. Entra a `develop` por Pull Request revisado por otro integrante y se borra al fusionarse. Cada versión se marca con un tag.

```
feature/* → develop → qa → main
```

## Herramientas

* **GitHub:** código, defectos y GitHub Actions para la integración continua.
* **Instagantt:** cronograma.
* **Figma:** prototipo.
* **Process Dashboard:** tiempos, defectos y valor ganado de TSP.
* **GitBook:** esta documentación.
* **Render:** demostración pública.
* **Groq:** tutor de IA.
* **Brevo:** correo.

## Riesgos técnicos vigentes

* Render gratuito se duerme tras 15 minutos sin uso, y su base de datos vence hacia el 12/12/2026.
* Groq retiró los modelos Llama el 16/08/2026; se pasó a `gpt-oss`.
* Render bloquea el correo por SMTP; se pasó a la API de Brevo.
