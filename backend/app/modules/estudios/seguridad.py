"""RF-010 10.2 y RNF-003: desidentificación de imágenes y cifrado en reposo."""
import base64
import hashlib
import io
from pathlib import Path

from cryptography.fernet import Fernet

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


def guardar_cifrado(id_estudio: int, png: bytes) -> str:
    ruta = Path(get_settings().estudios_dir) / f"{id_estudio}.bin"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(_fernet().encrypt(png))
    return ruta.as_posix()


def leer_cifrado(ruta: str) -> bytes:
    return _fernet().decrypt(Path(ruta).read_bytes())


def borrar(ruta: str) -> None:
    Path(ruta).unlink(missing_ok=True)
