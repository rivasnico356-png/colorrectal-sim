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
