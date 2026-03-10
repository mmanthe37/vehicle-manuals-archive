"""Unit tests for Pydantic schemas."""
from __future__ import annotations

from datetime import datetime

from libs.common.schemas.events import EventEnvelope, EventType
from libs.common.schemas.ingestion import IngestRequest, IngestResult
from libs.common.schemas.manual import ManualSchema


class TestManualSchema:
    def test_valid_manual(self):
        m = ManualSchema(
            logical_id="toyota:camry:2012:le:es:us:1",
            content_id="abc123",
            make="toyota",
            model="camry",
            year=2012,
            language="es",
            sha256="abc123",
            capture_at=datetime.utcnow(),
        )
        assert m.make == "toyota"
        assert m.year == 2012
        assert m.language == "es"
        assert m.parse_status == "pending"
        assert m.ocr_status == "pending"

    def test_logical_id_format(self):
        m = ManualSchema(
            logical_id="toyota:camry:2012:le:es:us:1",
            content_id="deadbeef",
            make="toyota",
            model="camry",
            year=2012,
            language="es",
            region="us",
            sha256="deadbeef",
            capture_at=datetime.utcnow(),
        )
        parts = m.logical_id.split(":")
        assert len(parts) == 7
        assert parts[0] == "toyota"
        assert parts[2] == "2012"
        assert parts[4] == "es"

    def test_revision_default(self):
        m = ManualSchema(
            logical_id="x",
            content_id="y",
            make="ford",
            model="f150",
            year=2020,
            language="en",
            sha256="y",
            capture_at=datetime.utcnow(),
        )
        assert m.revision == 1


class TestIngestRequest:
    def test_url_request(self):
        req = IngestRequest(
            source_url="https://example.com/manual.pdf",
            make="toyota",
            model="camry",
            year=2012,
            language="es",
        )
        assert req.source_url == "https://example.com/manual.pdf"
        assert req.language == "es"

    def test_file_request(self):
        req = IngestRequest(file_path="/tmp/manual.pdf", make="honda", model="civic", year=2015)
        assert req.file_path == "/tmp/manual.pdf"


class TestIngestResult:
    def test_result_fields(self):
        r = IngestResult(
            content_id="sha256abc",
            logical_id="toyota:camry:2012:le:es:us:1",
        )
        assert r.content_id == "sha256abc"
        assert r.parse_queued is True
        assert r.already_existed is False


class TestEventEnvelope:
    def test_event_creation(self):
        e = EventEnvelope(
            event_type=EventType.MANUAL_CREATED,
            content_id="abc",
        )
        assert e.event_type == EventType.MANUAL_CREATED.value
        assert e.content_id == "abc"
        assert e.event_id  # auto-generated UUID

    def test_all_event_types(self):
        for et in EventType:
            e = EventEnvelope(event_type=et, content_id="x")
            assert e.event_type == et.value
