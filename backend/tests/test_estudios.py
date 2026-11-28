"""Pruebas de RF-010 (estudios propios), RF-003 3.4/IE-04 (modelo de visión) y RF-001 1.3 (recuperación)."""
import io
import re

import numpy as np
import pytest
from PIL import Image
from sqlalchemy import create_engine, text

from app.core.correo import buzon_desarrollo
from app.core.textos import ROTULO_IA
from app.modules.estudios import seguridad
from app.modules.estudios.vision import CON_REGION, SIN_REGION, ResultadoVision, fijar_modelo, resultado_desde_mascara
from app.modules.tutor.prompt import VERSION_PROMPT
from tests.conftest import DB_URL, correo, crear_profesional, registrar_usuario, requiere_db, token

API = "/api/v1"


def jpg_con_exif() -> bytes:
    img = Image.new("RGB", (32, 32), (180, 90, 90))
    exif = Image.Exif()
    exif[0x013B] = "Nombre Apellido"  # Artist
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif.tobytes())
    return buf.getvalue()


def dicom_con_datos() -> bytes:
    from pydicom.dataset import Dataset, FileMetaDataset
    from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid

    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    ds = Dataset()
    ds.file_meta = meta
    ds.SOPClassUID, ds.SOPInstanceUID = meta.MediaStorageSOPClassUID, meta.MediaStorageSOPInstanceUID
    ds.PatientName, ds.PatientID, ds.InstitutionName = "Persona^Ficticia", "DOC-998877", "Institucion Ficticia"
    ds.BurnedInAnnotation = "YES"
    ds.Rows = ds.Columns = 8
    ds.SamplesPerPixel, ds.PhotometricInterpretation = 1, "MONOCHROME2"
    ds.BitsAllocated = ds.BitsStored = 8
    ds.HighBit, ds.PixelRepresentation = 7, 0
    ds.PixelData = bytes(range(64))
    buf = io.BytesIO()
    ds.save_as(buf, enforce_file_format=True)
    return buf.getvalue()


class ModeloFalso:
    version = "prueba-1"

    def analizar(self, imagen: bytes) -> ResultadoVision:
        return ResultadoVision({"x": 0.1, "y": 0.2, "ancho": 0.3, "alto": 0.3}, CON_REGION, 87.5, self.version)


@pytest.fixture
def modelo_falso():
    fijar_modelo(ModeloFalso())
    yield
    fijar_modelo(None)


def test_jpg_queda_sin_exif():
    png, advertencia = seguridad.desidentificar("foto.jpg", jpg_con_exif())
    img = Image.open(io.BytesIO(png))
    assert img.format == "PNG" and not img.getexif() and b"Nombre Apellido" not in png and not advertencia


def test_dicom_queda_sin_etiquetas_y_advierte_texto_sobreimpreso():
    png, advertencia = seguridad.desidentificar("estudio.dcm", dicom_con_datos())
    assert advertencia
    for dato in (b"Persona", b"DOC-998877", b"Institucion"):
        assert dato not in png
    assert Image.open(io.BytesIO(png)).size == (8, 8)


def test_formato_no_permitido():
    with pytest.raises(seguridad.ErrorNegocio):
        seguridad.desidentificar("archivo.pdf", b"%PDF")


class _BaseEnMemoria:
    """Sustituye a la sesión de base de datos en las pruebas del cifrado (sin PostgreSQL)."""

    def __init__(self):
        self.filas: dict[int, bytes] = {}

    def execute(self, sentencia, params):
        sql = str(sentencia)
        if sql.lstrip().startswith("INSERT"):
            self.filas[params["e"]] = params["d"]
        elif sql.lstrip().startswith("DELETE"):
            self.filas.pop(params["e"], None)
        return self

    def scalar(self):
        return self._ultimo


def test_cifrado_en_reposo_en_la_base():
    """RNF-003: el estudio se guarda cifrado en la base y solo se lee con la clave."""
    db = _BaseEnMemoria()
    ruta = seguridad.guardar_cifrado(db, 7, b"\x89PNG datos")
    assert ruta == "base:7"
    assert b"PNG" not in db.filas[7]
    db._ultimo = db.filas[7]
    assert seguridad.leer_cifrado(db, ruta) == b"\x89PNG datos"
    seguridad.borrar(db, ruta)
    assert 7 not in db.filas


