"""Configuración leída de variables de entorno (ADR-08). Nunca se escriben secretos en el código."""
from functools import lru_cache

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
    ia_modelo_principal: str = "llama-3.3-70b-versatile"
    ia_modelo_alternativo: str = "llama-3.1-8b-instant"
    ia_timeout_segundos: float = 8.0
    ia_version_prompt: str = "tutor-v0.2"

    # RF-004 4.3: número máximo de consultas al tutor por etapa (configurable).
    tutor_max_consultas_etapa: int = 3
    # Carpeta local con las imágenes de los datasets públicos (no se sube al repositorio).
    media_dir: str = "media"
    cors_origenes: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
