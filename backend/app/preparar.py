"""Prepara la base al arrancar el despliegue público (Render).

1. Carga el esquema (db/*.sql) si la base está vacía.
2. Crea el primer administrador con ADMIN_CORREO, ADMIN_NOMBRE y ADMIN_CONTRASENA si aún no existe.
3. Con CASO_DEMO=1 publica un caso de demostración con texto de prueba (sin contenido clínico) para recorrer el flujo
   mientras los profesionales de la salud escriben los casos reales.
4. Si existe la imagen de ejemplo de HyperKvasir (imagen segmentada de la partición de prueba del modelo de visión), la agrega a la etapa 1 del
   caso de demostración con el modelo de visión activado, para mostrar su resultado en el enlace público.
5. Agrega a la etapa 2 del caso de demostración las imágenes de HyperKvasir de la carpeta app/demo (preparación intestinal
   y resección), cada una una sola vez.

Cada paso es idempotente: se puede ejecutar en cada arranque. Uso: python -m app.preparar
"""
import hashlib
import json
import os
import secrets
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import SessionLocal, engine
from app.core.security import hash_contrasena, verificar_contrasena
from app.modules.casos import service as casos
from app.modules.casos.schemas import CasoIn, EtapaIn, OpcionIn
from app.modules.usuarios.schemas import validar_contrasena

TITULO_DEMO = "Caso de demostración del simulador"


# Scripts de la versión inicial (01 a 04): solo se ejecutan sobre una base vacía. Del 05 en adelante los scripts son
# idempotentes y se aplican en cada arranque, así las bases que ya existen reciben los cambios nuevos.
ULTIMO_SCRIPT_INICIAL = "04"


def aplicar_esquema() -> bool:
    """Carga el esquema completo en una base vacía o aplica los scripts nuevos a una base existente.

    Devuelve True si la base estaba vacía.
    """
    with engine.connect() as c:
        vacia = not c.execute(text("SELECT to_regclass('public.usuario')")).scalar()
    scripts = sorted(Path(get_settings().esquema_dir).glob("*.sql"))
    if not vacia:
        scripts = [a for a in scripts if a.name[:2] > ULTIMO_SCRIPT_INICIAL]
    crudo = engine.raw_connection()
    try:
        crudo.driver_connection.autocommit = True
        with crudo.driver_connection.cursor() as cur:
            for archivo in scripts:
                cur.execute(archivo.read_text(encoding="utf-8"))
                print(f"Esquema: {archivo.name} aplicado.")
    finally:
        crudo.close()
    return vacia


def _crear_usuario(db: Session, rol: str, nombre: str, correo: str, contrasena: str) -> str:
    return str(db.execute(text("""INSERT INTO usuario (id_rol, nombre, correo, hash_contrasena, rango_edad)
                                  VALUES ((SELECT id_rol FROM rol WHERE nombre = :r), :n, lower(:c), :h, '30-39')
                                  RETURNING id_usuario"""),
                          {"r": rol, "n": nombre, "c": correo, "h": hash_contrasena(contrasena)}).scalar_one())


def crear_admin_inicial(db: Session) -> bool:
    """Crea el administrador inicial o, si ya existe, deja su contraseña igual a ADMIN_CONTRASENA y lo desbloquea.

    Los campos de Render admiten varias líneas: se quitan espacios y saltos de línea al inicio y al final.
    """
    correo, contrasena = os.getenv("ADMIN_CORREO", "").strip(), os.getenv("ADMIN_CONTRASENA", "").strip()
    if not (correo and contrasena):
        return False
    validar_contrasena(contrasena)
    existente = db.execute(text("SELECT id_usuario, hash_contrasena FROM usuario WHERE lower(correo) = lower(:c)"),
                           {"c": correo}).first()
    if existente:
        if not verificar_contrasena(contrasena, existente.hash_contrasena):
            db.execute(text("""UPDATE usuario SET hash_contrasena = :h, intentos_fallidos = 0, bloqueado_hasta = NULL
                               WHERE id_usuario = :u"""), {"h": hash_contrasena(contrasena), "u": existente.id_usuario})
            db.commit()
            print("Contraseña del administrador inicial actualizada desde ADMIN_CONTRASENA.")
        return False
    _crear_usuario(db, "Administrador", os.getenv("ADMIN_NOMBRE", "Administrador"), correo, contrasena)
    db.commit()
    print("Administrador inicial creado.")
    return True


