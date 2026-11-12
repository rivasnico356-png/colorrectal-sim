"""Pruebas de integración del flujo completo (requieren PostgreSQL con el esquema cargado).

Los casos de estas pruebas son datos de prueba del software, no contenido clínico.
"""
from tests.conftest import correo, crear_profesional, registrar_usuario, requiere_db, token

API = "/api/v1"


def _opcion(texto, puntaje, correcta=False, ia=False):
    return {"texto": texto, "puntaje": puntaje, "es_correcta": correcta, "recomendada_ia": ia,
            "retroalimentacion": f"Explicación de prueba para {texto}.", "fuente": "Fuente de prueba"}


def publicar_caso(cliente, autor, revisor, nivel=1) -> int:
    r = cliente.post(f"{API}/editor/casos", headers=autor, json={
        "titulo": "Caso de prueba del software", "tema": "pólipos", "nivel_dificultad": nivel,
        "descripcion": "Descripción de prueba en lenguaje sencillo.", "contexto_simulado": "Persona simulada de prueba."})
    assert r.status_code == 201, r.text
    id_caso = r.json()["id_caso"]
    # Etapa 1: la IA recomienda la opción correcta. Etapa 2: la IA se equivoca a propósito (RF-002 2.4).
    e1 = {"orden": 1, "enunciado": "Enunciado de prueba de la etapa uno.", "recomendacion_ia": "Sugerencia de prueba uno.",
          "opciones": [_opcion("Uno A", 100, correcta=True, ia=True), _opcion("Uno B", 0)]}
    e2 = {"orden": 2, "enunciado": "Enunciado de prueba de la etapa dos.", "recomendacion_ia": "Sugerencia de prueba dos.",
          "opciones": [_opcion("Dos A", 100, correcta=True), _opcion("Dos B", 50), _opcion("Dos C", 0, ia=True)]}
    for e in (e1, e2):
        assert cliente.put(f"{API}/editor/casos/{id_caso}/etapas", headers=autor, json=e).status_code == 201
    # RF-002 2.5: el autor no puede revisar su propio caso; sin fuente clínica no se aprueba.
    assert cliente.post(f"{API}/editor/casos/{id_caso}/revision", headers=autor, json={"accion": "aprobar",
                                                                                      "fuente_clinica": "x"}).status_code == 403
    assert cliente.post(f"{API}/editor/casos/{id_caso}/revision", headers=revisor, json={"accion": "aprobar"}).status_code == 422
    assert cliente.post(f"{API}/editor/casos/{id_caso}/revision", headers=revisor,
                        json={"accion": "aprobar", "fuente_clinica": "Referencia de prueba"}).json()["estado"] == "revisado"
    assert cliente.post(f"{API}/editor/casos/{id_caso}/revision", headers=revisor,
                        json={"accion": "publicar"}).json()["estado"] == "publicado"
    return id_caso


@requiere_db
def test_cierre_de_sesion_invalida_el_token(cliente):
    _, cab = registrar_usuario(cliente)
    assert cliente.get(f"{API}/usuarios/me", headers=cab).status_code == 200
    assert cliente.post(f"{API}/auth/logout", headers=cab).status_code == 204
    assert cliente.get(f"{API}/usuarios/me", headers=cab).status_code == 401


@requiere_db
def test_solo_el_profesional_crea_casos(cliente):
    _, cab = registrar_usuario(cliente)
    r = cliente.post(f"{API}/editor/casos", headers=cab, json={"titulo": "No permitido", "tema": "tamizaje",
                                                               "nivel_dificultad": 1, "descripcion": "x" * 25,
                                                               "contexto_simulado": "y" * 12})
    assert r.status_code == 403


