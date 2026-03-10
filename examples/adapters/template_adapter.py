"""Template for a new OEM adapter.

Copy this file to services/ingestion/adapters/<oem_name>.py
and implement the abstract methods.
"""
from __future__ import annotations

from collections.abc import Iterator

from libs.common.schemas.ingestion import IngestRequest
from services.ingestion.adapters.base import AdapterBase


class TemplateOemAdapter(AdapterBase):
    adapter_id = "template_oem"
    base_url = "https://www.example-oem.com"
    crawl_delay = 3.0  # seconds between requests

    def fetch_seed(self) -> list[str]:
        """Return seed URLs for model/year enumeration."""
        return [self.base_url + "/owner-manuals"]

    def enumerate_models_years(self) -> Iterator[tuple[str, str, int]]:
        """Yield (make, model, year) tuples from the site."""
        # TODO: implement site-specific scraping
        # Example:
        # seed_data, _ = self.download(self.fetch_seed()[0])
        # parse seed_data and yield tuples
        yield ("example_make", "example_model", 2023)

    def list_manual_links(self, make: str, model: str, year: int) -> list[IngestRequest]:
        """Return IngestRequest objects for each manual found."""
        # TODO: implement site-specific link extraction
        return [
            IngestRequest(
                source_url=f"{self.base_url}/manuals/{model}/{year}/owner.pdf",
                make=make,
                model=model,
                year=year,
                language="en",
                region="us",
                adapter=self.adapter_id,
            )
        ]