def publicar_caso_demo(db: Session) -> bool:
    if os.getenv("CASO_DEMO", "") != "1":
        return False
    if db.execute(text("SELECT 1 FROM caso WHERE titulo = :t AND NOT eliminado"), {"t": TITULO_DEMO}).first():
        return False
    # Autor y revisor internos: cuentas sin contraseña conocida, solo para firmar el caso de demostración.
    autor = _crear_usuario(db, "Profesional de la salud", "Autor de demostración",
                           f"demo-autor-{secrets.token_hex(3)}@ejemplo.com", secrets.token_urlsafe(24) + "a1")
    revisor = _crear_usuario(db, "Profesional de la salud", "Revisor de demostración",
                             f"demo-revisor-{secrets.token_hex(3)}@ejemplo.com", secrets.token_urlsafe(24) + "a1")
    db.commit()
    id_caso = casos.crear_caso(db, autor, CasoIn(
        titulo=TITULO_DEMO, tema="pólipos", nivel_dificultad=1,
        descripcion="Caso de prueba para conocer cómo funciona el simulador. El texto no tiene contenido clínico.",
        contexto_simulado="Persona simulada de demostración."))
    for orden in (1, 2):
        opciones = [OpcionIn(texto=f"Opción {x}", puntaje=p, es_correcta=p == 100, recomendada_ia=x == "A",
                             retroalimentacion="Explicación de demostración: aquí el profesional explica la respuesta.",
                             fuente="Texto de demostración") for x, p in (("A", 100), ("B", 0))]
        casos.guardar_etapa(db, autor, id_caso, EtapaIn(
            orden=orden, enunciado=f"Etapa {orden} de demostración. Aquí irá la pregunta del caso clínico.",
            recomendacion_ia="Sugerencia de demostración del tutor de IA.", opciones=opciones))
    casos.revisar(db, revisor, id_caso, "aprobar", "Texto de demostración")
    casos.revisar(db, revisor, id_caso, "publicar", None)
    print(f"Caso de demostración publicado: {id_caso}")
    return True


def agregar_imagen_demo(db: Session, ruta: str | None = None) -> bool:
    """Agrega la imagen de ejemplo de HyperKvasir a la etapa 1 del caso de demostración (una sola vez)."""
    archivo = Path(ruta or os.getenv("IMAGEN_DEMO", "modelos/ejemplo-kvasir.jpg"))
    if not archivo.is_file():
        return False
    etapa = db.execute(text("""SELECT e.id_etapa, c.id_autor FROM etapa e JOIN caso c ON c.id_caso = e.id_caso
                               WHERE c.titulo = :t AND NOT c.eliminado AND e.orden = 1"""), {"t": TITULO_DEMO}).first()
    if etapa is None or db.execute(text("SELECT 1 FROM recurso_multimedia WHERE id_etapa = :e"), {"e": etapa.id_etapa}).first():
        return False
    id_dataset = db.execute(text("SELECT id_dataset FROM dataset WHERE nombre = 'HyperKvasir'")).scalar()
    if id_dataset is None:
        return False
    casos.guardar_recurso(db, str(etapa.id_autor), etapa.id_etapa, archivo.name, archivo.read_bytes(), id_dataset,
                          "HyperKvasir (Borgli et al., 2020), CC BY 4.0")
    db.execute(text("UPDATE etapa SET usa_modelo_vision = TRUE WHERE id_etapa = :e"), {"e": etapa.id_etapa})
    db.commit()
    print("Imagen de ejemplo de HyperKvasir agregada al caso de demostración.")
    return True