@requiere_db
def test_borrador_no_aparece_y_editar_conserva_version(cliente, admin):
    _, autor = crear_profesional(cliente, admin)
    _, revisor = crear_profesional(cliente, admin)
    id_caso = publicar_caso(cliente, autor, revisor)
    _, usuario = registrar_usuario(cliente)
    assert any(c["id_caso"] == id_caso for c in cliente.get(f"{API}/casos", headers=usuario).json())
    datos = {"titulo": "Caso de prueba editado", "tema": "pólipos", "nivel_dificultad": 1,
             "descripcion": "Descripción de prueba editada.", "contexto_simulado": "Persona simulada de prueba."}
    assert cliente.put(f"{API}/editor/casos/{id_caso}", headers=autor, json=datos).status_code == 204
    assert not any(c["id_caso"] == id_caso for c in cliente.get(f"{API}/casos", headers=usuario).json())
    assert len(cliente.get(f"{API}/editor/casos/{id_caso}/versiones", headers=autor).json()) >= 1


@requiere_db
def test_simulacion_completa_con_tutor_progreso_y_profesional(cliente, admin):
    email_prof, autor = crear_profesional(cliente, admin)
    _, revisor = crear_profesional(cliente, admin)
    id_caso = publicar_caso(cliente, autor, revisor)
    _, usuario = registrar_usuario(cliente, compartir=True)

    # RF-003 3.1: el aviso se acepta antes del primer caso.
    assert cliente.post(f"{API}/intentos", headers=usuario, json={"id_caso": id_caso}).status_code == 422
    r = cliente.post(f"{API}/intentos", headers=usuario, json={"id_caso": id_caso, "acepto_aviso": True})
    assert r.status_code == 201, r.text
    id_intento = r.json()["id_intento"]

    estado = cliente.get(f"{API}/intentos/{id_intento}", headers=usuario).json()
    etapa = estado["etapa"]
    assert estado["progreso"] == {"actual": 1, "total": 2}
    assert "es_correcta" not in str(etapa["opciones"])  # la solución no se envía antes de decidir
    assert etapa["recomendacion_ia"]["rotulo"].startswith("Resultado experimental de apoyo")

    # RF-004 4.5: sin clave de IA, el tutor responde con la explicación predefinida y no bloquea.
    tutor = cliente.post(f"{API}/intentos/{id_intento}/etapas/{etapa['id_etapa']}/tutor", headers=usuario, json={})
    assert tutor.status_code == 200 and tutor.json()["proveedor"] == "predefinida"
    # RF-004 4.3: límite de preguntas por etapa.
    for _ in range(etapa["tutor"]["maximo"]):
        assert cliente.post(f"{API}/intentos/{id_intento}/etapas/{etapa['id_etapa']}/tutor", headers=usuario,
                                json={"pregunta": "¿Qué significa pólipo?"}).status_code == 200
    assert cliente.post(f"{API}/intentos/{id_intento}/etapas/{etapa['id_etapa']}/tutor", headers=usuario,
                        json={"pregunta": "¿Otra pregunta?"}).status_code == 429

    # Etapa 1: sigue a la IA, que acierta.
    correcta = next(o for o in etapa["opciones"] if o["id_opcion"] == etapa["recomendacion_ia"]["id_opcion"])
    d1 = cliente.post(f"{API}/intentos/{id_intento}/decisiones", headers=usuario,
                      json={"id_etapa": etapa["id_etapa"], "id_opcion": correcta["id_opcion"], "confianza": 5, "tiempo_ms": 4000})
    assert d1.status_code == 200, d1.text
    assert d1.json()["resultado"] == "correcto" and d1.json()["siguio_ia"] and d1.json()["puntaje"] == 100
    # RF-003 3.6: una decisión registrada no se puede cambiar.
    assert cliente.post(f"{API}/intentos/{id_intento}/decisiones", headers=usuario,
                        json={"id_etapa": etapa["id_etapa"], "id_opcion": correcta["id_opcion"], "confianza": 3}).status_code == 409

    # Etapa 2: la IA se equivoca a propósito; la persona la rechaza y elige la opción parcial.
    etapa2 = cliente.get(f"{API}/intentos/{id_intento}", headers=usuario).json()["etapa"]
    parcial = next(o for o in etapa2["opciones"] if o["texto"] == "Dos B")
    d2 = cliente.post(f"{API}/intentos/{id_intento}/decisiones", headers=usuario,
                      json={"id_etapa": etapa2["id_etapa"], "id_opcion": parcial["id_opcion"], "confianza": 2}).json()
    assert d2["resultado"] == "parcial" and d2["puntaje"] == 50
    assert d2["ia_estaba_equivocada"] and d2["detectaste_error_ia"] and d2["intento_finalizado"]
    assert d2["respuesta_esperada"] == "Dos A" and d2["fuente"]
    assert "Primer caso" in d2["insignias_nuevas"]

    # RF-005 5.4: resumen coherente con lo registrado.
    resumen = cliente.get(f"{API}/intentos/{id_intento}/resumen", headers=usuario).json()
    assert resumen["puntaje_total"] == 150 and resumen["aciertos"] == 1 and resumen["errores_ia_detectados"] == 1

    # RF-008 8.1 y 8.2.
    assert cliente.get(f"{API}/progreso/historial", headers=usuario).json()[0]["puntaje_total"] == 150
    progreso = cliente.get(f"{API}/progreso", headers=usuario).json()
    assert progreso["puntaje_acumulado"] == 150 and progreso["tasa_deteccion_errores_ia"] == 100
    assert cliente.get(f"{API}/casos", headers=usuario).json()[0]["estado_usuario"] in ("completado", "no_iniciado")

    # RF-001 1.6 y RF-008 8.3/8.4: vínculo directo y panel del profesional.
    r = cliente.post(f"{API}/vinculos", headers=usuario, json={"correo_profesional": email_prof, "autoriza_compartir": True})
    assert r.status_code == 201, r.text
    panel = cliente.get(f"{API}/profesional/panel", headers=autor).json()
    assert panel["usuarios"] == 1 and "nombre" not in str(panel)
    yo = cliente.get(f"{API}/usuarios/me", headers=usuario).json()
    assert cliente.get(f"{API}/profesional/usuarios/{yo['id_usuario']}/avance", headers=autor).status_code == 200
    assert cliente.get(f"{API}/profesional/usuarios/{yo['id_usuario']}/avance", headers=revisor).status_code == 403

    # RF-007 7.2: exportación sin nombres ni correos.
    csv = cliente.get(f"{API}/exportacion/interacciones.csv", headers=autor).text
    assert "id_seudonimo" in csv and "Persona de prueba" not in csv and "@" not in csv
    assert len(csv.strip().splitlines()) == 3

    # RF-009 9.1: al revocar 'compartir avance' el profesional deja de ver el detalle.
    assert cliente.put(f"{API}/privacidad/autorizaciones/compartir_avance", headers=usuario,
                       json={"aceptada": False}).status_code == 204
    assert cliente.get(f"{API}/profesional/usuarios/{yo['id_usuario']}/avance", headers=autor).status_code == 403


