"""M10 Estudios propios (RF-010): carga cifrada, desidentificación, interpretación experimental y compartir."""
import hashlib
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.deps import PROFESIONAL, USUARIO, requiere_rol, usuario_actual
from app.core.errores import ErrorNegocio
from app.core.textos import ROTULO_IA
from app.modules.estudios import seguridad
from app.modules.estudios.vision import CON_REGION, obtener_modelo
from app.modules.tutor.servicio import crear_servicio
from app.modules.usuarios.service import bitacora

router = APIRouter(tags=["Estudios propios"])

PREGUNTA_ESTUDIO = ("Explica este resultado en lenguaje sencillo y sugiere tres preguntas que la persona pueda llevar a su médico. "
                    "No des indicaciones de tratamiento.")
EXPLICACION_FIJA = {
    True: ("El modelo experimental marcó una zona de la imagen que se parece a un pólipo en los datos con los que fue entrenado. "
           "Esto no confirma nada: solo su médico puede interpretar su estudio. Preguntas para su médico: ¿qué muestra esta zona?, "
           "¿hace falta algún estudio adicional?, ¿cada cuánto debo repetir la colonoscopia?"),
    False: ("El modelo experimental no marcó zonas parecidas a un pólipo. Esto no descarta hallazgos: el modelo puede equivocarse "
            "y solo su médico puede interpretar su estudio. Preguntas para su médico: ¿qué se observa en mi estudio?, "
            "¿cuándo debo hacer el próximo control?"),
}


class CompartirIn(BaseModel):
    id_vinculo: int | None = Field(default=None, description="Vínculo activo con el profesional; vacío para dejar de compartir")


class ComentarioIn(BaseModel):
    texto: str = Field(min_length=3, max_length=2000)


def _interpretar(db: Session, id_estudio: int, png: bytes) -> bool:
    """RF-010 10.3: modelo de visión + explicación del tutor. La IA solo recibe la imagen ya desidentificada
    y el resultado del modelo, nunca datos de la persona (IE-02)."""
    modelo = obtener_modelo()
    if modelo is None:
        return False
    r = modelo.analizar(png)
    con_region = r.clasificacion == CON_REGION
    tutor = crear_servicio().explicar(
        "Estudio de colonoscopia cargado por la persona usuaria.",
        f"El modelo experimental de visión indica: {r.clasificacion}, con una confianza de {r.confianza} %.",
        EXPLICACION_FIJA[con_region], PREGUNTA_ESTUDIO)
    db.execute(text("""INSERT INTO interpretacion_estudio (id_estudio, roi, clasificacion, confianza, explicacion, version_modelo)
                       VALUES (:e, CAST(:r AS jsonb), :c, :f, :x, :v)"""),
               {"e": id_estudio, "r": json.dumps(r.roi or {}), "c": r.clasificacion, "f": r.confianza, "x": tutor.texto,
                "v": r.version_modelo})
    return True


def _estudio(db: Session, id_estudio: int, quien: dict) -> dict:
    """El estudio solo lo ve su dueño o el profesional con quien lo compartió (RF-010 10.1 y 10.4)."""
    fila = db.execute(text("""SELECT e.*, e.id_usuario::text AS dueno, e.id_profesional_compartido::text AS compartido_con
                              FROM estudio_propio e WHERE e.id_estudio = :e AND NOT e.eliminado"""), {"e": id_estudio}).mappings().first()
    if fila is None or quien["sub"] not in (fila["dueno"], fila["compartido_con"]):
        raise HTTPException(404, "Estudio no encontrado.")
    if quien["sub"] == fila["compartido_con"]:
        vigente = db.execute(text("""SELECT 1 FROM vinculo WHERE id_usuario = CAST(:u AS uuid) AND id_profesional = CAST(:p AS uuid)
                                     AND fecha_fin IS NULL"""), {"u": fila["dueno"], "p": quien["sub"]}).first()
        if not vigente:
            raise HTTPException(404, "Estudio no encontrado.")
    return dict(fila)


