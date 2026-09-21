from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://siscoord_app:siscoord_app_troque_esta_senha@localhost:5432/siscoord"
    database_url_migracao: str = "postgresql+psycopg://siscoord:siscoord@localhost:5432/siscoord"
    jwt_secret: str = "changeme-in-.env-with-a-long-random-value"
    jwt_algorithm: str = "HS256"
    jwt_expira_minutos: int = 480

    srid_armazenamento: int = 4674  # SIRGAS 2000 (RNF-02)

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8080"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
