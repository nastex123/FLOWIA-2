"""Global application settings using Pydantic Settings."""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "FlowMind AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "insecure-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/flowmind"
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_BACKEND: str = "local"  # "local" | "s3"
    LOCAL_STORAGE_PATH: str = "./data/storage"

    # S3 / MinIO Configuration
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "flowmind-documents"
    S3_USE_SSL: bool = False

    # Document Processing Limits
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = Field(
        default_factory=lambda: ["xlsx", "xls", "csv", "pdf"]
    )


settings = Settings()
