"""Reglas de negocio de M02 Casos clínicos (RF-002) y desbloqueo por nivel (RF-006 6.1)."""
import hashlib
import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.errores import ErrorNegocio
from app.modules.casos.schemas import CasoIn, EtapaIn
from app.modules.usuarios.service import bitacora

FORMATOS = {".jpg": "imagen", ".jpeg": "imagen", ".png": "imagen", ".mp4": "video"}
MAX_BYTES = {"imagen": 10 * 1024 * 1024, "video": 100 * 1024 * 1024}
TIPOS_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".mp4": "video/mp4"}


def dificultad_maxima(db: Session, id_usuario: str) -> int:
    """RF-006 6.1: Explorador hasta dificultad 2, el segundo nivel hasta 4 y el tercero todos."""
    posicion = db.execute(text("""SELECT count(*) FROM nivel n2, usuario u JOIN nivel n ON n.id_nivel = u.id_nivel
                                  WHERE u.id_usuario = CAST(:u AS uuid) AND n2.puntaje_minimo <= n.puntaje_minimo"""),
                          {"u": id_usuario}).scalar() or 1
    return {1: 2, 2: 4}.get(posicion, 5)


def niveles_por_dificultad(db: Session) -> dict[int, str]:
    nombres = [r[0] for r in db.execute(text("SELECT nombre FROM nivel ORDER BY puntaje_minimo"))]
    nombres += [nombres[-1]] * (3 - len(nombres))
    return {1: nombres[0], 2: nombres[0], 3: nombres[1], 4: nombres[1], 5: nombres[2]}


def _caso_editable(db: Session, id_caso: int) -> dict:
    caso = db.execute(text("SELECT * FROM caso WHERE id_caso = :c AND NOT eliminado"), {"c": id_caso}).mappings().first()
    if caso is None:
        raise ErrorNegocio("Caso no encontrado.", 404)
    return dict(caso)


def contenido(db: Session, id_caso: int) -> dict:
    caso = _caso_editable(db, id_caso)
    etapas = db.execute(text("SELECT * FROM etapa WHERE id_caso = :c ORDER BY orden"), {"c": id_caso}).mappings().all()
    salida = {k: (str(v) if v is not None and not isinstance(v, int | bool | str) else v) for k, v in caso.items()}
    salida["etapas"] = []
    for e in etapas:
        opciones = db.execute(text("SELECT * FROM opcion_decision WHERE id_etapa = :e ORDER BY id_opcion"),
                              {"e": e["id_etapa"]}).mappings().all()
        recursos = db.execute(text("""SELECT r.id_recurso, r.tipo, r.ruta_almacenamiento, r.licencia, d.nombre AS dataset,
                                             d.fuente_url FROM recurso_multimedia r LEFT JOIN dataset d ON d.id_dataset = r.id_dataset
                                      WHERE r.id_etapa = :e ORDER BY r.id_recurso"""), {"e": e["id_etapa"]}).mappings().all()
        salida["etapas"].append(dict(e) | {"opciones": [dict(o) for o in opciones], "recursos": [dict(r) for r in recursos]})
    return salida


def _guardar_version(db: Session, id_caso: int, editor: str) -> None:
    """RF-002 2.1b: se conserva la versión anterior antes de cada cambio."""
    numero = db.execute(text("SELECT coalesce(max(numero), 0) + 1 FROM caso_version WHERE id_caso = :c"), {"c": id_caso}).scalar()
    db.execute(text("""INSERT INTO caso_version (id_caso, numero, contenido, id_editor)
                       VALUES (:c, :n, CAST(:j AS jsonb), CAST(:u AS uuid))"""),
               {"c": id_caso, "n": numero, "j": json.dumps(contenido(db, id_caso), default=str), "u": editor})


def crear_caso(db: Session, autor: str, datos: CasoIn) -> int:
    id_caso = db.execute(text("""INSERT INTO caso (id_autor, titulo, tema, nivel_dificultad, descripcion, contexto_simulado)
                                 VALUES (CAST(:a AS uuid), :t, :m, :n, :d, :x) RETURNING id_caso"""),
                         {"a": autor, "t": datos.titulo, "m": datos.tema, "n": datos.nivel_dificultad,
                          "d": datos.descripcion, "x": datos.contexto_simulado}).scalar_one()
    bitacora(db, autor, "caso", str(id_caso), "crear")
    db.commit()
    return id_caso


