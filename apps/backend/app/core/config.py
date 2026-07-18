"""Configuration centralisée, lue depuis les variables d'environnement (.env)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    celery_broker_url: str
    celery_result_backend: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    environment: str = "development"
    cors_origins: str = "http://localhost:3001"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
