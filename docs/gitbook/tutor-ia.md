# Agente tutor de IA (RF-004)

- **Proveedor principal:** Groq, modelo `llama-3.3-70b-versatile` (API compatible con OpenAI).
- **Alternativo:** `llama-3.1-8b-instant` en el mismo proveedor.
- **Respaldo final:** la recomendación predefinida que el profesional configuró para la etapa.

El código sigue los patrones de la arquitectura (ADR-04):

| Patrón | Dónde |
|--------|-------|
| Adapter | `backend/app/modules/tutor/proveedores.py` (`AdaptadorOpenAICompatible`) |
| Strategy | `backend/app/modules/tutor/servicio.py` (`ServicioTutor`, cadena principal → alternativo → predefinida) |
| Factory Method | `crear_servicio()` arma la cadena desde las variables de entorno |

El prompt está versionado en `prompt.py` (`tutor-v0.1`). Cualquier cambio en el texto sube la versión,
y cada respuesta guarda proveedor, versión del modelo, versión del prompt y latencia en `interaccion_ia`.

Pendiente de decidir con el dueño del proyecto: límite de preguntas al tutor (por etapa o por intento).

## Cómo se usa en la simulación

* Antes de decidir se muestra la sugerencia configurada para la etapa (puede ser errónea a propósito, sin que la persona lo sepa).
* El botón *¿Por qué sugiere esto?* pide la explicación; las preguntas libres tienen un límite por etapa (`TUTOR_MAX_CONSULTAS_ETAPA`, por defecto 3).
* Cada respuesta queda registrada con proveedor, versión del modelo, versión del prompt y latencia.
* El tutor no revela la respuesta correcta, no da indicaciones de tratamiento y ante síntomas de alarma recomienda consultar al médico.
