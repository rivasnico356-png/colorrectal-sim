"""Hash de contraseñas (bcrypt) y tokens JWT (RF-001, RNF-003)."""
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings


def hash_contrasena(contrasena: str) -> str:
    return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()


def verificar_contrasena(contrasena: str, hash_guardado: str) -> bool:
    try:
        return bcrypt.checkpw(contrasena.encode(), hash_guardado.encode())
    except ValueError:
        return False


def crear_token(sujeto: str, rol: str) -> str:
    s = get_settings()
    ahora = datetime.now(UTC)
    datos = {"sub": sujeto, "rol": rol, "iat": ahora, "exp": ahora + timedelta(minutes=s.jwt_minutos_expiracion)}
    return jwt.encode(datos, s.jwt_secreto, algorithm=s.jwt_algoritmo)


def leer_token(token: str) -> dict:
    s = get_settings()
    return jwt.decode(token, s.jwt_secreto, algorithms=[s.jwt_algoritmo])
