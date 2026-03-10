"""Unit tests for the ingestion pipeline (no I/O)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from libs.common.schemas.ingestion import IngestRequest
from services.ingestion.fetchers.pipeline import IngestionPipeline, _logical_id, _sha256

FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "corpus"


class TestSha256:
    def test_known_hash(self):
        data = b"hello world"
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert _sha256(data) == expected


class TestLogicalId:
    def test_full_logical_id(self):
        req = IngestRequest(
            make="toyota",
            model="camry",
            year=2012,
            trim="le",
            language="es",
            region="us",
        )
        lid = _logical_id(req)
        assert lid == "toyota:camry:2012:le:es:us:1"

    def test_defaults(self):
        req = IngestRequest()
        lid = _logical_id(req)
        assert lid == "unknown:unknown:0:base:en:us:1"


class TestIngestionPipeline:
    def test_ingest_file(self):
        """Ingest a real fixture PDF without storage/db/events."""
        path = FIXTURE_DIR / "toyota_camry_2012_es.pdf"
        if not path.exists():
            pytest.skip("Fixture PDF not found")
        req = IngestRequest(
            file_path=str(path),
            make="toyota",
            model="camry",
            year=2012,
            trim="le",
            language="es",
            region="us",
        )
        pipeline = IngestionPipeline()
        result = pipeline.ingest(req)
        assert result.content_id  # sha256 non-empty
        assert result.logical_id == "toyota:camry:2012:le:es:us:1"
        assert len(result.content_id) == 64  # sha256 hex

    def test_ingest_idempotent(self):
        """Ingesting the same file twice produces the same content_id."""
        path = FIXTURE_DIR / "toyota_camry_2012_es.pdf"
        if not path.exists():
            pytest.skip("Fixture PDF not found")
        req = IngestRequest(
            file_path=str(path), make="toyota", model="camry", year=2012, language="es"
        )
        pipeline = IngestionPipeline()
        r1 = pipeline.ingest(req)
        r2 = pipeline.ingest(req)
        assert r1.content_id == r2.content_id

    def test_missing_source_raises(self):
        req = IngestRequest()
        pipeline = IngestionPipeline()
        with pytest.raises(ValueError):
            pipeline.ingest(req)