@requiere_db
def test_privacidad_rectificar_y_suprimir(cliente):
    email, cab = registrar_usuario(cliente)
    assert len(cliente.get(f"{API}/privacidad/autorizaciones", headers=cab).json()) == 3
    assert cliente.patch(f"{API}/usuarios/me", headers=cab, json={"nombre": "Nombre corregido"}).status_code == 204
    assert cliente.get(f"{API}/privacidad/mis-datos", headers=cab).json()["perfil"]["nombre"] == "Nombre corregido"
    assert cliente.request("DELETE", f"{API}/usuarios/me", headers=cab, json={"contrasena": "mala1234", "confirmar": True}).status_code == 400
    assert cliente.request("DELETE", f"{API}/usuarios/me", headers=cab,
                           json={"contrasena": "Segura123", "confirmar": True}).status_code == 204
    assert cliente.post(f"{API}/auth/login", json={"correo": email, "contrasena": "Segura123"}).status_code == 401


@requiere_db
def test_administracion_de_usuarios(cliente, admin):
    email, cab = registrar_usuario(cliente)
    lista = cliente.get(f"{API}/admin/usuarios", params={"buscar": email}, headers=admin).json()
    assert len(lista) == 1
    assert cliente.get(f"{API}/admin/usuarios", headers=cab).status_code == 403
    assert cliente.patch(f"{API}/admin/usuarios/{lista[0]['id_usuario']}", headers=admin,
                         json={"estado": "inactivo"}).status_code == 204
    assert cliente.post(f"{API}/auth/login", json={"correo": email, "contrasena": "Segura123"}).status_code == 401
    assert cliente.post(f"{API}/admin/usuarios", headers=admin, json={"nombre": "Otra", "correo": correo("x"), "contrasena": "Segura123",
                                                                     "rol": "Usuario"}).status_code == 201
    assert token  # importado para reutilizar en otras pruebas