@router.post("/estudios", status_code=status.HTTP_201_CREATED)
async def cargar(archivo: UploadFile = File(...), confirma_sin_datos_visibles: bool = Form(False), db: Session = Depends(get_db),
                 usuario: dict = Depends(requiere_rol(USUARIO))) -> dict:
    """RF-010 10.1 y 10.2."""
    if get_settings().entorno == "demostracion":
        # Ley 1581: el enlace público de demostración no recibe estudios reales de personas.
        raise HTTPException(403, "En la versión de demostración no se pueden cargar estudios. Esta función se habilita en la "
                                 "instalación oficial de la plataforma.")
    sensibles = db.execute(text("""SELECT aceptada FROM autorizacion_datos WHERE id_usuario = CAST(:u AS uuid)
                                   AND tipo = 'datos_sensibles'"""), {"u": usuario["sub"]}).scalar()
    if not sensibles:
        raise HTTPException(403, "Para cargar estudios primero autoriza el tratamiento de datos sensibles en Mis datos.")
    if not confirma_sin_datos_visibles:
        raise HTTPException(422, "Confirma que la imagen no muestra tu nombre ni otros datos personales escritos sobre ella.")
    try:
        png, advertencia = seguridad.desidentificar(archivo.filename or "", await archivo.read())
    except ErrorNegocio as e:
        raise HTTPException(e.codigo, e.mensaje) from e
    id_estudio = db.execute(text("""INSERT INTO estudio_propio (id_usuario, ruta_cifrada, hash_sha256, desidentificado, advertencia_texto)
                                    VALUES (CAST(:u AS uuid), '', :h, TRUE, :a) RETURNING id_estudio"""),
                            {"u": usuario["sub"], "h": hashlib.sha256(png).hexdigest(), "a": advertencia}).scalar_one()
    ruta = seguridad.guardar_cifrado(id_estudio, png)
    db.execute(text("UPDATE estudio_propio SET ruta_cifrada = :r WHERE id_estudio = :e"), {"r": ruta, "e": id_estudio})
    procesado = _interpretar(db, id_estudio, png)
    bitacora(db, usuario["sub"], "estudio_propio", str(id_estudio), "cargar")
    db.commit()
    return {"id_estudio": id_estudio, "procesado": procesado,
            "advertencia": "La imagen podría tener texto sobreimpreso; revisa que no muestre tus datos." if advertencia else None}


@router.get("/estudios")
def mis_estudios(db: Session = Depends(get_db), usuario: dict = Depends(requiere_rol(USUARIO))) -> list[dict]:
    """RF-010 10.5: fecha de carga y estado (procesado, compartido)."""
    filas = db.execute(text("""SELECT e.id_estudio, e.fecha_carga, e.advertencia_texto,
                                      EXISTS (SELECT 1 FROM interpretacion_estudio i WHERE i.id_estudio = e.id_estudio) AS procesado,
                                      p.nombre AS compartido_con,
                                      (SELECT count(*) FROM comentario_estudio c WHERE c.id_estudio = e.id_estudio AND NOT c.leido)
                                      AS comentarios_nuevos
                               FROM estudio_propio e LEFT JOIN usuario p ON p.id_usuario = e.id_profesional_compartido
                               WHERE e.id_usuario = CAST(:u AS uuid) AND NOT e.eliminado ORDER BY e.fecha_carga DESC"""),
                       {"u": usuario["sub"]}).mappings().all()
    return [dict(f) for f in filas]


@router.get("/estudios/{id_estudio}")
def ver_estudio(id_estudio: int, db: Session = Depends(get_db), quien: dict = Depends(usuario_actual)) -> dict:
    e = _estudio(db, id_estudio, quien)
    interp = db.execute(text("""SELECT roi, clasificacion, confianza, explicacion, version_modelo, fecha FROM interpretacion_estudio
                                WHERE id_estudio = :e ORDER BY fecha DESC LIMIT 1"""), {"e": id_estudio}).mappings().first()
    comentarios = db.execute(text("""SELECT c.id_comentario, u.nombre AS profesional, c.texto, c.fecha, c.leido
                                     FROM comentario_estudio c JOIN usuario u ON u.id_usuario = c.id_profesional
                                     WHERE c.id_estudio = :e ORDER BY c.fecha"""), {"e": id_estudio}).mappings().all()
    if quien["sub"] == e["dueno"]:
        db.execute(text("UPDATE comentario_estudio SET leido = TRUE WHERE id_estudio = :e"), {"e": id_estudio})
    else:
        bitacora(db, quien["sub"], "estudio_propio", str(id_estudio), "consultar")
    db.commit()
    return {"id_estudio": id_estudio, "fecha_carga": e["fecha_carga"], "compartido": e["compartido_con"] is not None,
            "advertencia_texto": e["advertencia_texto"],
            "interpretacion": (dict(interp) | {"confianza": float(interp["confianza"]), "rotulo": ROTULO_IA}) if interp else None,
            "comentarios": [dict(c) for c in comentarios]}


@router.get("/estudios/{id_estudio}/imagen")
def imagen(id_estudio: int, db: Session = Depends(get_db), quien: dict = Depends(usuario_actual)) -> Response:
    e = _estudio(db, id_estudio, quien)
    return Response(seguridad.leer_cifrado(e["ruta_cifrada"]), media_type="image/png", headers={"Cache-Control": "no-store"})


