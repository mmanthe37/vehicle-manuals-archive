"""OpenSearch index manager: create indexes, upsert documents, search."""
from __future__ import annotations

from typing import Any

INDEX_MANUALS = "vmw_manuals"
INDEX_PAGES = "vmw_manual_pages"

MANUALS_MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                "default": {"type": "standard"},
                "english": {"type": "english"},
                "spanish": {"type": "spanish"},
            }
        }
    },
    "mappings": {
        "properties": {
            "content_id": {"type": "keyword"},
            "logical_id": {"type": "keyword"},
            "make": {"type": "keyword"},
            "model": {"type": "keyword"},
            "year": {"type": "integer"},
            "trim": {"type": "keyword"},
            "language": {"type": "keyword"},
            "region": {"type": "keyword"},
            "revision": {"type": "integer"},
            "title": {"type": "text", "analyzer": "default"},
            "source_url": {"type": "keyword"},
            "capture_at": {"type": "date"},
            "parse_status": {"type": "keyword"},
        }
    },
}

PAGES_MAPPING = {
    "mappings": {
        "properties": {
            "content_id": {"type": "keyword"},
            "page_number": {"type": "integer"},
            "text": {"type": "text", "analyzer": "default"},
            "language": {"type": "keyword"},
            "ocr_confidence": {"type": "float"},
        }
    }
}


class OpenSearchIndexer:
    def __init__(self, hosts: list[str] | None = None):
        from opensearchpy import OpenSearch

        self._client = OpenSearch(hosts=hosts or ["http://localhost:9200"])

    def ensure_indexes(self) -> None:
        for name, body in [
            (INDEX_MANUALS, MANUALS_MAPPING),
            (INDEX_PAGES, PAGES_MAPPING),
        ]:
            if not self._client.indices.exists(index=name):
                self._client.indices.create(index=name, body=body)

    def upsert_manual(self, doc: dict[str, Any]) -> None:
        self._client.index(
            index=INDEX_MANUALS,
            id=doc["content_id"],
            body=doc,
        )

    def upsert_page(self, page: dict[str, Any]) -> None:
        doc_id = f"{page['content_id']}_{page['page_number']}"
        self._client.index(index=INDEX_PAGES, id=doc_id, body=page)

    def search_text(
        self,
        query: str,
        make: str | None = None,
        model: str | None = None,
        year: int | None = None,
        language: str | None = None,
        size: int = 20,
    ) -> list[dict[str, Any]]:
        must: list[dict] = [{"multi_match": {"query": query, "fields": ["title", "text"]}}]
        filters: list[dict] = []
        if make:
            filters.append({"term": {"make": make}})
        if model:
            filters.append({"term": {"model": model}})
        if year:
            filters.append({"term": {"year": year}})
        if language:
            filters.append({"term": {"language": language}})
        body: dict = {
            "query": {"bool": {"must": must, "filter": filters}},
            "size": size,
        }
        resp = self._client.search(index=INDEX_MANUALS, body=body)
        return [hit["_source"] for hit in resp["hits"]["hits"]]

    def delete_manual(self, content_id: str) -> None:
        self._client.delete(index=INDEX_MANUALS, id=content_id, ignore=[404])