def editar_caso(db: Session, editor: str, id_caso: int, datos: CasoIn) -> None:
    """RF-002 2.1b: editar devuelve el caso a Borrador para una nueva revisión."""
    _caso_editable(db, id_caso)
    _guardar_version(db, id_caso, editor)
    db.execute(text("""UPDATE caso SET titulo = :t, tema = :m, nivel_dificultad = :n, descripcion = :d, contexto_simulado = :x,
                              estado = 'borrador', id_revisor = NULL, fecha_revision = NULL, fecha_publicacion = NULL
                       WHERE id_caso = :c"""),
               {"t": datos.titulo, "m": datos.tema, "n": datos.nivel_dificultad, "d": datos.descripcion,
                "x": datos.contexto_simulado, "c": id_caso})
    bitacora(db, editor, "caso", str(id_caso), "editar")
    db.commit()


def guardar_etapa(db: Session, editor: str, id_caso: int, datos: EtapaIn) -> int:
    """RF-002 2.3 y 2.4: crea o reemplaza la etapa con ese orden, con sus opciones."""
    _caso_editable(db, id_caso)
    _guardar_version(db, id_caso, editor)
    usada = db.execute(text("""SELECT 1 FROM decision d JOIN etapa e ON e.id_etapa = d.id_etapa
                               WHERE e.id_caso = :c AND e.orden = :o LIMIT 1"""), {"c": id_caso, "o": datos.orden}).first()
    if usada:
        # RF-007 7.1: los registros de decisiones no se pueden modificar.
        raise ErrorNegocio("Esta etapa ya tiene decisiones registradas y no se puede cambiar. Crea un caso nuevo.", 409)
    db.execute(text("DELETE FROM etapa WHERE id_caso = :c AND orden = :o"), {"c": id_caso, "o": datos.orden})
    id_etapa = db.execute(text("""INSERT INTO etapa (id_caso, orden, enunciado, recomendacion_ia, ia_erronea_intencional, usa_modelo_vision)
                                  VALUES (:c, :o, :e, :r, :i, :v) RETURNING id_etapa"""),
                          {"c": id_caso, "o": datos.orden, "e": datos.enunciado, "r": datos.recomendacion_ia,
                           "i": datos.ia_erronea_intencional, "v": datos.usa_modelo_vision}).scalar_one()
    for o in datos.opciones:
        db.execute(text("""INSERT INTO opcion_decision (id_etapa, texto, es_correcta, retroalimentacion, puntaje, fuente, recomendada_ia)
                           VALUES (:e, :t, :c, :r, :p, :f, :i)"""),
                   {"e": id_etapa, "t": o.texto, "c": o.es_correcta, "r": o.retroalimentacion, "p": o.puntaje,
                    "f": o.fuente, "i": o.recomendada_ia})
    db.execute(text("""UPDATE caso SET estado = 'borrador', id_revisor = NULL, fecha_revision = NULL, fecha_publicacion = NULL
                       WHERE id_caso = :c"""), {"c": id_caso})
    bitacora(db, editor, "etapa", str(id_etapa), "guardar")
    db.commit()
    return id_etapa


