"""Unit tests for PDF parser."""
from __future__ import annotations

from pathlib import Path

import pytest

from services.parse.parsers.pdf import parse_pdf

FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "corpus"


class TestPdfParser:
    def test_parse_spanish_camry(self):
        path = FIXTURE_DIR / "toyota_camry_2012_es.pdf"
        if not path.exists():
            pytest.skip("Fixture PDF not found")
        data = path.read_bytes()
        result = parse_pdf(data, content_id="test-es")
        assert result.content_id == "test-es"
        assert result.page_count >= 1
        assert result.error is None
        # Should contain Spanish text
        full_text = " ".join(p.text for p in result.pages)
        assert "camry" in full_text.lower() or "toyota" in full_text.lower()

    def test_parse_english_camry(self):
        path = FIXTURE_DIR / "toyota_camry_2012_en.pdf"
        if not path.exists():
            pytest.skip("Fixture PDF not found")
        data = path.read_bytes()
        result = parse_pdf(data, content_id="test-en")
        assert result.page_count >= 1

    def test_parse_invalid_bytes(self):
        result = parse_pdf(b"not a pdf", content_id="bad")
        assert result.error is not None

    def test_page_numbers_start_at_1(self):
        path = FIXTURE_DIR / "toyota_camry_2012_en.pdf"
        if not path.exists():
            pytest.skip("Fixture PDF not found")
        data = path.read_bytes()
        result = parse_pdf(data, content_id="pn")
        assert result.pages[0].page_number == 1
