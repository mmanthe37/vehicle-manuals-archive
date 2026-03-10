"""Core data schemas for OEM vehicle manuals."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ParseStatus(enum.StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OcrStatus(enum.StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ManualSchema(BaseModel):
    """Logical manual record (make/model/year/lang/region)."""

    logical_id: str = Field(
        ...,
        description="make:model:year:trim:lang:region:revision",
        examples=["toyota:camry:2012:le:es:us:1"],
    )
    content_id: str = Field(..., description="SHA-256 of canonical blob")
    make: str
    model: str
    year: int
    trim: str | None = None
    language: str = Field(..., description="BCP-47 language code, e.g. en, es, fr")
    region: str | None = Field(None, description="ISO 3166-1 alpha-2 market code")
    revision: int = Field(1, ge=1)
    title: str | None = None
    source_url: str | None = None
    mime_type: str = "application/pdf"
    size_bytes: int | None = None
    sha256: str
    capture_at: datetime
    parse_status: ParseStatus = ParseStatus.PENDING
    ocr_status: OcrStatus = OcrStatus.PENDING
    page_count: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"use_enum_values": True}


class ManualVersionSchema(BaseModel):
    """Immutable version record for a manual."""

    content_id: str
    logical_id: str
    revision: int
    previous_content_id: str | None = None
    added_pages: int = 0
    removed_pages: int = 0
    text_similarity: float | None = None
    created_at: datetime


class DocumentPageSchema(BaseModel):
    """Per-page parsed text and embedding."""

    content_id: str
    page_number: int
    text: str
    language: str | None = None
    ocr_confidence: float | None = None
    embedding: list[float] | None = None
