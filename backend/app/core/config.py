"""Configuration centralisée, lue depuis les variables d'environnement (.env)."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    celery_broker_url: str
    celery_result_backend: str
    secret_key: str
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
