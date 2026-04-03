"""Application settings for backend runtime."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = "AIEmbedd Backend"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api/v1"
    backend_secret: str = Field(default="change-me-in-production")
    database_url: str = Field(default="sqlite:///./data/aiembedd.db")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
