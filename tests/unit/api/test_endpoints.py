"""Unit tests for FastAPI endpoints."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from services.api.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestIngestUrlEndpoint:
    def test_ingest_url_returns_result(self, client):
        resp = client.post(
            "/ingest/url",
            json={
                "url": "https://example.com/manual.pdf",
                "make": "toyota",
                "model": "camry",
                "year": 2012,
                "language": "es",
                "region": "us",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "content_id" in body
        assert "logical_id" in body
        assert body["message"] == "queued"

    def test_ingest_url_logical_id_format(self, client):
        resp = client.post(
            "/ingest/url",
            json={
                "url": "https://example.com/manual.pdf",
                "make": "honda",
                "model": "civic",
                "year": 2015,
                "language": "en",
            },
        )
        body = resp.json()
        parts = body["logical_id"].split(":")
        assert len(parts) == 7


class TestManualsEndpoint:
    def test_list_manuals_empty(self, client):
        resp = client.get("/manuals")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_manuals_filters(self, client):
        resp = client.get("/manuals?make=toyota&model=camry&year=2012&language=es")
        assert resp.status_code == 200

    def test_download_not_found(self, client):
        resp = client.get("/manuals/nonexistent123/download")
        assert resp.status_code == 404


class TestSearchEndpoint:
    def test_text_search_empty(self, client):
        resp = client.post("/search/text", json={"query": "brake fluid"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_semantic_search_empty(self, client):
        resp = client.post("/search/semantic", json={"query": "oil change procedure"})
        assert resp.status_code == 200


class TestLineageEndpoint:
    def test_lineage_empty(self, client):
        resp = client.get("/lineage/abc123")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
