"""PDF parser: PyMuPDF primary, pdfminer.six fallback."""
from __future__ import annotations

import io
from dataclasses import dataclass, field


@dataclass
class PageResult:
    page_number: int
    text: str
    has_images: bool = False
    needs_ocr: bool = False


@dataclass
class ParseResult:
    content_id: str
    page_count: int
    pages: list[PageResult] = field(default_factory=list)
    error: str | None = None


def parse_pdf(data: bytes, content_id: str) -> ParseResult:
    """Extract text from PDF bytes. Tries PyMuPDF first, falls back to pdfminer."""
    try:
        return _parse_with_pymupdf(data, content_id)
    except Exception as primary_exc:
        try:
            return _parse_with_pdfminer(data, content_id)
        except Exception as fallback_exc:
            return ParseResult(
                content_id=content_id,
                page_count=0,
                error=f"pymupdf: {primary_exc}; pdfminer: {fallback_exc}",
            )


def _parse_with_pymupdf(data: bytes, content_id: str) -> ParseResult:
    import fitz  # PyMuPDF

    doc = fitz.open(stream=data, filetype="pdf")
    pages: list[PageResult] = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        images = page.get_images()
        needs_ocr = len(text.strip()) < 50 and len(images) > 0
        pages.append(
            PageResult(
                page_number=page_num + 1,
                text=text,
                has_images=len(images) > 0,
                needs_ocr=needs_ocr,
            )
        )
    doc.close()
    return ParseResult(content_id=content_id, page_count=len(pages), pages=pages)


def _parse_with_pdfminer(data: bytes, content_id: str) -> ParseResult:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer

    pages: list[PageResult] = []
    for page_num, layout in enumerate(extract_pages(io.BytesIO(data))):
        texts: list[str] = []
        for element in layout:
            if isinstance(element, LTTextContainer):
                texts.append(element.get_text())
        text = "".join(texts)
        pages.append(PageResult(page_number=page_num + 1, text=text))
    return ParseResult(content_id=content_id, page_count=len(pages), pages=pages)
