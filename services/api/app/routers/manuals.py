"""Manuals listing, retrieval, and download endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class ManualSummary(BaseModel):
    content_id: str
    logical_id: str
    make: str
    model: str
    year: int
    trim: str | None = None
    language: str
    region: str | None = None
    revision: int
    title: str | None = None
    page_count: int | None = None
    parse_status: str


class DownloadResponse(BaseModel):
    content_id: str
    presigned_url: str
    expires_in: int = 3600


@router.get("", response_model=list[ManualSummary])
async def list_manuals(
    make: str | None = Query(None),
    model: str | None = Query(None),
    year: int | None = Query(None),
    trim: str | None = Query(None),
    language: str | None = Query(None),
    region: str | None = Query(None),
    revision: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[ManualSummary]:
    """List manuals with optional filters."""
    # In production, queries Postgres. Returns empty list when no DB.
    return []


@router.get("/{content_id}/download", response_model=DownloadResponse)
async def download_manual(content_id: str) -> DownloadResponse:
    """Return a presigned S3 URL for the manual blob."""
    # In production, calls StorageClient.presigned_url()
    raise HTTPException(status_code=404, detail="Manual not found")


@router.get("/{content_id}/pages")
async def get_pages(content_id: str) -> list[dict]:
    """Return parsed pages for a manual."""
    return []
