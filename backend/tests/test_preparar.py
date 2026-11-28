"""Preparación del despliegue público: esquema, administrador inicial y caso de demostración."""
from sqlalchemy import text

from app import preparar
from app.core.config import Settings, get_settings
from app.core.db import SessionLocal
from tests.conftest import correo, registrar_usuario, requiere_db, token


def test_url_de_render_usa_psycopg():
    assert Settings(database_url="postgresql://u:c@h/db").database_url == "postgresql+psycopg://u:c@h/db"
    assert Settings(database_url="postgres://u:c@h/db").database_url == "postgresql+psycopg://u:c@h/db"


@requiere_db
def test_preparar_es_idempotente(cliente, monkeypatch):
    admin = correo("admin_inicial")
    monkeypatch.setenv("ADMIN_CORREO", admin)
    monkeypatch.setenv("ADMIN_CONTRASENA", "Inicial123")
    monkeypatch.setenv("CASO_DEMO", "1")
    assert preparar.aplicar_esquema() is False  # la base de pruebas ya tiene el esquema
    with SessionLocal() as db:
        db.execute(text("UPDATE caso SET eliminado = TRUE WHERE titulo = :t"), {"t": preparar.TITULO_DEMO})
        db.commit()
        assert preparar.crear_admin_inicial(db) is True
        assert preparar.crear_admin_inicial(db) is False
        # Si la variable cambia (o traía un salto de línea), el administrador queda con la contraseña nueva.
        monkeypatch.setenv("ADMIN_CONTRASENA", "Nueva12345\n")
        assert preparar.crear_admin_inicial(db) is False
        assert preparar.publicar_caso_demo(db) is True
        assert preparar.publicar_caso_demo(db) is False
    cab = token(cliente, admin, "Nueva12345")
    assert cliente.get("/api/v1/admin/usuarios", headers=cab).status_code == 200
    _, cab_usuario = registrar_usuario(cliente)
    catalogo = cliente.get("/api/v1/casos", headers=cab_usuario).json()
    assert any(c["titulo"] == preparar.TITULO_DEMO for c in catalogo)


@requiere_db
def test_demostracion_no_recibe_estudios(cliente, monkeypatch):
    monkeypatch.setattr(get_settings(), "entorno", "demostracion")
    _, cab_usuario = registrar_usuario(cliente)
    r = cliente.post("/api/v1/estudios", headers=cab_usuario,
                     files={"archivo": ("a.png", b"x", "image/png")}, data={"confirma_sin_datos_visibles": "true"})
    assert r.status_code == 403
    assert "demostración" in r.json()["detail"]
    condiciones = cliente.get("/api/v1/estudios/condiciones", headers=cab_usuario).json()
    assert condiciones["demostracion"] and not condiciones["habilitado"]


@requiere_db
def test_demostracion_recibe_estudios_con_estudios_en_demo(cliente, monkeypatch):
    """Con ESTUDIOS_EN_DEMO=1 la demostración permite cargar, con el aviso de usar solo imágenes de datasets públicos."""
    monkeypatch.setattr(get_settings(), "entorno", "demostracion")
    monkeypatch.setattr(get_settings(), "estudios_en_demo", True)
    _, cab_usuario = registrar_usuario(cliente)
    condiciones = cliente.get("/api/v1/estudios/condiciones", headers=cab_usuario).json()
    assert condiciones["habilitado"] and "HyperKvasir" in condiciones["aviso"]
    r = cliente.post("/api/v1/estudios", headers=cab_usuario,
                     files={"archivo": ("a.png", b"x", "image/png")}, data={"confirma_sin_datos_visibles": "true"})
    assert "demostración" not in r.json()["detail"]  # ya no la bloquea la demostración, sino la autorización de datos sensibles


