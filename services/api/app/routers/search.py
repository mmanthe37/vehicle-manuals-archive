"""Text and semantic search endpoints."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TextSearchRequest(BaseModel):
    query: str
    make: str | None = None
    model: str | None = None
    year: int | None = None
    language: str | None = None
    size: int = 20


class SearchResult(BaseModel):
    content_id: str
    logical_id: str
    title: str | None = None
    make: str
    model: str
    year: int
    language: str
    score: float


@router.post("/text", response_model=list[SearchResult])
async def text_search(req: TextSearchRequest) -> list[SearchResult]:
    """BM25 full-text search via OpenSearch."""
    return []


@router.post("/semantic", response_model=list[SearchResult])
async def semantic_search(req: TextSearchRequest) -> list[SearchResult]:
    """Hybrid BM25 + vector semantic search."""
    return []