IMAGENES_ETAPA_2 = ("preparacion-intestinal.jpg", "reseccion.jpg")
LICENCIA_HYPERKVASIR = "HyperKvasir (Borgli et al., 2020), CC BY 4.0"


def agregar_imagenes_etapa_2(db: Session, carpeta: str | None = None) -> int:
    """Agrega a la etapa 2 del caso de demostración las imágenes de HyperKvasir que aún no tiene. Devuelve cuántas agregó."""
    base = Path(carpeta) if carpeta else Path(__file__).parent / "demo"
    etapa = db.execute(text("""SELECT e.id_etapa, c.id_autor FROM etapa e JOIN caso c ON c.id_caso = e.id_caso
                               WHERE c.titulo = :t AND NOT c.eliminado AND e.orden = 2"""), {"t": TITULO_DEMO}).first()
    id_dataset = db.execute(text("SELECT id_dataset FROM dataset WHERE nombre = 'HyperKvasir'")).scalar()
    if etapa is None or id_dataset is None:
        return 0
    agregadas = 0
    for nombre in IMAGENES_ETAPA_2:
        archivo = base / nombre
        if not archivo.is_file():
            continue
        contenido = archivo.read_bytes()
        ya_esta = db.execute(text("""SELECT 1 FROM recurso_multimedia r JOIN recurso_contenido rc ON rc.id_recurso = r.id_recurso
                                     WHERE r.id_etapa = :e AND rc.sha256 = :h"""),
                             {"e": etapa.id_etapa, "h": hashlib.sha256(contenido).hexdigest()}).first()
        if ya_esta:
            continue
        casos.guardar_recurso(db, str(etapa.id_autor), etapa.id_etapa, nombre, contenido, id_dataset, LICENCIA_HYPERKVASIR)
        agregadas += 1
    db.commit()
    if agregadas:
        print(f"Imágenes de HyperKvasir agregadas a la etapa 2 del caso de demostración: {agregadas}")
    return agregadas


# RF-002: casos aportados por Valentina (PR #25 y PR #36 a #38). Las imágenes del JSON se resuelven a archivos reales
# de HyperKvasir; ningún nombre del JSON se carga tal cual.
CASO_TAMIZAJE = Path(__file__).parent / "demo" / "caso_tamizaje.json"
CASO_VISION = Path(__file__).parent / "demo" / "caso_vision_polipos.json"
# Caso 3: completa los 10 escenarios clínicos de decisión del Acta de constitución (3 + 3 + 4 etapas; el caso de
# demostración tiene 2 etapas de práctica sin contenido clínico y no cuenta).
CASO_SENALES = Path(__file__).parent / "demo" / "caso_senales_alarma.json"
# Cada etapa clínica tiene su propia foto de HyperKvasir (demo/etapas/, origen en demo/etapas/manifiesto.json): los
# pólipos son de la partición de prueba del modelo de visión y ninguna foto se repite entre etapas.
IMAGENES_TAMIZAJE = {
    "polipo_etapa1.jpg": "etapas/tamizaje_e1_polipo.jpg",
    "bbps_etapa2.jpg": "etapas/tamizaje_e2_preparacion.jpg",
    "reseccion_etapa3.jpg": "etapas/tamizaje_e3_reseccion.jpg",
}
IMAGENES_VISION = {
    "polipo_vision_etapa1.jpg": "etapas/vision_e1_polipo.jpg",
    "preparacion_vision_etapa2.jpg": "etapas/vision_e2_preparacion.jpg",
    "reseccion_vision_etapa3.jpg": "etapas/vision_e3_reseccion.jpg",
}
IMAGENES_SENALES = {
    "polipo_senales_etapa1.jpg": "etapas/senales_e1_polipo.jpg",
    "reseccion_senales_etapa2.jpg": "etapas/senales_e2_reseccion.jpg",
    "polipo_senales_etapa3.jpg": "etapas/senales_e3_polipo.jpg",
    "preparacion_senales_etapa4.jpg": "etapas/senales_e4_preparacion.jpg",
}
# Primera versión del Caso 2 (PR #36 a #38): sus imágenes eran fichas de texto de OSF y no fotos, así que se retira.
TITULO_VISION_ANTERIOR = "Detección y Caracterización de Pólipos por Visión Computacional"


