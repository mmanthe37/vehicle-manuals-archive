"""Make/model/year normalisation dictionaries and alias maps."""

from __future__ import annotations

# Canonical make name → list of aliases (all lowercase)
MAKE_ALIASES: dict[str, list[str]] = {
    "toyota": ["toyota motor", "toyota motor corp"],
    "honda": ["honda motor", "honda motor co"],
    "ford": ["ford motor", "ford motor company"],
    "chevrolet": ["chevy", "chevrolet motor"],
    "bmw": ["bayerische motoren werke", "bmw ag"],
    "mercedes-benz": ["mercedes", "benz", "daimler"],
    "volkswagen": ["vw", "volkswagen ag"],
    "nissan": ["nissan motor"],
    "hyundai": ["hyundai motor"],
    "kia": ["kia motors"],
}

# Reverse lookup: alias → canonical name
_ALIAS_REVERSE: dict[str, str] = {}
for canonical, aliases in MAKE_ALIASES.items():
    for alias in aliases:
        _ALIAS_REVERSE[alias] = canonical
    _ALIAS_REVERSE[canonical] = canonical


def normalize_make(raw: str) -> str:
    return _ALIAS_REVERSE.get(raw.strip().lower(), raw.strip().lower())


def normalize_model(raw: str) -> str:
    return raw.strip().lower().replace("-", " ").replace("_", " ")


def normalize_year(raw: int | str) -> int:
    return int(raw)


LANG_CODE_MAP: dict[str, str] = {
    "english": "en",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "japanese": "ja",
    "chinese": "zh",
    "korean": "ko",
    "portuguese": "pt",
    "italian": "it",
}


def normalize_language(raw: str) -> str:
    """Map common language names/codes to BCP-47 codes."""
    lower = raw.strip().lower()
    return LANG_CODE_MAP.get(lower, lower[:2])
