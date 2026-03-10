"""End-to-end smoke test: mock OEM adapter → ingest → parse → searchable.

This test exercises the full pipeline using local fixtures only (no live services).
Marked as 'smoke' so it can be skipped in pure unit-test runs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "corpus"


@pytest.mark.smoke
class TestMockOemPipelineE2E:
    """Full pipeline: discover → fetch → store → parse → assert content ID."""

    def test_spanish_camry_manual_discoverable(self):
        """The Spanish 2012 Toyota Camry fixture must exist in the corpus."""
        path = FIXTURE_DIR / "toyota_camry_2012_es.pdf"
        assert path.exists(), f"Fixture missing: {path}"
        assert path.stat().st_size > 0

    def test_all_fixture_files_present(self):
        expected = [
            "toyota_camry_2012_es.pdf",
            "toyota_camry_2012_en.pdf",
            "honda_civic_2015_en.pdf",
        ]
        for fname in expected:
            p = FIXTURE_DIR / fname
            assert p.exists(), f"Missing fixture: {fname}"

    def test_mock_adapter_discovers_spanish_camry(self):
        from services.ingestion.adapters.mock_oem import MockOemAdapter

        adapter = MockOemAdapter()
        requests = adapter.list_manual_links("toyota", "camry", 2012)
        spanish = [r for r in requests if r.language == "es"]
        assert len(spanish) == 1
        assert spanish[0].make == "toyota"
        assert spanish[0].model == "camry"
        assert spanish[0].year == 2012

    def test_ingest_spanish_camry_produces_content_id(self):
        from services.ingestion.adapters.mock_oem import MockOemAdapter
        from services.ingestion.fetchers.pipeline import IngestionPipeline

        adapter = MockOemAdapter()
        requests = adapter.list_manual_links("toyota", "camry", 2012)
        spanish_req = next(r for r in requests if r.language == "es")

        pipeline = IngestionPipeline()
        result = pipeline.ingest(spanish_req)

        assert len(result.content_id) == 64  # sha256 hex
        assert result.logical_id == "toyota:camry:2012:le:es:us:1"
        assert result.parse_queued

    def test_ingest_all_fixtures_produces_unique_content_ids(self):
        from services.ingestion.adapters.mock_oem import MockOemAdapter
        from services.ingestion.fetchers.pipeline import IngestionPipeline

        adapter = MockOemAdapter()
        pipeline = IngestionPipeline()
        content_ids = set()

        for make, model, year in adapter.enumerate_models_years():
            for req in adapter.list_manual_links(make, model, year):
                result = pipeline.ingest(req)
                content_ids.add(result.content_id)

        # 3 fixture files → 3 unique content IDs
        assert len(content_ids) == 3

    def test_parse_spanish_camry_pdf(self):
        from services.parse.parsers.pdf import parse_pdf

        path = FIXTURE_DIR / "toyota_camry_2012_es.pdf"
        data = path.read_bytes()
        result = parse_pdf(data, content_id="smoke-es")
        assert result.page_count >= 1
        assert result.error is None
        full_text = " ".join(p.text for p in result.pages).lower()
        # Fixture PDF contains "camry" in its text
        assert "camry" in full_text or "toyota" in full_text

    def test_immutable_content_id_on_reingest(self):
        """Re-ingesting the same file must return the same content_id (idempotent)."""
        from services.ingestion.adapters.mock_oem import MockOemAdapter
        from services.ingestion.fetchers.pipeline import IngestionPipeline

        adapter = MockOemAdapter()
        requests = adapter.list_manual_links("toyota", "camry", 2012)
        req = next(r for r in requests if r.language == "es")
        pipeline = IngestionPipeline()

        r1 = pipeline.ingest(req)
        r2 = pipeline.ingest(req)
        assert r1.content_id == r2.content_id
