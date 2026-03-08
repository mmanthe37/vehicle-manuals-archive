# Adapter Authoring Guide

## Overview

Each OEM source site gets a dedicated Python adapter class that implements the
`AdapterBase` interface. Adapters handle site-specific URL patterns, pagination,
metadata extraction, and normalization.

## 1. Create the Adapter File

```python
# services/ingestion/adapters/my_oem.py
from services.ingestion.adapters.base import AdapterBase
from libs.common.schemas.ingestion import IngestRequest
from typing import Iterator

class MyOemAdapter(AdapterBase):
    adapter_id = "my_oem"
    base_url = "https://www.my-oem.com"
    crawl_delay = 3.0  # seconds between requests

    def fetch_seed(self) -> list[str]:
        return [self.base_url + "/owners-manuals"]

    def enumerate_models_years(self) -> Iterator[tuple[str, str, int]]:
        # Scrape the model/year list from the site
        seed_url = self.fetch_seed()[0]
        data, _ = self.download(seed_url)
        # parse data and yield tuples
        yield ("my_oem", "model_name", 2023)

    def list_manual_links(self, make: str, model: str, year: int) -> list[IngestRequest]:
        url = f"{self.base_url}/manuals/{model}/{year}"
        data, _ = self.download(url)
        # parse links from data
        return [
            IngestRequest(
                source_url="https://www.my-oem.com/manuals/model_2023.pdf",
                make=make,
                model=model,
                year=year,
                language="en",
                region="us",
                adapter=self.adapter_id,
            )
        ]
```

## 2. Implement the Interface

| Method | Required | Description |
|--------|----------|-------------|
| `fetch_seed()` | ✅ | Return seed URLs for model/year enumeration |
| `enumerate_models_years()` | ✅ | Yield `(make, model, year)` tuples |
| `list_manual_links()` | ✅ | Return `IngestRequest` list for a model/year |
| `normalize_metadata()` | Optional | Custom make/model/trim normalization |
| `resolve_redirects()` | Optional | Override redirect logic |
| `download()` | Optional | Override HTTP download (e.g. for auth) |

## 3. robots.txt Compliance

The base class **automatically**:
- Reads and parses `/robots.txt` from `base_url`
- Checks `can_fetch(url)` before every download
- Respects `Crawl-delay` directive (uses your `crawl_delay` if higher)

**Never bypass** `can_fetch()`. If a URL is disallowed, skip it.

## 4. Register the Adapter

Add the adapter to `examples/seeds/adapters.yml`:

```yaml
adapters:
  - id: my_oem
    module: services.ingestion.adapters.my_oem
    class: MyOemAdapter
    enabled: true
    schedule: "0 3 * * *"
```

## 5. Test Your Adapter

```bash
vmw seed run --adapter my_oem --dry-run
```

Then run the unit tests:

```python
# tests/unit/ingestion/test_my_oem.py
from services.ingestion.adapters.my_oem import MyOemAdapter

def test_enumerate():
    adapter = MyOemAdapter()
    pairs = list(adapter.enumerate_models_years())
    assert len(pairs) > 0
```

## Normalization Tips

- Use `services.parse.enrichment.normalizer.normalize_make()` for make names
- Language codes must be BCP-47 (e.g. `en`, `es`, `fr-CA`)
- Region codes must be ISO 3166-1 alpha-2 (e.g. `us`, `ca`, `gb`)
- VIN decoding: use `vmw vin decode <vin>` or the NHTSA API
