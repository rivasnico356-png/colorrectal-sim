import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app.core.security import hash_contrasena
from app.main import app

DB_URL = os.getenv("DATABASE_URL", "")


def _db_disponible() -> bool:
    if not DB_URL:
        return False
    try:
        with create_engine(DB_URL).connect() as c:
            c.execute(text("select 1 from caso_version limit 1"))
        return True
    except Exception:
        return False


requiere_db = pytest.mark.skipif(not _db_disponible(), reason="Sin base de datos de pruebas (DATABASE_URL)")


@pytest.fixture
def cliente() -> TestClient:
    return TestClient(app)


def correo(prefijo: str) -> str:
    return f"{prefijo}_{uuid.uuid4().hex[:8]}@ejemplo.com"


def token(cliente: TestClient, email: str, clave: str = "Segura123") -> dict:
    r = cliente.post("/api/v1/auth/login", json={"correo": email, "contrasena": clave})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def registrar_usuario(cliente: TestClient, compartir: bool = False) -> tuple[str, dict]:
    email = correo("usuario")
    r = cliente.post("/api/v1/auth/registro", json={"nombre": "Persona de prueba", "correo": email, "contrasena": "Segura123",
                                                    "rango_edad": "50-59", "acepta_politica": True,
                                                    "autoriza_compartir": compartir})
    assert r.status_code == 201, r.text
    return email, token(cliente, email)


@pytest.fixture
def admin(cliente) -> dict:
    """Crea un administrador directamente en la base (solo en pruebas)."""
    email = correo("admin")
    with create_engine(DB_URL).begin() as c:
        c.execute(text("""INSERT INTO usuario (id_rol, nombre, correo, hash_contrasena, rango_edad)
                          VALUES ((SELECT id_rol FROM rol WHERE nombre = 'Administrador'), 'Admin de prueba', :c, :h, '30-39')"""),
                  {"c": email, "h": hash_contrasena("Segura123")})
    return token(cliente, email)


def crear_profesional(cliente: TestClient, admin: dict) -> tuple[str, dict]:
    email = correo("profesional")
    r = cliente.post("/api/v1/admin/usuarios", headers=admin,
                     json={"nombre": "Profesional de prueba", "correo": email, "contrasena": "Segura123",
                           "rol": "Profesional de la salud"})
    assert r.status_code == 201, r.text
    return email, token(cliente, email)
