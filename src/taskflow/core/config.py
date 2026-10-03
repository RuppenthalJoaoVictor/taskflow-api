"""Configurações da aplicação, carregadas de variáveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da TaskFlow API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "TaskFlow API"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = "sqlite:///./taskflow.db"

    secret_key: str = "troque-esta-chave-em-producao"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24


@lru_cache
def get_settings() -> Settings:
    """Retorna as configurações em cache para evitar releitura a cada request."""
    return Settings()
