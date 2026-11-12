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
