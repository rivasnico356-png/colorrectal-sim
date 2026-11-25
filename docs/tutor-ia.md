# Agente tutor de IA (RF-004)

- **Proveedor principal:** Groq, modelo `openai/gpt-oss-120b` (API compatible con OpenAI), con esfuerzo de razonamiento bajo.
- **Alternativo:** `openai/gpt-oss-20b` en el mismo proveedor.
- Groq retiró `llama-3.3-70b-versatile` y `llama-3.1-8b-instant` el 16-08-2026 para cuentas gratuitas; se reemplazaron por los modelos que recomienda su página de modelos retirados.
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