@router.put("/estudios/{id_estudio}/compartir", status_code=status.HTTP_204_NO_CONTENT)
def compartir(id_estudio: int, datos: CompartirIn, db: Session = Depends(get_db), usuario: dict = Depends(requiere_rol(USUARIO))) -> None:
    """RF-010 10.4: compartir es opcional y se puede revocar."""
    _estudio(db, id_estudio, usuario)
    profesional = None
    if datos.id_vinculo is not None:
        profesional = db.execute(text("""SELECT id_profesional::text FROM vinculo WHERE id_vinculo = :v
                                         AND id_usuario = CAST(:u AS uuid) AND fecha_fin IS NULL"""),
                                 {"v": datos.id_vinculo, "u": usuario["sub"]}).scalar()
        if profesional is None:
            raise HTTPException(404, "Vínculo no encontrado.")
    db.execute(text("UPDATE estudio_propio SET id_profesional_compartido = CAST(:p AS uuid) WHERE id_estudio = :e"),
               {"p": profesional, "e": id_estudio})
    bitacora(db, usuario["sub"], "estudio_propio", str(id_estudio), "compartir" if profesional else "dejar_de_compartir")
    db.commit()


@router.delete("/estudios/{id_estudio}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id_estudio: int, db: Session = Depends(get_db), usuario: dict = Depends(requiere_rol(USUARIO))) -> None:
    """RF-010 10.5: borra el archivo y su interpretación del almacenamiento."""
    e = _estudio(db, id_estudio, usuario)
    seguridad.borrar(e["ruta_cifrada"])
    db.execute(text("DELETE FROM interpretacion_estudio WHERE id_estudio = :e"), {"e": id_estudio})
    db.execute(text("DELETE FROM comentario_estudio WHERE id_estudio = :e"), {"e": id_estudio})
    db.execute(text("""UPDATE estudio_propio SET eliminado = TRUE, ruta_cifrada = '', id_profesional_compartido = NULL
                       WHERE id_estudio = :e"""), {"e": id_estudio})
    bitacora(db, usuario["sub"], "estudio_propio", str(id_estudio), "eliminar")
    db.commit()


@router.get("/profesional/estudios")
def estudios_compartidos(db: Session = Depends(get_db), prof: dict = Depends(requiere_rol(PROFESIONAL))) -> list[dict]:
    filas = db.execute(text("""SELECT e.id_estudio, u.nombre AS usuario, e.fecha_carga,
                                      (SELECT count(*) FROM comentario_estudio c WHERE c.id_estudio = e.id_estudio) AS comentarios
                               FROM estudio_propio e JOIN usuario u ON u.id_usuario = e.id_usuario
                               JOIN vinculo v ON v.id_usuario = e.id_usuario AND v.id_profesional = e.id_profesional_compartido
                                             AND v.fecha_fin IS NULL
                               WHERE e.id_profesional_compartido = CAST(:p AS uuid) AND NOT e.eliminado
                               ORDER BY e.fecha_carga DESC"""), {"p": prof["sub"]}).mappings().all()
    return [dict(f) for f in filas]


@router.post("/estudios/{id_estudio}/comentarios", status_code=status.HTTP_201_CREATED)
def comentar(id_estudio: int, datos: ComentarioIn, db: Session = Depends(get_db), prof: dict = Depends(requiere_rol(PROFESIONAL))) -> dict:
    """RF-010 10.4: comentario educativo del profesional; la persona lo ve como aviso nuevo."""
    _estudio(db, id_estudio, prof)
    id_c = db.execute(text("""INSERT INTO comentario_estudio (id_estudio, id_profesional, texto)
                              VALUES (:e, CAST(:p AS uuid), :t) RETURNING id_comentario"""),
                      {"e": id_estudio, "p": prof["sub"], "t": datos.texto}).scalar_one()
    bitacora(db, prof["sub"], "comentario_estudio", str(id_c), "crear")
    db.commit()
    return {"id_comentario": id_c}


@router.get("/notificaciones")
def notificaciones(db: Session = Depends(get_db), usuario: dict = Depends(usuario_actual)) -> dict:
    nuevos = db.execute(text("""SELECT count(*) FROM comentario_estudio c JOIN estudio_propio e ON e.id_estudio = c.id_estudio
                                WHERE e.id_usuario = CAST(:u AS uuid) AND NOT c.leido AND NOT e.eliminado"""),
                        {"u": usuario["sub"]}).scalar()
    return {"comentarios_nuevos": nuevos}
