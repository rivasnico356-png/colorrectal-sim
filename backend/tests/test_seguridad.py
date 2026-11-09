"""PU-01 y PU-02: contraseñas y tokens (RNF-003)."""
import jwt
import pytest

from app.core.security import crear_token, hash_contrasena, leer_token, verificar_contrasena


def test_hash_no_guarda_texto_plano():
    h = hash_contrasena("Segura123")
    assert h != "Segura123"
    assert verificar_contrasena("Segura123", h)
    assert not verificar_contrasena("otra", h)


def test_token_lleva_sujeto_y_rol():
    datos = leer_token(crear_token("abc", "Usuario"))
    assert datos["sub"] == "abc" and datos["rol"] == "Usuario"


def test_token_alterado_se_rechaza():
    with pytest.raises(jwt.PyJWTError):
        leer_token(crear_token("abc", "Usuario") + "x")