@requiere_db
def test_imagen_de_ejemplo_en_el_caso_de_demostracion(cliente, monkeypatch, tmp_path):
    """La etapa 1 del caso de demostración recibe una sola vez la imagen de HyperKvasir con el modelo de visión activo."""
    import io

    from PIL import Image

    monkeypatch.setenv("CASO_DEMO", "1")
    imagen = tmp_path / "ejemplo-kvasir.jpg"
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (180, 90, 90)).save(buf, format="JPEG")
    imagen.write_bytes(buf.getvalue())
    preparar.aplicar_esquema()  # aplica db/07 (solo HyperKvasir en el catálogo)
    with SessionLocal() as db:
        db.execute(text("UPDATE caso SET eliminado = TRUE WHERE titulo = :t"), {"t": preparar.TITULO_DEMO})
        db.commit()
        assert preparar.publicar_caso_demo(db) is True
        assert preparar.agregar_imagen_demo(db, str(imagen)) is True
        assert preparar.agregar_imagen_demo(db, str(imagen)) is False
        fila = db.execute(text("""SELECT e.usa_modelo_vision, d.nombre FROM etapa e JOIN caso c ON c.id_caso = e.id_caso
                                  JOIN recurso_multimedia r ON r.id_etapa = e.id_etapa JOIN dataset d ON d.id_dataset = r.id_dataset
                                  WHERE c.titulo = :t AND NOT c.eliminado AND e.orden = 1"""), {"t": preparar.TITULO_DEMO}).one()
    assert fila.usa_modelo_vision is True and fila.nombre == "HyperKvasir"

    # De punta a punta: la imagen guardada en la base llega al modelo de visión y su resultado aparece en la etapa.
    from app.modules.estudios.vision import CON_REGION, ResultadoVision, fijar_modelo

    recibido = {}

    class ModeloFalso:
        version = "prueba-demo"

        def analizar(self, datos: bytes) -> ResultadoVision:
            recibido["bytes"] = datos
            return ResultadoVision({"x": 0.2, "y": 0.2, "ancho": 0.4, "alto": 0.3}, CON_REGION, 81.0, self.version)

    fijar_modelo(ModeloFalso())
    try:
        _, cab = registrar_usuario(cliente)
        id_caso = next(c["id_caso"] for c in cliente.get("/api/v1/casos", headers=cab).json() if c["titulo"] == preparar.TITULO_DEMO)
        intento = cliente.post("/api/v1/intentos", headers=cab, json={"id_caso": id_caso, "acepto_aviso": True}).json()
        etapa = cliente.get(f"/api/v1/intentos/{intento['id_intento']}", headers=cab).json()["etapa"]
    finally:
        fijar_modelo(None)
    assert recibido["bytes"] == imagen.read_bytes()
    assert etapa["modelo_vision"]["disponible"] is True and etapa["modelo_vision"]["version_modelo"] == "prueba-demo"
    assert etapa["recursos"][0]["dataset"] == "HyperKvasir" and etapa["recursos"][0]["tipo"] == "imagen"


@requiere_db
def test_catalogo_solo_hyperkvasir():
    """El proyecto usa un solo dataset público: HyperKvasir, con su licencia verificada."""
    preparar.aplicar_esquema()
    with SessionLocal() as db:
        filas = db.execute(text("SELECT nombre, licencia FROM dataset")).all()
    assert [f.nombre for f in filas] == ["HyperKvasir"] and filas[0].licencia.startswith("CC BY 4.0")


@requiere_db
def test_imagenes_de_la_etapa_2_del_caso_de_demostracion(monkeypatch):
    """La etapa 2 del caso de demostración recibe una sola vez las imágenes de HyperKvasir de app/demo."""
    monkeypatch.setenv("CASO_DEMO", "1")
    preparar.aplicar_esquema()
    with SessionLocal() as db:
        db.execute(text("UPDATE caso SET eliminado = TRUE WHERE titulo = :t"), {"t": preparar.TITULO_DEMO})
        db.commit()
        assert preparar.publicar_caso_demo(db) is True
        assert preparar.agregar_imagenes_etapa_2(db) == len(preparar.IMAGENES_ETAPA_2)
        assert preparar.agregar_imagenes_etapa_2(db) == 0
        filas = db.execute(text("""SELECT d.nombre, r.licencia, r.tipo FROM recurso_multimedia r
                                   JOIN dataset d ON d.id_dataset = r.id_dataset JOIN etapa e ON e.id_etapa = r.id_etapa
                                   JOIN caso c ON c.id_caso = e.id_caso
                                   WHERE c.titulo = :t AND NOT c.eliminado AND e.orden = 2"""), {"t": preparar.TITULO_DEMO}).all()
    assert len(filas) == len(preparar.IMAGENES_ETAPA_2)
    assert all(f.nombre == "HyperKvasir" and "CC BY 4.0" in f.licencia for f in filas)


def test_las_imagenes_de_demostracion_son_jpg_reales():
    """Los archivos de app/demo deben ser imágenes JPEG, no fichas de texto con extensión .jpg."""
    from pathlib import Path

    from PIL import Image

    carpeta = Path(preparar.__file__).parent / "demo"
    for nombre in preparar.IMAGENES_ETAPA_2:
        with Image.open(carpeta / nombre) as imagen:
            assert imagen.format == "JPEG"