def test_lee_estudios_guardados_en_disco_antes_del_cambio(tmp_path):
    """Las instalaciones anteriores guardaban el archivo cifrado en ESTUDIOS_DIR: se siguen leyendo y borrando."""
    archivo = tmp_path / "1.bin"
    archivo.write_bytes(seguridad._fernet().encrypt(b"\x89PNG antiguo"))
    assert seguridad.leer_cifrado(None, str(archivo)) == b"\x89PNG antiguo"
    seguridad.borrar(None, str(archivo))
    assert not archivo.exists()
    with pytest.raises(seguridad.ErrorNegocio):
        seguridad.leer_cifrado(None, str(archivo))


def test_resultado_del_modelo_desde_mascara():
    prob = np.zeros((100, 100))
    prob[20:40, 30:60] = 0.9
    r = resultado_desde_mascara(prob, "v1")
    assert r.clasificacion == CON_REGION and r.roi == {"x": 0.3, "y": 0.2, "ancho": 0.3, "alto": 0.2} and r.confianza == 90.0
    assert resultado_desde_mascara(np.full((50, 50), 0.1), "v1").clasificacion == SIN_REGION


@requiere_db
def test_recuperacion_de_contrasena_un_solo_uso(cliente):
    email, _ = registrar_usuario(cliente)
    buzon_desarrollo.clear()
    assert cliente.post(f"{API}/auth/recuperar", json={"correo": correo("noexiste")}).status_code == 202
    assert not buzon_desarrollo  # no revela si el correo existe ni envía nada
    assert cliente.post(f"{API}/auth/recuperar", json={"correo": email}).status_code == 202
    enlace = re.search(r"restablecer=(\S+)", buzon_desarrollo[-1].get_content()).group(1)
    assert cliente.post(f"{API}/auth/restablecer", json={"token": enlace, "contrasena": "Nueva12345"}).status_code == 204
    assert cliente.post(f"{API}/auth/restablecer", json={"token": enlace, "contrasena": "Otra12345"}).status_code == 400
    token(cliente, email, "Nueva12345")


@requiere_db
def test_estudio_exige_autorizacion_de_datos_sensibles(cliente):
    _, cab = registrar_usuario(cliente)
    r = cliente.post(f"{API}/estudios", headers=cab, files={"archivo": ("a.jpg", jpg_con_exif(), "image/jpeg")},
                     data={"confirma_sin_datos_visibles": "true"})
    assert r.status_code == 403