def guardar_recurso(db: Session, editor: str, id_etapa: int, nombre: str, contenido_archivo: bytes, id_dataset: int,
                    licencia: str) -> int:
    """RF-002 2.2: solo JPG, PNG o MP4, con tamaño máximo y con fuente (dataset) y licencia obligatorias."""
    extension = Path(nombre).suffix.lower()
    tipo = FORMATOS.get(extension)
    if tipo is None:
        raise ErrorNegocio("Formato no permitido. Usa JPG, PNG o MP4.", 415)
    if len(contenido_archivo) > MAX_BYTES[tipo]:
        raise ErrorNegocio("El archivo supera el tamaño máximo permitido.", 413)
    if not licencia.strip():
        raise ErrorNegocio("Registra la licencia del recurso.", 422)
    if not db.execute(text("SELECT 1 FROM dataset WHERE id_dataset = :d"), {"d": id_dataset}).first():
        raise ErrorNegocio("Indica el dataset público de origen.", 422)
    id_caso = db.execute(text("SELECT id_caso FROM etapa WHERE id_etapa = :e"), {"e": id_etapa}).scalar()
    if id_caso is None:
        raise ErrorNegocio("Etapa no encontrada.", 404)
    id_recurso = db.execute(text("""INSERT INTO recurso_multimedia (id_etapa, id_dataset, tipo, ruta_almacenamiento, licencia)
                                    VALUES (:e, :d, :t, '', :l) RETURNING id_recurso"""),
                            {"e": id_etapa, "d": id_dataset, "t": tipo, "l": licencia}).scalar_one()
    # El contenido se guarda en la base para que no se pierda si el servidor se reinicia; se publica en /media/recursos/.
    db.execute(text("""INSERT INTO recurso_contenido (id_recurso, tipo_mime, tamano_bytes, sha256, datos)
                       VALUES (:i, :m, :t, :h, :d)"""),
               {"i": id_recurso, "m": TIPOS_MIME[extension], "t": len(contenido_archivo),
                "h": hashlib.sha256(contenido_archivo).hexdigest(), "d": contenido_archivo})
    db.execute(text("UPDATE recurso_multimedia SET ruta_almacenamiento = :r WHERE id_recurso = :i"),
               {"r": f"recursos/{id_recurso}{extension}", "i": id_recurso})
    bitacora(db, editor, "recurso_multimedia", str(id_recurso), "crear")
    db.commit()
    return id_recurso


def revisar(db: Session, revisor: str, id_caso: int, accion: str, fuente_clinica: str | None) -> str:
    """RF-002 2.5: Borrador → Revisado → Publicado. El autor no puede revisar su propio caso."""
    caso = _caso_editable(db, id_caso)
    if str(caso["id_autor"]) == revisor:
        raise ErrorNegocio("El autor del caso no puede ser su propio revisor.", 403)
    if accion == "aprobar":
        if caso["estado"] != "borrador":
            raise ErrorNegocio("Solo se aprueban casos en borrador.", 409)
        if not (fuente_clinica and fuente_clinica.strip()):
            raise ErrorNegocio("Registra la fuente clínica de respaldo.", 422)
        etapas_validas = db.execute(text("""SELECT count(*) FROM etapa e WHERE e.id_caso = :c AND EXISTS
                                            (SELECT 1 FROM opcion_decision o WHERE o.id_etapa = e.id_etapa AND o.es_correcta)"""),
                                    {"c": id_caso}).scalar()
        if not etapas_validas:
            raise ErrorNegocio("El caso necesita al menos una etapa con solución esperada.", 422)
        db.execute(text("""UPDATE caso SET estado = 'revisado', id_revisor = CAST(:r AS uuid), fuente_clinica = :f,
                                  fecha_revision = now() WHERE id_caso = :c"""), {"r": revisor, "f": fuente_clinica, "c": id_caso})
        nuevo = "revisado"
    elif accion == "publicar":
        if caso["estado"] != "revisado":
            raise ErrorNegocio("Solo se publican casos revisados.", 409)
        db.execute(text("UPDATE caso SET estado = 'publicado', fecha_publicacion = now() WHERE id_caso = :c"), {"c": id_caso})
        nuevo = "publicado"
    else:
        db.execute(text("""UPDATE caso SET estado = 'borrador', id_revisor = NULL, fecha_revision = NULL, fecha_publicacion = NULL
                           WHERE id_caso = :c"""), {"c": id_caso})
        nuevo = "borrador"
    bitacora(db, revisor, "caso", str(id_caso), accion, {"fuente_clinica": fuente_clinica} if fuente_clinica else None)
    db.commit()
    return nuevo


def eliminar_caso(db: Session, editor: str, id_caso: int) -> None:
    """RF-002 2.1c: borrado lógico; los intentos ya hechos se conservan."""
    _caso_editable(db, id_caso)
    db.execute(text("UPDATE caso SET eliminado = TRUE WHERE id_caso = :c"), {"c": id_caso})
    bitacora(db, editor, "caso", str(id_caso), "eliminar")
    db.commit()
