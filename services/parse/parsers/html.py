"""HTML parser: readability + BeautifulSoup."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HtmlParseResult:
    content_id: str
    title: str | None
    text: str
    error: str | None = None


def parse_html(data: bytes, content_id: str, encoding: str = "utf-8") -> HtmlParseResult:
    """Extract clean text from HTML bytes."""
    try:
        from readability import Document as ReadabilityDoc

        doc = ReadabilityDoc(data.decode(encoding, errors="replace"))
        summary_html = doc.summary()
        title = doc.title()
    except Exception:
        summary_html = data.decode(encoding, errors="replace")
        title = None

    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(summary_html, "html.parser")
        text = soup.get_text(separator="\n")
    except Exception as exc:
        return HtmlParseResult(content_id=content_id, title=title, text="", error=str(exc))

    return HtmlParseResult(content_id=content_id, title=title, text=text)
