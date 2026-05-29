from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Riot API"
    app_env: str = "development"
    riot_api_key: str = Field(default="", repr=False)
    default_platform_region: str = "na1"
    default_routing_region: str = "americas"
    cache_ttl_seconds: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