@requiere_db
def test_estudio_completo_compartir_comentar_y_eliminar(cliente, admin, modelo_falso, tmp_path, monkeypatch):
    monkeypatch.setattr(seguridad.get_settings(), "estudios_dir", str(tmp_path))
    email_prof, prof = crear_profesional(cliente, admin)
    _, otro_prof = crear_profesional(cliente, admin)
    _, cab = registrar_usuario(cliente)
    assert cliente.put(f"{API}/privacidad/autorizaciones/datos_sensibles", headers=cab, json={"aceptada": True}).status_code == 204

    r = cliente.post(f"{API}/estudios", headers=cab, files={"archivo": ("a.jpg", jpg_con_exif(), "image/jpeg")},
                     data={"confirma_sin_datos_visibles": "true"})
    assert r.status_code == 201, r.text
    id_estudio = r.json()["id_estudio"]
    assert r.json()["procesado"]

    detalle = cliente.get(f"{API}/estudios/{id_estudio}", headers=cab).json()
    assert detalle["interpretacion"]["clasificacion"] == CON_REGION and detalle["interpretacion"]["rotulo"] == ROTULO_IA
    assert detalle["interpretacion"]["explicacion"]  # explicación del tutor (predefinida si no hay IA)
    # RNF-007: la interpretación guarda la versión del modelo y la del prompt del tutor.
    assert detalle["interpretacion"]["version_modelo"] == ModeloFalso.version
    assert detalle["interpretacion"]["version_prompt"] == VERSION_PROMPT
    imagen = cliente.get(f"{API}/estudios/{id_estudio}/imagen", headers=cab)
    assert imagen.status_code == 200 and not Image.open(io.BytesIO(imagen.content)).getexif()

    # Sin compartir, el profesional no lo ve.
    assert cliente.get(f"{API}/estudios/{id_estudio}", headers=prof).status_code == 404
    id_vinculo = cliente.post(f"{API}/vinculos", headers=cab, json={"correo_profesional": email_prof}).json()["id_vinculo"]
    assert cliente.put(f"{API}/estudios/{id_estudio}/compartir", headers=cab, json={"id_vinculo": id_vinculo}).status_code == 204
    assert len(cliente.get(f"{API}/profesional/estudios", headers=prof).json()) == 1
    assert cliente.get(f"{API}/estudios/{id_estudio}", headers=otro_prof).status_code == 404
    assert cliente.post(f"{API}/estudios/{id_estudio}/comentarios", headers=prof, json={"texto": "Comentario educativo."}).status_code == 201
    assert cliente.get(f"{API}/notificaciones", headers=cab).json()["comentarios_nuevos"] == 1
    assert cliente.get(f"{API}/estudios/{id_estudio}", headers=cab).json()["comentarios"][0]["texto"] == "Comentario educativo."
    assert cliente.get(f"{API}/notificaciones", headers=cab).json()["comentarios_nuevos"] == 0

    # Revocar el compartir y eliminar: se borra el archivo cifrado.
    assert cliente.put(f"{API}/estudios/{id_estudio}/compartir", headers=cab, json={"id_vinculo": None}).status_code == 204
    assert cliente.get(f"{API}/estudios/{id_estudio}", headers=prof).status_code == 404
    assert cliente.delete(f"{API}/estudios/{id_estudio}", headers=cab).status_code == 204
    with create_engine(DB_URL).connect() as c:
        assert c.execute(text("SELECT count(*) FROM estudio_contenido WHERE id_estudio = :e"), {"e": id_estudio}).scalar() == 0
    assert cliente.get(f"{API}/estudios", headers=cab).json() == []


@requiere_db
def test_suprimir_la_cuenta_borra_los_estudios(cliente, modelo_falso, tmp_path, monkeypatch):
    """RF-009 9.3 (Ley 1581): al suprimir la cuenta, los estudios propios se eliminan del almacenamiento."""
    monkeypatch.setattr(seguridad.get_settings(), "estudios_dir", str(tmp_path))
    _, cab = registrar_usuario(cliente)
    assert cliente.put(f"{API}/privacidad/autorizaciones/datos_sensibles", headers=cab, json={"aceptada": True}).status_code == 204
    r = cliente.post(f"{API}/estudios", headers=cab, files={"archivo": ("a.jpg", jpg_con_exif(), "image/jpeg")},
                     data={"confirma_sin_datos_visibles": "true"})
    assert r.status_code == 201, r.text
    id_estudio = r.json()["id_estudio"]
    with create_engine(DB_URL).connect() as c:  # el contenido cifrado existe antes de suprimir
        assert c.execute(text("SELECT count(*) FROM estudio_contenido WHERE id_estudio = :e"), {"e": id_estudio}).scalar() == 1

    assert cliente.request("DELETE", f"{API}/usuarios/me", headers=cab,
                           json={"contrasena": "Segura123", "confirmar": True}).status_code == 204
    with create_engine(DB_URL).connect() as c:
        fila = c.execute(text("""SELECT eliminado, ruta_cifrada,
                                        (SELECT count(*) FROM interpretacion_estudio WHERE id_estudio = :e) AS interpretaciones
                                 FROM estudio_propio WHERE id_estudio = :e"""), {"e": id_estudio}).mappings().one()
        contenido = c.execute(text("SELECT count(*) FROM estudio_contenido WHERE id_estudio = :e"), {"e": id_estudio}).scalar()
    assert fila["eliminado"] and fila["ruta_cifrada"] == "" and fila["interpretaciones"] == 0 and contenido == 0