def _imagen_tamizaje(nombre: str, mapa: dict[str, str] | None = None) -> Path | None:
    destino = (mapa or IMAGENES_TAMIZAJE).get(nombre)
    if destino is None:
        return None
    if destino == "IMAGEN_DEMO":
        ruta = Path(os.getenv("IMAGEN_DEMO", "modelos/ejemplo-kvasir.jpg"))
    else:
        ruta = Path(__file__).parent / "demo" / destino
    return ruta if ruta.is_file() else None


def actualizar_descripcion_caso(db: Session, id_caso: int, descripcion: str) -> bool:
    """Pone al día la descripción de un caso ya publicado si cambió en su JSON. Devuelve True si la cambió."""
    cambiada = db.execute(text("""UPDATE caso SET descripcion = :d WHERE id_caso = :c AND descripcion IS DISTINCT FROM :d
                                  RETURNING id_caso"""), {"d": descripcion, "c": id_caso}).first()
    db.commit()
    return cambiada is not None


def actualizar_imagenes_caso(db: Session, id_caso: int, datos: dict, imagenes: dict[str, str]) -> int:
    """Si un caso ya publicado tiene en alguna etapa una foto distinta de la que fija su mapa, cambia el contenido del
    recurso por la foto nueva (mismo recurso, así se conservan los intentos). Devuelve cuántas fotos cambió."""
    cambiadas = 0
    for etapa in datos["etapas"]:
        imagen = _imagen_tamizaje(etapa["imagen_url"], imagenes)
        if imagen is None:
            continue
        contenido = imagen.read_bytes()
        huella = hashlib.sha256(contenido).hexdigest()
        recurso = db.execute(text("""SELECT r.id_recurso, c.sha256 FROM recurso_multimedia r
                                     JOIN etapa e ON e.id_etapa = r.id_etapa
                                     JOIN recurso_contenido c ON c.id_recurso = r.id_recurso
                                     WHERE e.id_caso = :c AND e.orden = :o AND r.tipo = 'imagen'
                                     ORDER BY r.id_recurso LIMIT 1"""), {"c": id_caso, "o": etapa["etapa"]}).first()
        if recurso is None or recurso.sha256 == huella:
            continue
        db.execute(text("""UPDATE recurso_contenido SET datos = :d, sha256 = :h, tamano_bytes = :t, tipo_mime = 'image/jpeg'
                           WHERE id_recurso = :i"""), {"d": contenido, "h": huella, "t": len(contenido), "i": recurso.id_recurso})
        cambiadas += 1
    db.commit()
    if cambiadas:
        print(f"Caso {datos['titulo']}: {cambiadas} fotos actualizadas.")
    return cambiadas


