"""Core ingestion pipeline: fetch → deduplicate → store → emit CDC events."""

from __future__ import annotations

import hashlib
import json
import mimetypes
from datetime import datetime
from pathlib import Path

from libs.common.logging import get_logger
from libs.common.schemas.events import EventType
from libs.common.schemas.ingestion import IngestRequest, IngestResult

logger = get_logger(__name__)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _logical_id(req: IngestRequest) -> str:
    parts = [
        (req.make or "unknown").lower(),
        (req.model or "unknown").lower(),
        str(req.year or 0),
        (req.trim or "base").lower(),
        (req.language or "en").lower(),
        (req.region or "us").lower(),
        "1",
    ]
    return ":".join(parts)


class IngestionPipeline:
    """Orchestrates download → checksum → deduplicate → S3 store → DB upsert → event emit."""

    def __init__(self, storage=None, db_session=None, event_bus=None):
        self.storage = storage
        self.db = db_session
        self.event_bus = event_bus

    def ingest(self, req: IngestRequest, adapter=None) -> IngestResult:
        logger.info("ingest_start", source_url=req.source_url, file_path=req.file_path)

        # 1. Acquire bytes
        if req.file_path:
            data = Path(req.file_path).read_bytes()
            headers: dict = {}
        elif req.source_url and adapter:
            data, headers = adapter.download(req.source_url)
        else:
            raise ValueError("IngestRequest must have source_url or file_path")

        # 2. Checksum
        sha256 = _sha256(data)
        size_bytes = len(data)

        # 3. MIME sniffing
        mime_type = "application/octet-stream"
        if req.file_path:
            guessed, _ = mimetypes.guess_type(req.file_path)
            if guessed:
                mime_type = guessed
        elif "content-type" in headers:
            mime_type = headers["content-type"].split(";")[0].strip()

        logical_id = _logical_id(req)

        # 4. Dedup gate: check if content already stored
        already_existed = False
        if self.storage:
            try:
                self.storage.get_blob(sha256)
                already_existed = True
                logger.info("ingest_dedup_hit", content_id=sha256)
            except Exception:
                pass

        if not already_existed:
            # 5. Store blob in S3/MinIO
            if self.storage:
                self.storage.put_blob(data, sha256)
                # Store logical ref pointer
                ref_key = self.storage.ref_key(
                    req.make or "unknown",
                    req.model or "unknown",
                    req.year or 0,
                    req.language or "en",
                    1,
                )
                ref_payload = json.dumps(
                    {
                        "content_id": sha256,
                        "logical_id": logical_id,
                        "captured_at": datetime.utcnow().isoformat(),
                    }
                ).encode()
                self.storage.put_ref(ref_key, ref_payload)

        # 6. DB upsert (if session available)
        if self.db:
            self._upsert_document(req, sha256, logical_id, size_bytes, mime_type)

        # 7. Emit CDC event
        if self.event_bus:
            import asyncio

            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                self.event_bus.emit(
                    EventType.MANUAL_CREATED if not already_existed else EventType.MANUAL_VERSIONED,
                    content_id=sha256,
                    logical_id=logical_id,
                )
            )

        logger.info("ingest_complete", content_id=sha256, logical_id=logical_id)
        return IngestResult(
            content_id=sha256,
            logical_id=logical_id,
            source_url=req.source_url,
            already_existed=already_existed,
            parse_queued=True,
        )

    def _upsert_document(
        self, req: IngestRequest, sha256: str, logical_id: str, size_bytes: int, mime_type: str
    ) -> None:
        from sqlalchemy import select

        from libs.common.db import Document

        existing = self.db.execute(
            select(Document).where(Document.content_id == sha256)
        ).scalar_one_or_none()

        if existing is None:
            doc = Document(
                content_id=sha256,
                logical_id=logical_id,
                source_url=req.source_url,
                capture_at=datetime.utcnow(),
                make=req.make,
                model=req.model,
                year=req.year,
                trim=req.trim,
                language=req.language,
                region=req.region,
                sha256=sha256,
                size_bytes=size_bytes,
                mime_type=mime_type,
                parse_status="pending",
                ocr_status="pending",
                metadata_=req.metadata,
            )
            self.db.add(doc)
            self.db.commit()
