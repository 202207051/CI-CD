"""my-python-app package."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__version__ = "0.1.0"
__all__ = ["Settings", "get_settings", "__version__"]


class Settings(BaseSettings):
    """애플리케이션 및 Valkey 환경 설정."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="my-python-app", alias="APP_NAME")
    app_env: str = Field(default="production", alias="APP_ENV")
    app_port: int = Field(default=8000, alias="APP_PORT")
    secret_key: str = Field(
        default="change-this-to-a-random-secret-key-2026",
        alias="SECRET_KEY",
    )

    valkey_host: str = Field(default="valkey", alias="VALKEY_HOST")
    valkey_port: int = Field(default=6379, alias="VALKEY_PORT")
    valkey_db: int = Field(default=0, alias="VALKEY_DB")
    valkey_password: str | None = Field(default=None, alias="VALKEY_PASSWORD")


_settings: Settings | None = None


def get_settings() -> Settings:
    """설정 싱글톤 반환."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
