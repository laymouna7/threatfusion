"""Configuration centralisée, lue depuis les variables d'environnement (.env)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    celery_broker_url: str
    celery_result_backend: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
