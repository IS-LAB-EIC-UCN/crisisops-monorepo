from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CrisisOps"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://crisisops:crisisops@localhost:5432/crisisops"
    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
