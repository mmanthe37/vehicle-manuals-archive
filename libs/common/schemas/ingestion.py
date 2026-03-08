"""Ingestion request/result schemas."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Request to ingest a document from a URL or file path."""

    source_url: str | None = None
    file_path: str | None = None
    make: str | None = None
    model: str | None = None
    year: int | None = None
    trim: str | None = None
    language: str | None = None
    region: str | None = None
    adapter: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResult(BaseModel):
    """Result of a completed ingest operation."""

    content_id: str
    logical_id: str
    source_url: str | None = None
    already_existed: bool = False
    parse_queued: bool = True
    message: str = "ok"
