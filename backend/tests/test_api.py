"""PI-01 a PI-04: API (salud, autenticación y catálogo)."""
import uuid

from tests.conftest import requiere_db


def test_salud(cliente):
    r = cliente.get("/api/v1/salud")
    assert r.status_code == 200 and r.json()["estado"] == "ok"


def test_catalogo_exige_sesion(cliente):
    assert cliente.get("/api/v1/casos").status_code == 401


def test_registro_exige_aceptar_politica(cliente):
    r = cliente.post("/api/v1/auth/registro", json={
        "nombre": "Ana", "correo": "ana@ejemplo.com", "contrasena": "Segura123",
        "rango_edad": "40-49", "acepta_politica": False})
    assert r.status_code == 422


@requiere_db
def test_registro_login_y_perfil(cliente):
    correo = f"prueba_{uuid.uuid4().hex[:8]}@ejemplo.com"
    datos = {"nombre": "Persona de prueba", "correo": correo, "contrasena": "Segura123",
             "rango_edad": "40-49", "acepta_politica": True,
             "autoriza_datos_sensibles": True, "autoriza_compartir": False}
    assert cliente.post("/api/v1/auth/registro", json=datos).status_code == 201
    assert cliente.post("/api/v1/auth/registro", json=datos).status_code == 409
    token = cliente.post("/api/v1/auth/login", json={"correo": correo, "contrasena": "Segura123"}).json()["access_token"]
    yo = cliente.get("/api/v1/usuarios/me", headers={"Authorization": f"Bearer {token}"})
    assert yo.status_code == 200 and yo.json()["correo"] == correo
    assert cliente.get("/api/v1/casos", headers={"Authorization": f"Bearer {token}"}).status_code == 200


@requiere_db
def test_bloqueo_tras_cinco_intentos(cliente):
    correo = f"bloq_{uuid.uuid4().hex[:8]}@ejemplo.com"
    r = cliente.post("/api/v1/auth/registro", json={"nombre": "Persona bloqueo", "correo": correo,
                                                   "contrasena": "Segura123", "rango_edad": "18-29",
                                                   "acepta_politica": True})
    assert r.status_code == 201
    for _ in range(5):
        cliente.post("/api/v1/auth/login", json={"correo": correo, "contrasena": "mala12345"})
    r = cliente.post("/api/v1/auth/login", json={"correo": correo, "contrasena": "Segura123"})
    assert r.status_code == 423