@requiere_db
def test_caso_de_tamizaje_se_publica_una_vez_con_sus_imagenes(monkeypatch, tmp_path):
    """El caso de tamizaje (PR #25) queda publicado con 3 etapas, la IA equivocada a propósito en la etapa 3
    y una imagen de HyperKvasir por etapa."""
    import json
    from io import BytesIO

    from PIL import Image

    imagen = tmp_path / "ejemplo-kvasir.jpg"
    buffer = BytesIO()
    Image.new("RGB", (64, 64), (180, 90, 80)).save(buffer, "JPEG")
    imagen.write_bytes(buffer.getvalue())
    monkeypatch.setenv("CASO_DEMO", "1")
    monkeypatch.setenv("IMAGEN_DEMO", str(imagen))
    datos = json.loads(preparar.CASO_TAMIZAJE.read_text(encoding="utf-8"))
    preparar.aplicar_esquema()
    with SessionLocal() as db:
        db.execute(text("UPDATE caso SET eliminado = TRUE WHERE titulo = :t"), {"t": datos["titulo"]})
        db.commit()
        id_caso = preparar.publicar_caso_tamizaje(db)
        assert id_caso is not None
        assert preparar.publicar_caso_tamizaje(db) is None
        caso = db.execute(text("SELECT estado, tema FROM caso WHERE id_caso = :c"), {"c": id_caso}).one()
        etapas = db.execute(text("""SELECT e.orden, count(r.id_recurso) AS imagenes FROM etapa e
                                    LEFT JOIN recurso_multimedia r ON r.id_etapa = e.id_etapa
                                    WHERE e.id_caso = :c GROUP BY e.orden ORDER BY e.orden"""), {"c": id_caso}).all()
        ia_erronea = db.execute(text("""SELECT o.es_correcta FROM opcion_decision o JOIN etapa e ON e.id_etapa = o.id_etapa
                                        WHERE e.id_caso = :c AND e.orden = 3 AND o.recomendada_ia"""), {"c": id_caso}).scalar()
    assert caso.estado == "publicado" and caso.tema == "tamizaje"
    assert [(e.orden, e.imagenes) for e in etapas] == [(1, 1), (2, 1), (3, 1)]
    assert ia_erronea is False


def test_imagenes_del_caso_de_tamizaje_existen():
    """Cada imagen que nombra el JSON del caso de tamizaje corresponde a un archivo real (o a la imagen de ejemplo)."""
    import json

    datos = json.loads(preparar.CASO_TAMIZAJE.read_text(encoding="utf-8"))
    for etapa in datos["etapas"]:
        destino = preparar.IMAGENES_TAMIZAJE[etapa["imagen_url"]]
        assert destino == "IMAGEN_DEMO" or (preparar.CASO_TAMIZAJE.parent / destino).is_file()


@requiere_db
def test_caso_de_vision_reemplaza_la_version_anterior_y_usa_fotos_reales(monkeypatch, tmp_path):
    """Caso 2: retira la primera versión (sus «imágenes» eran fichas de texto), se publica una vez con una foto de
    HyperKvasir en cada etapa, el modelo de visión activo en las etapas 1 y 2 y la IA equivocada a propósito en la 2."""
    import json
    from io import BytesIO

    from PIL import Image

    imagen = tmp_path / "ejemplo-kvasir.jpg"
    buffer = BytesIO()
    Image.new("RGB", (64, 64), (170, 80, 80)).save(buffer, "JPEG")
    imagen.write_bytes(buffer.getvalue())
    monkeypatch.setenv("CASO_DEMO", "1")
    monkeypatch.setenv("IMAGEN_DEMO", str(imagen))
    datos = json.loads(preparar.CASO_VISION.read_text(encoding="utf-8"))
    preparar.aplicar_esquema()
    with SessionLocal() as db:
        db.execute(text("UPDATE caso SET eliminado = TRUE WHERE titulo IN (:a, :b)"),
                   {"a": datos["titulo"], "b": preparar.TITULO_VISION_ANTERIOR})
        autor = preparar._crear_usuario(db, "Profesional de la salud", "Autor anterior",
                                        f"vision-anterior-{tmp_path.name}@ejemplo.com", "Segura123456")
        db.execute(text("""INSERT INTO caso (id_autor, titulo, tema, nivel_dificultad, estado)
                           VALUES (:a, :t, 'pólipos', 1, 'publicado')"""),
                   {"a": autor, "t": preparar.TITULO_VISION_ANTERIOR})
        db.commit()
        id_caso = preparar.publicar_caso_vision(db)
        assert id_caso is not None
        assert preparar.publicar_caso_vision(db) is None
        anteriores = db.execute(text("SELECT count(*) FROM caso WHERE titulo = :t AND NOT eliminado"),
                                {"t": preparar.TITULO_VISION_ANTERIOR}).scalar()
        etapas = db.execute(text("""SELECT e.orden, e.usa_modelo_vision, count(r.id_recurso) AS imagenes FROM etapa e
                                    LEFT JOIN recurso_multimedia r ON r.id_etapa = e.id_etapa
                                    WHERE e.id_caso = :c GROUP BY e.orden, e.usa_modelo_vision ORDER BY e.orden"""),
                            {"c": id_caso}).all()
        ia_erronea = db.execute(text("""SELECT e.orden FROM etapa e WHERE e.id_caso = :c AND e.ia_erronea_intencional"""),
                                {"c": id_caso}).scalars().all()
        mimes = db.execute(text("""SELECT c.tipo_mime FROM recurso_contenido c JOIN recurso_multimedia r ON r.id_recurso = c.id_recurso
                                   JOIN etapa e ON e.id_etapa = r.id_etapa WHERE e.id_caso = :c"""), {"c": id_caso}).scalars().all()
    assert anteriores == 0
    assert [(e.orden, e.usa_modelo_vision, e.imagenes) for e in etapas] == [(1, True, 1), (2, True, 1), (3, False, 1)]
    assert ia_erronea == [2]
    assert mimes == ["image/jpeg"] * 3


