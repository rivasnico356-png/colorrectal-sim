# Estado de los requisitos en el código

Trazabilidad entre el SRS v1.2, el código y las pruebas automáticas. Base para la Matriz de Pruebas Unitarias y el Plan de Pruebas.

Estados: **Implementado** (código y prueba automática), **Parcial** (falta algo indicado), **Pendiente**.

| Req. | Descripción | Estado | Código | Prueba |
|------|-------------|--------|--------|--------|
| 1.1 | Registro con autorización de datos | Implementado | `usuarios/schemas.py`, `usuarios/service.py` | `test_reglas`, `test_api` |
| 1.2 | Inicio de sesión, mensaje genérico, bloqueo | Implementado | `usuarios/service.py` | `test_api::test_bloqueo_tras_cinco_intentos` |
| 1.2b | Cierre de sesión invalida el token | Implementado | `usuarios/service.py`, `core/deps.py` | `test_flujo::test_cierre_de_sesion_invalida_el_token` |
| 1.3 | Recuperación de contraseña por correo | Implementado | `usuarios/service.py`, `core/correo.py` | `test_estudios::test_recuperacion_de_contrasena_un_solo_uso` |
| 1.4 | Control de acceso por rol | Implementado | `core/deps.py`, `App.tsx` | `test_flujo::test_solo_el_profesional_crea_casos` |
| 1.5 | Administración de usuarios | Implementado | `usuarios/router.py`, `Admin.tsx` | `test_flujo::test_administracion_de_usuarios` |
| 1.6 | Vínculo directo Usuario–Profesional | Implementado | `vinculos/router.py` | `test_flujo::test_simulacion_completa…` |
| 2.1 / 2.1b / 2.1c | Crear, editar (con versiones) y eliminar casos | Implementado | `casos/service.py` | `test_flujo::test_borrador_no_aparece_y_editar_conserva_version` |
| 2.2 | Recursos multimedia con dataset y licencia | Implementado | `casos/service.py::guardar_recurso` | Pendiente prueba automática |
| 2.3 / 2.4 | Opciones, puntaje, explicación, fuente y recomendación de la IA | Implementado | `casos/schemas.py` | `test_reglas` |
| 2.5 | Revisión por persona distinta al autor y publicación | Implementado | `casos/service.py::revisar` | `test_flujo` |
| 2.6 | Catálogo con filtros y estado | Implementado | `casos/router.py` | `test_flujo` |
| 3.1 / 3.2 | Aviso de alcance y etapas en orden | Implementado | `simulacion/service.py` | `test_flujo` |
| 3.3 / 3.3b | Visor de imagen con zoom y reproductor de video | Parcial | `Simulacion.tsx` | Falta avance cuadro a cuadro del video |
| 3.4 | Resultado del modelo de visión | Implementado* | `estudios/vision.py`, `simulacion/service.py` | `test_estudios::test_resultado_del_modelo_desde_mascara` |
| 3.5 / 3.6 | Decisión con confianza 1–5; retomar sin modificar | Implementado | `simulacion/service.py` | `test_flujo` |
| 4.1–4.5 | Recomendación, explicación, preguntas con límite, siguió/rechazó, respaldo | Implementado | `tutor/`, `simulacion/service.py` | `test_tutor`, `test_flujo` |
| 5.1–5.4 | Evaluación, puntaje, retroalimentación y resumen | Implementado | `simulacion/service.py` | `test_flujo` |
| 6.1 / 6.2 | Niveles con desbloqueo e insignias | Implementado | `gamificacion/service.py` | `test_flujo` |
| 7.1 / 7.2 | Registro de decisiones y exportación seudonimizada | Implementado | `simulacion/service.py`, `progreso/router.py` | `test_flujo` |
| 8.1–8.4 | Historial, progreso, panel agregado y avance individual | Implementado | `progreso/router.py` | `test_flujo` |
| 9.1–9.3 | Autorizaciones, consulta, rectificación y supresión | Implementado | `privacidad/router.py` | `test_flujo::test_privacidad_rectificar_y_suprimir` |
| 10.1–10.5 | Estudios propios: carga, desidentificación, interpretación, compartir, eliminar | Implementado* | `estudios/` | `test_estudios` |

\* Funciona con el modelo de visión entrenado (`vision/README.md`). Sin el archivo del modelo, la plataforma informa que no está disponible.

## No funcionales

| Req. | Estado | Evidencia o pendiente |
|------|--------|-----------------------|
| RNF-001 Rendimiento | Implementado | Carga con 30 usuarios: p90 10 ms y 0 % de errores; estrés hasta 150 usuarios sin fallas ([resultados](pruebas-no-funcionales.md)) |
| RNF-002 Disponibilidad | Pendiente | Medición durante el periodo de pruebas |
| RNF-003 Seguridad | Parcial | bcrypt, roles, secretos en variables de entorno, gitleaks, estudios cifrados, cabeceras de seguridad, OWASP ZAP sin fallas ni avisos (120 reglas), pip-audit y npm audit de producción sin vulnerabilidades. Falta HTTPS en el despliegue |
| RNF-004 Usabilidad | Pendiente | Cuestionario SUS con 5 personas |
| RNF-005 Web y móvil | Implementado | Flujo completo aprobado en Chrome, Firefox, Safari (WebKit), Chrome Android y Safari iPhone, sin desborde horizontal ([resultados](pruebas-no-funcionales.md)). Falta confirmarlo en un teléfono físico |
| RNF-006 Mantenibilidad | Parcial | Docker, CI y pruebas; faltan los tags v0.5, v0.9 y v1.0 |
| RNF-007 Transparencia de la IA | Implementado | Rótulo exacto del SRS (`core/textos.py`); versiones de modelo y prompt guardadas en `interaccion_ia` |
| RNF-008 Accesibilidad | Implementado | Lighthouse: 100 en accesibilidad (escritorio y móvil); axe sin hallazgos en las 10 pantallas del flujo en los 5 navegadores |

## Cambios que deben reflejarse en los documentos

- **Arquitectura de datos:** `db/03_ajustes_srs.sql` y `db/04_estudios_recuperacion.sql` agregan campos y tablas que pide el SRS.
- **SRS 3.5:** la confianza se pide de 1 a 5 y se guarda en el campo de 0 a 100 (multiplicada por 20).
- **SRS 7.2 y 8.3:** ya no hay grupos; la exportación y el panel usan el vínculo directo con el profesional.
