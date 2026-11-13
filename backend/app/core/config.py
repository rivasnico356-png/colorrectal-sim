"""Configuración leída de variables de entorno (ADR-08). Nunca se escriben secretos en el código."""
import os
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_nombre: str = "Colorrectal-Sim API"
    entorno: str = "desarrollo"
    database_url: str = "postgresql+psycopg://colorrectal:colorrectal@localhost:5432/colorrectal_sim"

    jwt_secreto: str = "cambiar-en-.env"
    sal_seudonimo: str = ""  # se aplica con SET app.sal_seudonimo al exportar (RNF-007)
    jwt_algoritmo: str = "HS256"
    jwt_minutos_expiracion: int = 60

    # RF-001 1.2: bloqueo temporal tras intentos fallidos
    max_intentos_fallidos: int = 5
    minutos_bloqueo: int = 15

    # Agente tutor (RF-004). Proveedor principal y alternativo con API compatible con OpenAI.
    ia_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    ia_api_key: str = ""
    ia_modelo_principal: str = "openai/gpt-oss-120b"
    ia_modelo_alternativo: str = "openai/gpt-oss-20b"
    ia_timeout_segundos: float = 8.0
    ia_version_prompt: str = "tutor-v0.3"

    # RF-004 4.3: número máximo de consultas al tutor por etapa (configurable).
    tutor_max_consultas_etapa: int = 3
    # Carpeta local con las imágenes de los datasets públicos (no se sube al repositorio).
    media_dir: str = "media"
    # RNF-003: clave para cifrar en reposo los estudios propios (Fernet). Si está vacía se deriva de jwt_secreto
    # solo en desarrollo; en producción debe definirse.
    clave_cifrado_estudios: str = ""
    estudios_dir: str = "estudios"
    # IE-04: modelo de visión exportado a ONNX (lo entrena el equipo con vision/entrenar.py).
    modelo_vision_ruta: str = "modelos/vision.onnx"
    # IE-05: correo SMTP para la recuperación de contraseña. Sin servidor configurado no se envía (desarrollo).
    # Correo por API HTTPS (Brevo). El remitente (SMTP_REMITENTE) debe estar verificado en Brevo.
    brevo_api_key: str = ""
    smtp_servidor: str = ""
    smtp_puerto: int = 587
    smtp_usuario: str = ""
    smtp_contrasena: str = ""
    smtp_remitente: str = "no-responder@colorrectal-sim.local"
    # En Render se usa la dirección pública del servicio para los enlaces de recuperación.
    frontend_url: str = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:5173")
    minutos_enlace_recuperacion: int = 30
    cors_origenes: str = "http://localhost:5173"
    # Despliegue público: scripts del esquema y frontend compilado que sirve la misma API (un solo enlace).
    esquema_dir: str = "../db"
    web_dir: str = "web"

    @field_validator("database_url")
    @classmethod
    def usar_psycopg(cls, v: str) -> str:
        """Los proveedores entregan postgres:// o postgresql://; SQLAlchemy necesita el controlador psycopg 3."""
        for prefijo in ("postgres://", "postgresql://"):
            if v.startswith(prefijo):
                return "postgresql+psycopg://" + v[len(prefijo):]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
