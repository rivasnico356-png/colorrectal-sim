"""RF-010 10.2 y RNF-003: desidentificación de imágenes y cifrado en reposo."""
import base64
import hashlib
import io
from pathlib import Path

from cryptography.fernet import Fernet
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errores import ErrorNegocio

MAX_BYTES = 20 * 1024 * 1024
EXTENSIONES = {".jpg": "imagen", ".jpeg": "imagen", ".png": "imagen", ".dcm": "dicom"}

# Etiquetas DICOM que identifican a la persona o a la institución (verificación de RF-010 10.2).
ETIQUETAS_DICOM = ["PatientName", "PatientID", "PatientBirthDate", "PatientSex", "PatientAge", "PatientAddress",
                   "OtherPatientIDs", "OtherPatientNames", "InstitutionName", "InstitutionAddress", "ReferringPhysicianName",
                   "PerformingPhysicianName", "OperatorsName", "StudyDate", "SeriesDate", "AcquisitionDate", "ContentDate",
                   "StudyTime", "AccessionNumber", "StudyID", "StationName", "DeviceSerialNumber"]


def _fernet() -> Fernet:
    s = get_settings()
    semilla = s.clave_cifrado_estudios or s.jwt_secreto
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(semilla.encode()).digest()))


def desidentificar(nombre: str, contenido: bytes) -> tuple[bytes, bool]:
    """Devuelve la imagen como PNG sin ningún metadato y si puede tener texto sobreimpreso.

    Se guarda solo la matriz de píxeles: los metadatos EXIF o DICOM no pasan al archivo final.
    """
    import numpy as np
    from PIL import Image

    tipo = EXTENSIONES.get(Path(nombre).suffix.lower())
    if tipo is None:
        raise ErrorNegocio("Formato no permitido. Usa JPG, PNG o DICOM (.dcm).", 415)
    if len(contenido) > MAX_BYTES:
        raise ErrorNegocio("El archivo supera el tamaño máximo de 20 MB.", 413)
    advertencia = False
    try:
        if tipo == "dicom":
            import pydicom

            ds = pydicom.dcmread(io.BytesIO(contenido))
            advertencia = str(getattr(ds, "BurnedInAnnotation", "")).upper() == "YES"
            pixeles = ds.pixel_array.astype(np.float32)
            if pixeles.ndim == 3 and pixeles.shape[-1] not in (3, 4):
                pixeles = pixeles[0]
            pixeles = 255 * (pixeles - pixeles.min()) / max(float(pixeles.max() - pixeles.min()), 1.0)
            imagen = Image.fromarray(pixeles.astype(np.uint8)).convert("RGB")
        else:
            imagen = Image.open(io.BytesIO(contenido)).convert("RGB")
    except ErrorNegocio:
        raise
    except Exception as exc:
        raise ErrorNegocio("No pudimos leer la imagen. Verifica que el archivo no esté dañado.", 422) from exc
    limpia = Image.fromarray(np.asarray(imagen))  # imagen nueva: no conserva EXIF ni otros metadatos
    salida = io.BytesIO()
    limpia.save(salida, format="PNG")
    return salida.getvalue(), advertencia


# Las rutas con este prefijo indican que el archivo cifrado está en la tabla estudio_contenido (db/08).
# Las demás son archivos en ESTUDIOS_DIR, de instalaciones anteriores a este cambio.
PREFIJO_BASE = "base:"


def guardar_cifrado(db: Session, id_estudio: int, png: bytes) -> str:
    """Guarda el estudio cifrado en la base; así no se pierde si el servidor se reinicia."""
    db.execute(text("""INSERT INTO estudio_contenido (id_estudio, datos_cifrados) VALUES (:e, :d)
                       ON CONFLICT (id_estudio) DO UPDATE SET datos_cifrados = EXCLUDED.datos_cifrados"""),
               {"e": id_estudio, "d": _fernet().encrypt(png)})
    return f"{PREFIJO_BASE}{id_estudio}"


def leer_cifrado(db: Session, ruta: str) -> bytes:
    if ruta.startswith(PREFIJO_BASE):
        datos = db.execute(text("SELECT datos_cifrados FROM estudio_contenido WHERE id_estudio = :e"),
                           {"e": int(ruta.removeprefix(PREFIJO_BASE))}).scalar()
    else:
        archivo = Path(ruta)
        datos = archivo.read_bytes() if ruta and archivo.is_file() else None
    if datos is None:
        raise ErrorNegocio("La imagen de este estudio ya no está disponible.", 404)
    return _fernet().decrypt(bytes(datos))


def borrar(db: Session, ruta: str) -> None:
    if ruta.startswith(PREFIJO_BASE):
        db.execute(text("DELETE FROM estudio_contenido WHERE id_estudio = :e"), {"e": int(ruta.removeprefix(PREFIJO_BASE))})
    else:
        Path(ruta).unlink(missing_ok=True)
