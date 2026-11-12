"""Crea el primer administrador. Uso: docker compose exec backend python -m app.crear_admin <correo> "<nombre>"

La contraseña se pide por teclado y no queda en el historial de la terminal.
"""
import getpass
import sys

from sqlalchemy import text

from app.core.db import SessionLocal
from app.core.security import hash_contrasena
from app.modules.usuarios.schemas import validar_contrasena


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit('Uso: python -m app.crear_admin <correo> "<nombre>"')
    correo, nombre = sys.argv[1], sys.argv[2]
    clave = getpass.getpass("Contraseña (8 o más caracteres, con letras y números): ")
    if len(clave) < 8:
        sys.exit("La contraseña debe tener al menos 8 caracteres.")
    validar_contrasena(clave)
    with SessionLocal() as db:
        if db.execute(text("SELECT 1 FROM usuario WHERE lower(correo) = lower(:c)"), {"c": correo}).first():
            sys.exit("Ya existe una cuenta con ese correo.")
        db.execute(text("""INSERT INTO usuario (id_rol, nombre, correo, hash_contrasena, rango_edad)
                           VALUES ((SELECT id_rol FROM rol WHERE nombre = 'Administrador'), :n, lower(:c), :h, '30-39')"""),
                   {"n": nombre, "c": correo, "h": hash_contrasena(clave)})
        db.commit()
    print("Administrador creado.")


if __name__ == "__main__":
    main()
