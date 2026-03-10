"""Mock OEM adapter for local development and end-to-end smoke tests.

Simulates a fictional OEM site and returns fixture manuals including
a Spanish-language 2012 Toyota Camry manual from the local test corpus.
"""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from libs.common.schemas.ingestion import IngestRequest
from services.ingestion.adapters.base import AdapterBase

# Fixture corpus lives in tests/fixtures/corpus/
FIXTURE_DIR = Path(__file__).parents[3] / "tests" / "fixtures" / "corpus"


class MockOemAdapter(AdapterBase):
    adapter_id = "mock_oem"
    base_url = "http://mock-oem.local"
    crawl_delay = 0.0  # no throttle for local tests

    def can_fetch(self, url: str) -> bool:
        return True  # mock – no real robots.txt

    def fetch_seed(self) -> list[str]:
        return [self.base_url + "/manuals"]

    def enumerate_models_years(self) -> Iterator[tuple[str, str, int]]:
        yield ("toyota", "camry", 2012)
        yield ("honda", "civic", 2015)

    def list_manual_links(
        self, make: str, model: str, year: int
    ) -> list[IngestRequest]:
        results: list[IngestRequest] = []
        if (make, model, year) == ("toyota", "camry", 2012):
            results.append(
                IngestRequest(
                    file_path=str(FIXTURE_DIR / "toyota_camry_2012_es.pdf"),
                    make="toyota",
                    model="camry",
                    year=2012,
                    trim="le",
                    language="es",
                    region="us",
                    adapter=self.adapter_id,
                    metadata={"title": "Manual del propietario Toyota Camry 2012"},
                )
            )
            results.append(
                IngestRequest(
                    file_path=str(FIXTURE_DIR / "toyota_camry_2012_en.pdf"),
                    make="toyota",
                    model="camry",
                    year=2012,
                    trim="le",
                    language="en",
                    region="us",
                    adapter=self.adapter_id,
                    metadata={"title": "Toyota Camry 2012 Owner's Manual"},
                )
            )
        elif (make, model, year) == ("honda", "civic", 2015):
            results.append(
                IngestRequest(
                    file_path=str(FIXTURE_DIR / "honda_civic_2015_en.pdf"),
                    make="honda",
                    model="civic",
                    year=2015,
                    trim="lx",
                    language="en",
                    region="us",
                    adapter=self.adapter_id,
                    metadata={"title": "Honda Civic 2015 Owner's Manual"},
                )
            )
        return results

    def download(self, url: str) -> tuple[bytes, dict]:
        raise NotImplementedError("Mock adapter uses file_path; no HTTP download needed.")
