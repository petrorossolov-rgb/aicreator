"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with AICREATOR_ prefix for env vars."""

    model_config = SettingsConfigDict(env_prefix="AICREATOR_")

    database_url: str = "sqlite:///./aicreator.db"
    log_level: str = "INFO"
    log_format: str = "text"  # "text" or "json"
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
