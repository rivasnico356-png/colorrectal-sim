"""Prepara datos sintéticos para las pruebas de carga y estrés (solo en el entorno de pruebas).

Crea un administrador, dos profesionales y un caso publicado de dos etapas con texto de prueba.
No contiene contenido clínico ni datos de personas reales.
Uso: python -m pruebas_carga.sembrar http://localhost:8000/api/v1
"""
import sys
import uuid

import httpx
from sqlalchemy import text

from app.core.db import SessionLocal
from app.core.security import hash_contrasena

CLAVE = "Carga12345"


def main() -> None:
    api = sys.argv[1]
    admin = f"admin_{uuid.uuid4().hex[:6]}@carga.test"
    with SessionLocal() as db:
        db.execute(text("""INSERT INTO usuario (id_rol, nombre, correo, hash_contrasena, rango_edad)
                           VALUES ((SELECT id_rol FROM rol WHERE nombre = 'Administrador'), 'Admin carga', :c, :h, '30-39')"""),
                   {"c": admin, "h": hash_contrasena(CLAVE)})
        db.commit()
    c = httpx.Client(base_url=api, timeout=30)

    def token(correo):
        r = c.post("/auth/login", json={"correo": correo, "contrasena": CLAVE})
        r.raise_for_status()
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    cab_admin = token(admin)
    profes = []
    for i in range(2):
        correo = f"prof{i}_{uuid.uuid4().hex[:6]}@carga.test"
        c.post("/admin/usuarios", headers=cab_admin, json={"nombre": f"Profesional carga {i}", "correo": correo,
                                                           "contrasena": CLAVE, "rol": "Profesional de la salud"}).raise_for_status()
        profes.append(token(correo))
    autor, revisor = profes
    caso = c.post("/editor/casos", headers=autor, json={
        "titulo": "Caso sintético de carga", "tema": "pólipos", "nivel_dificultad": 1,
        "descripcion": "Caso sintético usado solo para pruebas de carga del software.",
        "contexto_simulado": "Persona simulada de prueba."}).json()["id_caso"]
    for orden in (1, 2):
        opciones = [{"texto": f"Opción {x}", "puntaje": p, "es_correcta": p == 100, "recomendada_ia": x == "A",
                     "retroalimentacion": "Explicación sintética de prueba.", "fuente": "Fuente sintética"}
                    for x, p in (("A", 100), ("B", 0))]
        c.put(f"/editor/casos/{caso}/etapas", headers=autor, json={
            "orden": orden, "enunciado": f"Enunciado sintético de la etapa {orden}.",
            "recomendacion_ia": "Sugerencia sintética de prueba.", "opciones": opciones}).raise_for_status()
    aprobar = {"accion": "aprobar", "fuente_clinica": "Fuente sintética"}
    c.post(f"/editor/casos/{caso}/revision", headers=revisor, json=aprobar).raise_for_status()
    c.post(f"/editor/casos/{caso}/revision", headers=revisor, json={"accion": "publicar"}).raise_for_status()
    print(f"Caso sintético publicado: {caso}")


if __name__ == "__main__":
    main()
