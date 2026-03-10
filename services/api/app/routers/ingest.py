"""Ingest endpoints: POST /ingest/url and POST /ingest/upload."""
from __future__ import annotations

import hashlib

from fastapi import APIRouter, BackgroundTasks, UploadFile
from pydantic import BaseModel

from libs.common.schemas.ingestion import IngestResult

router = APIRouter()


class UrlIngestPayload(BaseModel):
    url: str
    make: str | None = None
    model: str | None = None
    year: int | None = None
    trim: str | None = None
    language: str | None = "en"
    region: str | None = None
    adapter: str | None = None


@router.post("/url", response_model=IngestResult)
async def ingest_url(payload: UrlIngestPayload, background_tasks: BackgroundTasks) -> IngestResult:
    """Queue a URL for ingestion."""
    # In production, enqueue to Airflow/Temporal. Here we return a placeholder.
    content_id = hashlib.sha256(payload.url.encode()).hexdigest()
    logical_parts = [
        (payload.make or "unknown").lower(),
        (payload.model or "unknown").lower(),
        str(payload.year or 0),
        "base",
        (payload.language or "en").lower(),
        (payload.region or "us").lower(),
        "1",
    ]
    return IngestResult(
        content_id=content_id,
        logical_id=":".join(logical_parts),
        source_url=payload.url,
        already_existed=False,
        parse_queued=True,
        message="queued",
    )


@router.post("/upload", response_model=IngestResult)
async def ingest_upload(
    file: UploadFile,
    make: str | None = None,
    model: str | None = None,
    year: int | None = None,
    trim: str | None = None,
    language: str = "en",
    region: str | None = None,
) -> IngestResult:
    """Upload a file directly for ingestion."""
    data = await file.read()
    sha256 = hashlib.sha256(data).hexdigest()
    logical_parts = [
        (make or "unknown").lower(),
        (model or "unknown").lower(),
        str(year or 0),
        (trim or "base").lower(),
        language.lower(),
        (region or "us").lower(),
        "1",
    ]
    return IngestResult(
        content_id=sha256,
        logical_id=":".join(logical_parts),
        source_url=None,
        already_existed=False,
        parse_queued=True,
        message="uploaded",
    )
