"""Document lineage endpoint."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LineageRecord(BaseModel):
    content_id: str
    logical_id: str
    revision: int
    previous_content_id: str | None = None
    source_url: str | None = None
    capture_at: str | None = None


@router.get("/{content_id}", response_model=list[LineageRecord])
async def get_lineage(content_id: str) -> list[LineageRecord]:
    """Return the version history lineage for a document."""
    return []