def test_imagenes_del_caso_de_vision_son_fotos_reales():
    """Cada imagen del Caso 2 es un JPEG de verdad (o la imagen de ejemplo del modelo), no un archivo renombrado."""
    import json

    datos = json.loads(preparar.CASO_VISION.read_text(encoding="utf-8"))
    for etapa in datos["etapas"]:
        destino = preparar.IMAGENES_VISION[etapa["imagen_url"]]
        if destino != "IMAGEN_DEMO":
            assert (preparar.CASO_VISION.parent / destino).read_bytes().startswith(b"\xff\xd8\xff")
    assert not any(p.read_bytes()[:1] == b"{" for p in preparar.CASO_VISION.parent.glob("*.jpg"))



def test_imagenes_del_caso_3_existen_y_suman_10_escenarios():
    """El Caso 3 nombra solo imágenes reales de HyperKvasir y, con los demás casos de la demostración, completa los
    10 escenarios de decisión del Acta de constitución (2 del caso de demostración + 3 + 3 + 4)."""
    import json

    datos = json.loads(preparar.CASO_SENALES.read_text(encoding="utf-8"))
    for etapa in datos["etapas"]:
        destino = preparar.IMAGENES_SENALES[etapa["imagen_url"]]
        assert destino == "IMAGEN_DEMO" or (preparar.CASO_SENALES.parent / destino).is_file()
        assert sum(o["correcta"] for o in etapa["opciones"]) == 1
    tamizaje = json.loads(preparar.CASO_TAMIZAJE.read_text(encoding="utf-8"))
    vision = json.loads(preparar.CASO_VISION.read_text(encoding="utf-8"))
    assert 2 + len(tamizaje["etapas"]) + len(vision["etapas"]) + len(datos["etapas"]) == 10


@requiere_db
def test_caso_3_se_publica_una_vez_con_la_ia_equivocada_en_la_etapa_2(monkeypatch, tmp_path):
    """Caso 3: 4 etapas con una foto de HyperKvasir cada una, modelo de visión en la etapa 3 e IA errada en la 2."""
    import json
    from io import BytesIO

    from PIL import Image

    imagen = tmp_path / "ejemplo-kvasir.jpg"
    buffer = BytesIO()
    Image.new("RGB", (64, 64), (175, 85, 80)).save(buffer, "JPEG")
    imagen.write_bytes(buffer.getvalue())
    monkeypatch.setenv("CASO_DEMO", "1")
    monkeypatch.setenv("IMAGEN_DEMO", str(imagen))
    datos = json.loads(preparar.CASO_SENALES.read_text(encoding="utf-8"))
    preparar.aplicar_esquema()
    with SessionLocal() as db:
        db.execute(text("UPDATE caso SET eliminado = TRUE WHERE titulo = :t"), {"t": datos["titulo"]})
        db.commit()
        id_caso = preparar.publicar_caso_senales(db)
        assert id_caso is not None
        assert preparar.publicar_caso_senales(db) is None
        caso = db.execute(text("SELECT estado, tema FROM caso WHERE id_caso = :c"), {"c": id_caso}).one()
        etapas = db.execute(text("""SELECT e.orden, e.usa_modelo_vision, count(r.id_recurso) AS imagenes FROM etapa e
                                    LEFT JOIN recurso_multimedia r ON r.id_etapa = e.id_etapa
                                    WHERE e.id_caso = :c GROUP BY e.orden, e.usa_modelo_vision ORDER BY e.orden"""),
                            {"c": id_caso}).all()
        ia_erronea = db.execute(text("""SELECT o.es_correcta FROM opcion_decision o JOIN etapa e ON e.id_etapa = o.id_etapa
                                        WHERE e.id_caso = :c AND e.orden = 2 AND o.recomendada_ia"""), {"c": id_caso}).scalar()
    assert caso.estado == "publicado" and caso.tema == "tamizaje"
    assert [(e.orden, e.usa_modelo_vision, e.imagenes) for e in etapas] == [
        (1, False, 1), (2, False, 1), (3, True, 1), (4, False, 1)]
    assert ia_erronea is False
