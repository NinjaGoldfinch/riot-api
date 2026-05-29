from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.regions import ROUTING_REGIONS


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Riot API"
    app_env: Literal["development", "test", "production"] = "development"
    riot_api_key: str = Field(default="", repr=False)
    cors_allowed_origins: str = ""
    default_routing_region: str = "asia"
    database_url: str = Field(default="", repr=False)
    database_auto_migrate: bool = True
    database_echo: bool = False
    cache_ttl_seconds: int = Field(default=300, ge=0)
    account_cache_ttl_seconds: int = Field(default=300, ge=0)
    summoner_cache_ttl_seconds: int = Field(default=300, ge=0)
    ranked_cache_ttl_seconds: int = Field(default=120, ge=0)
    match_history_cache_ttl_seconds: int = Field(default=60, ge=0)
    match_detail_cache_ttl_seconds: int = Field(default=86_400, ge=0)
    rate_limit_enabled: bool = True
    rate_limit_requests: int = Field(default=60, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    rate_limit_service_requests: int = Field(default=30, ge=1)
    rate_limit_service_window_seconds: int = Field(default=60, ge=1)
    rate_limit_method_requests: int = Field(default=20, ge=1)
    rate_limit_method_window_seconds: int = Field(default=60, ge=1)

    @field_validator("default_routing_region")
    @classmethod
    def validate_default_routing_region(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in ROUTING_REGIONS:
            raise ValueError(
                f"Invalid default routing region '{value}'. "
                f"Expected one of: {sorted(ROUTING_REGIONS)}."
            )
        if normalized == "sea":
            return "asia"
        return normalized

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
