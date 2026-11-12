"""Prepara la base al arrancar el despliegue público (Render).

1. Carga el esquema (db/*.sql) si la base está vacía.
2. Crea el primer administrador con ADMIN_CORREO, ADMIN_NOMBRE y ADMIN_CONTRASENA si aún no existe.
3. Con CASO_DEMO=1 publica un caso de demostración con texto de prueba (sin contenido clínico) para recorrer el flujo
   mientras los profesionales de la salud escriben los casos reales.

Cada paso es idempotente: se puede ejecutar en cada arranque. Uso: python -m app.preparar
"""
import os
import secrets
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import SessionLocal, engine
from app.core.security import hash_contrasena
from app.modules.casos import service as casos
from app.modules.casos.schemas import CasoIn, EtapaIn, OpcionIn
from app.modules.usuarios.schemas import validar_contrasena

TITULO_DEMO = "Caso de demostración del simulador"


def aplicar_esquema() -> bool:
    """Ejecuta los scripts de db/ en orden solo si la tabla usuario no existe."""
    with engine.connect() as c:
        if c.execute(text("SELECT to_regclass('public.usuario')")).scalar():
            return False
    crudo = engine.raw_connection()
    try:
        crudo.driver_connection.autocommit = True
        with crudo.driver_connection.cursor() as cur:
            for archivo in sorted(Path(get_settings().esquema_dir).glob("*.sql")):
                cur.execute(archivo.read_text(encoding="utf-8"))
                print(f"Esquema: {archivo.name} aplicado.")
    finally:
        crudo.close()
    return True


def _crear_usuario(db: Session, rol: str, nombre: str, correo: str, contrasena: str) -> str:
    return str(db.execute(text("""INSERT INTO usuario (id_rol, nombre, correo, hash_contrasena, rango_edad)
                                  VALUES ((SELECT id_rol FROM rol WHERE nombre = :r), :n, lower(:c), :h, '30-39')
                                  RETURNING id_usuario"""),
                          {"r": rol, "n": nombre, "c": correo, "h": hash_contrasena(contrasena)}).scalar_one())


def crear_admin_inicial(db: Session) -> bool:
    correo, contrasena = os.getenv("ADMIN_CORREO", "").strip(), os.getenv("ADMIN_CONTRASENA", "")
    if not (correo and contrasena):
        return False
    if db.execute(text("SELECT 1 FROM usuario WHERE lower(correo) = lower(:c)"), {"c": correo}).first():
        return False
    validar_contrasena(contrasena)
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


def main() -> None:
    aplicar_esquema()
    with SessionLocal() as db:
        crear_admin_inicial(db)
        publicar_caso_demo(db)


if __name__ == "__main__":
    main()
