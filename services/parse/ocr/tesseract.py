"""Tesseract OCR pipeline for image-heavy PDF pages."""
from __future__ import annotations

import io
from dataclasses import dataclass


@dataclass
class OcrPageResult:
    page_number: int
    text: str
    confidence: float
    language: str | None = None


def ocr_page_image(image_bytes: bytes, page_number: int, lang: str = "eng") -> OcrPageResult:
    """Run Tesseract OCR on an image and return text + confidence."""
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes))
        data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=pytesseract.Output.DICT,
        )
        words = [w for w in data["text"] if w.strip()]
        confs = [c for c in data["conf"] if c != -1]
        text = " ".join(words)
        confidence = sum(confs) / len(confs) if confs else 0.0
        return OcrPageResult(
            page_number=page_number,
            text=text,
            confidence=confidence / 100.0,
            language=lang,
        )
    except Exception:
        return OcrPageResult(
            page_number=page_number,
            text="",
            confidence=0.0,
            language=lang,
        )


def detect_language(text: str) -> str:
    """Detect BCP-47 language code from text snippet."""
    if not text.strip():
        return "en"
    try:
        from langdetect import detect

        return detect(text)
    except Exception:
        return "en"
