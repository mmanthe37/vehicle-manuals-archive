"""Base class for OEM site adapters.

Each OEM site gets its own adapter subclass that implements the discovery
and metadata-normalisation interface. The base class enforces robots.txt
compliance and rate-limiting.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import httpx

from libs.common.logging import get_logger
from libs.common.schemas.ingestion import IngestRequest

logger = get_logger(__name__)


class AdapterBase(ABC):
    """Abstract base for per-OEM site adapters."""

    #: Unique adapter identifier (e.g. "toyota_us")
    adapter_id: str = "base"
    #: Base URL of the OEM portal
    base_url: str = ""
    #: Crawl delay in seconds (overridden by robots.txt if higher)
    crawl_delay: float = 2.0

    def __init__(self) -> None:
        self._robots: RobotFileParser | None = None
        self._last_fetch: float = 0.0

    # ------------------------------------------------------------------
    # robots.txt compliance
    # ------------------------------------------------------------------

    def _load_robots(self) -> None:
        if self._robots is not None:
            return
        robots_url = urljoin(self.base_url, "/robots.txt")
        rp = RobotFileParser(robots_url)
        try:
            rp.read()
            self._robots = rp
            # Respect Crawl-delay directive if present
            delay = rp.crawl_delay("*")
            if delay and delay > self.crawl_delay:
                self.crawl_delay = delay
        except Exception as exc:
            logger.warning("robots_txt_unavailable", url=robots_url, exc=str(exc))
            self._robots = RobotFileParser()

    def can_fetch(self, url: str) -> bool:
        self._load_robots()
        if self._robots is None:
            return True
        return self._robots.can_fetch("*", url)

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_fetch
        if elapsed < self.crawl_delay:
            time.sleep(self.crawl_delay - elapsed)
        self._last_fetch = time.monotonic()

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def fetch_seed(self) -> list[str]:
        """Return a list of seed URLs for model/year enumeration."""

    @abstractmethod
    def enumerate_models_years(self) -> Iterator[tuple[str, str, int]]:
        """Yield (make, model, year) tuples."""

    @abstractmethod
    def list_manual_links(self, make: str, model: str, year: int) -> list[IngestRequest]:
        """Return IngestRequest objects for each manual found."""

    def normalize_metadata(self, req: IngestRequest) -> IngestRequest:
        """Apply make/model/year/trim normalisation (override if needed)."""
        if req.make:
            req.make = req.make.strip().lower()
        if req.model:
            req.model = req.model.strip().lower()
        return req

    def resolve_redirects(self, url: str) -> str:
        """Follow HTTP redirects and return final URL."""
        self._throttle()
        try:
            resp = httpx.head(url, follow_redirects=True, timeout=15)
            return str(resp.url)
        except Exception:
            return url

    def download(self, url: str) -> tuple[bytes, dict]:
        """Download URL; return (content_bytes, headers_dict)."""
        if not self.can_fetch(url):
            raise PermissionError(f"robots.txt disallows fetching: {url}")
        self._throttle()
        with httpx.Client(follow_redirects=True, timeout=60) as client:
            resp = client.get(url, headers={"User-Agent": "vmw-crawler/1.0 (+internal)"})
            resp.raise_for_status()
            return resp.content, dict(resp.headers)