@requiere_db
def test_recurso_multimedia_exige_formato_dataset_y_licencia(cliente, admin, tmp_path, monkeypatch):
    """RF-002 2.2: solo JPG/PNG/MP4, con dataset de origen y licencia; se publica bajo /media."""
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "media_dir", str(tmp_path))
    _, autor = crear_profesional(cliente, admin)
    _, revisor = crear_profesional(cliente, admin)
    id_caso = publicar_caso(cliente, autor, revisor)
    id_etapa = cliente.get(f"{API}/editor/casos/{id_caso}", headers=revisor).json()["etapas"][0]["id_etapa"]
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 64
    url = f"{API}/editor/etapas/{id_etapa}/recursos"
    assert cliente.post(url, headers=autor, files={"archivo": ("a.pdf", b"%PDF", "application/pdf")},
                        data={"id_dataset": "1", "licencia": "CC BY 4.0"}).status_code == 415
    assert cliente.post(url, headers=autor, files={"archivo": ("a.png", png, "image/png")},
                        data={"id_dataset": "1", "licencia": " "}).status_code == 422
    assert cliente.post(url, headers=autor, files={"archivo": ("a.png", png, "image/png")},
                        data={"id_dataset": "999", "licencia": "CC BY 4.0"}).status_code == 422
    r = cliente.post(url, headers=autor, files={"archivo": ("a.png", png, "image/png")}, data={"id_dataset": "1", "licencia": "CC BY 4.0"})
    assert r.status_code == 201, r.text
    # El contenido queda en la base (sobrevive a reinicios del servidor) y se publica en /media/recursos/.
    assert not any(tmp_path.iterdir())
    url_recurso = f"/media/recursos/{r.json()['id_recurso']}.png"
    publicado = cliente.get(url_recurso)
    assert publicado.status_code == 200 and publicado.content == png
    assert publicado.headers["content-type"] == "image/png"
    assert publicado.headers["cross-origin-resource-policy"] == "same-site"
    # Peticiones parciales para el visor de video cuadro a cuadro (RF-003 3.3b).
    parcial = cliente.get(url_recurso, headers={"Range": "bytes=0-7"})
    assert parcial.status_code == 206 and parcial.content == png[:8]
    assert parcial.headers["content-range"] == f"bytes 0-7/{len(png)}"
    assert cliente.get(url_recurso, headers={"Range": "bytes=-4"}).content == png[-4:]
    assert cliente.get(url_recurso, headers={"Range": "bytes=9999-"}).status_code == 416
    assert cliente.get("/media/recursos/999999999.png").status_code == 404
    etapa = cliente.get(f"{API}/editor/casos/{id_caso}", headers=revisor).json()["etapas"][0]
    assert [x["ruta_almacenamiento"] for x in etapa["recursos"]] == [url_recurso.removeprefix("/media/")]
