"""Global application settings using Pydantic Settings."""

from typing import List, Optional
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

    # Database (Default: SQLite local asynchronous, or PostgreSQL)
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/flowmind.db"
    DATABASE_ECHO: bool = False

    # Redis (Optional in local mode, fallback to in-memory queue)
    REDIS_URL: Optional[str] = None

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