def _publicar_caso_json(db: Session, ruta: Path, imagenes: dict[str, str], fuente_revision: str) -> int | None:
    """Publica una sola vez un caso escrito en JSON (formato de caso_tamizaje.json) con sus imágenes de HyperKvasir.
    Si el caso ya existe, solo pone al día sus fotos."""
    if os.getenv("CASO_DEMO", "") != "1" or not ruta.is_file():
        return None
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    existente = db.execute(text("SELECT id_caso FROM caso WHERE titulo = :t AND NOT eliminado"), {"t": datos["titulo"]}).scalar()
    if existente is not None:
        actualizar_imagenes_caso(db, existente, datos, imagenes)
        actualizar_descripcion_caso(db, existente, datos["descripcion"])
        return None
    autor = _crear_usuario(db, "Profesional de la salud", "Autor de demostración",
                           f"demo-autor-{secrets.token_hex(3)}@ejemplo.com", secrets.token_urlsafe(24) + "a1")
    revisor = _crear_usuario(db, "Profesional de la salud", "Revisor de demostración",
                             f"demo-revisor-{secrets.token_hex(3)}@ejemplo.com", secrets.token_urlsafe(24) + "a1")
    db.commit()
    id_caso = casos.crear_caso(db, autor, CasoIn(
        titulo=datos["titulo"], tema=datos["tema"], nivel_dificultad=datos["nivel"],
        descripcion=datos["descripcion"], contexto_simulado=datos["paciente"]["nota"]))
    id_dataset = db.execute(text("SELECT id_dataset FROM dataset WHERE nombre = 'HyperKvasir'")).scalar()
    for etapa in datos["etapas"]:
        opciones = [OpcionIn(texto=o["texto"], puntaje=o["puntos"], es_correcta=o["correcta"],
                             recomendada_ia=o["sugerida_por_ia"], retroalimentacion=o["retroalimentacion"],
                             fuente=etapa["fuente"]) for o in etapa["opciones"]]
        imagen = _imagen_tamizaje(etapa["imagen_url"], imagenes)
        id_etapa = casos.guardar_etapa(db, autor, id_caso, EtapaIn(
            orden=etapa["etapa"], enunciado=etapa["enunciado"], recomendacion_ia=etapa["sugerencia_ia"]["texto"],
            usa_modelo_vision=bool(etapa["modelo_vision_activo"] and imagen), opciones=opciones))
        if imagen and id_dataset is not None:
            casos.guardar_recurso(db, autor, id_etapa, imagen.name, imagen.read_bytes(), id_dataset, LICENCIA_HYPERKVASIR)
    casos.revisar(db, revisor, id_caso, "aprobar", fuente_revision)
    casos.revisar(db, revisor, id_caso, "publicar", None)
    print(f"Caso publicado: {datos['titulo']} ({id_caso})")
    return id_caso


def publicar_caso_tamizaje(db: Session, ruta: Path | None = None) -> int | None:
    """Publica una sola vez el caso de tamizaje de 3 etapas con sus imágenes de HyperKvasir. Devuelve su id."""
    return _publicar_caso_json(db, ruta or CASO_TAMIZAJE, IMAGENES_TAMIZAJE,
                               "Aponte-Martín et al. (2025), guía colombiana de tamizaje")


def retirar_caso_vision_anterior(db: Session) -> bool:
    """Saca de la biblioteca la primera versión del Caso 2, cuyas imágenes no eran fotos."""
    retirado = db.execute(text("UPDATE caso SET eliminado = TRUE WHERE titulo = :t AND NOT eliminado RETURNING id_caso"),
                          {"t": TITULO_VISION_ANTERIOR}).first()
    db.commit()
    return retirado is not None


def publicar_caso_vision(db: Session, ruta: Path | None = None) -> int | None:
    """Caso 2: cómo leer el resultado del modelo de visión, con la IA equivocada a propósito en la etapa 2."""
    if os.getenv("CASO_DEMO", "") != "1":
        return None
    retirar_caso_vision_anterior(db)
    return _publicar_caso_json(db, ruta or CASO_VISION, IMAGENES_VISION,
                               "Aponte-Martín et al. (2025) y documentación del modelo de visión (RNF-007)")


def publicar_caso_senales(db: Session, ruta: Path | None = None) -> int | None:
    """Caso 3: señales de alarma, antecedentes familiares, prueba de sangre oculta positiva y preparación, con la IA
    equivocada a propósito en la etapa 2."""
    return _publicar_caso_json(db, ruta or CASO_SENALES, IMAGENES_SENALES,
                               "Aponte-Martín et al. (2025), guía colombiana de tamizaje")


def main() -> None:
    aplicar_esquema()
    with SessionLocal() as db:
        crear_admin_inicial(db)
        publicar_caso_demo(db)
        agregar_imagen_demo(db)
        agregar_imagenes_etapa_2(db)
        publicar_caso_tamizaje(db)
        publicar_caso_vision(db)
        publicar_caso_senales(db)


if __name__ == "__main__":
    main()
