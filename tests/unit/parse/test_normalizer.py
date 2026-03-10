"""Unit tests for normalizer (make/model/year/lang)."""

from __future__ import annotations

from services.parse.enrichment.normalizer import (
    normalize_language,
    normalize_make,
    normalize_model,
    normalize_year,
)


class TestNormalizeMake:
    def test_lowercase(self):
        assert normalize_make("Toyota") == "toyota"

    def test_alias_chevy(self):
        assert normalize_make("chevy") == "chevrolet"

    def test_alias_vw(self):
        assert normalize_make("VW") == "volkswagen"

    def test_unknown_make(self):
        assert normalize_make("Acura") == "acura"

    def test_toyota_variant(self):
        assert normalize_make("toyota motor corp") == "toyota"


class TestNormalizeModel:
    def test_lowercase(self):
        assert normalize_model("Camry") == "camry"

    def test_hyphens_to_spaces(self):
        assert normalize_model("F-150") == "f 150"

    def test_underscores_to_spaces(self):
        assert normalize_model("Accord_Sport") == "accord sport"


class TestNormalizeYear:
    def test_int(self):
        assert normalize_year(2012) == 2012

    def test_string(self):
        assert normalize_year("2015") == 2015


class TestNormalizeLanguage:
    def test_en(self):
        assert normalize_language("en") == "en"

    def test_english(self):
        assert normalize_language("English") == "en"

    def test_spanish(self):
        assert normalize_language("Spanish") == "es"

    def test_unknown(self):
        assert normalize_language("zz") == "zz"
