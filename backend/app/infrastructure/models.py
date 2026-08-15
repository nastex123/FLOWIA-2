"""SQLAlchemy ORM models with strict multi-tenant organization boundaries."""

import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now
    )

    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="organization", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(50), default="member")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.PENDING, index=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now
    )

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="documents"
    )
    extraction_record: Mapped[Optional["ExtractionRecord"]] = relationship(
        "ExtractionRecord", back_populates="document", uselist=False, cascade="all, delete-orphan"
    )


class ExtractionRecord(Base):
    __tablename__ = "extraction_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id"), nullable=False, unique=True, index=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(50), default="unknown")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    fields_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    tables_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    raw_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now
    )

    document: Mapped["Document"] = relationship(
        "Document", back_populates="extraction_record"
    )


class SchemaDefinition(Base):
    __tablename__ = "schema_definitions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_type: Mapped[str] = mapped_column(String(50), default="custom")
    fields_config_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now
    )
