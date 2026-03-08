"""CDC / event envelope schemas."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventType(enum.StrEnum):
    MANUAL_CREATED = "manual.created"
    MANUAL_VERSIONED = "manual.versioned"
    PARSE_COMPLETED = "parse.completed"
    OCR_COMPLETED = "ocr.completed"
    INDEX_UPDATED = "index.updated"
    INGEST_FAILED = "ingest.failed"


class EventEnvelope(BaseModel):
    """Envelope for all CDC events published to Kafka/SNS."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    content_id: str
    logical_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    emitted_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"use_enum_values": True}
