# Agente tutor de IA (RF-004)

## Modelos

| Orden | Modelo | Cuándo se usa |
|---|---|---|
| 1. Principal | Groq, `openai/gpt-oss-120b` (API compatible con OpenAI), con esfuerzo de razonamiento bajo | Siempre que responda dentro del tiempo límite (8 s) |
| 2. Alternativo | Groq, `openai/gpt-oss-20b` | Si el principal falla o tarda |
| 3. Respaldo final | La explicación predefinida que el profesional escribió para la etapa | Si ninguno de los dos responde; así la simulación nunca se bloquea |

Groq retiró `llama-3.3-70b-versatile` y `llama-3.1-8b-instant` el 16-08-2026 para cuentas gratuitas; se reemplazaron por los modelos que recomienda su página de modelos retirados.

## Cómo se usa en la simulación

* Antes de decidir se muestra la sugerencia configurada para la etapa. Puede ser errónea a propósito, sin que la persona lo sepa.
* El botón *¿Por qué sugiere esto?* pide la explicación. Las preguntas libres tienen un límite de **3 por etapa** (`TUTOR_MAX_CONSULTAS_ETAPA`).
* El tutor no revela la respuesta correcta, no da indicaciones de tratamiento y ante síntomas de alarma recomienda consultar al médico. Responde en texto plano y lenguaje sencillo.

## Qué pasa con cada pregunta

Todas las consultas entran por la fachada del tutor (`FachadaTutor`), que hace siempre los mismos pasos:

1. **Arma el contexto del caso** sin datos de la persona.
2. **Valida la pregunta** con una cadena de reglas (Chain of Responsibility):
   * Longitud: de 2 a 500 caracteres.
   * Límite: 3 preguntas por etapa.
   * Tema: rechaza intentos de cambiarle las reglas o el papel al tutor.
   * Seguridad: rechaza correos, teléfonos, números de documento y pedidos de tratamiento o medicamentos.

   Si la pregunta no cumple tema o seguridad, **no se envía a la IA**: la persona recibe una respuesta guía y no gasta pregunta.
3. **Pide la respuesta** al modelo principal, al alternativo o a la explicación predefinida, en ese orden (Strategy).
4. **La rotula** como resultado experimental.
5. **La registra** en `interaccion_ia` con el proveedor, la versión del modelo, la versión del prompt y la latencia.

## Código

| Archivo (`backend/app/modules/tutor/`) | Qué tiene |
|---|---|
| `fachada.py` | `FachadaTutor`: `recomendar` y `responder_pregunta` |
| `validacion.py` | La cadena de validación |
| `servicio.py` | `ServicioTutor` y las estrategias |
| `proveedores.py` | Adaptadores de IA y `FabricaProveedores` |
| `prompt.py` | El prompt del sistema, versionado (`tutor-v0.3`). Cualquier cambio en el texto sube la versión |
