# Vehicle Manuals Archive — Architecture Overview

## Summary

A private, ingestion-first, content-addressable warehouse for OEM vehicle owner's manuals.
Designed to autonomously discover, fetch, deduplicate, parse/OCR, index, and store manuals
at global scale (target: 5–10 million files, 20–50 TB year 1).

---

## System Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         INGESTION PLANE                              │
│  Playwright fetchers  ←→  Per-site adapters  ←→  Scheduler (Airflow) │
│  robots.txt compliance · rate-limit · ETag/Last-Modified caching     │
└─────────────────────────────┬────────────────────────────────────────┘
                              │ blobs (bytes)
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                                   │
│  S3 (content-addressable):  blobs/sha256/xx/<hash>                   │
│  refs/make/model/year/lang/revision.json → content_id                │
│  Postgres (RDS + pgvector): documents, pages, events, metadata       │
└──────────────┬──────────────┬───────────────────────────────────────┘
               │ parse jobs   │ index jobs
               ▼              ▼
┌──────────────────┐   ┌──────────────────────────────────────────────┐
│  PARSE / OCR     │   │  INDEXER                                      │
│  PyMuPDF + pdfminer  │  OpenSearch (BM25, per-language analyzers)   │
│  Tesseract OCR   │   │  pgvector (HNSW embeddings)                  │
│  langdetect      │   │  Hybrid BM25 + vector search                 │
└──────────────────┘   └──────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        API LAYER (internal)                          │
│  FastAPI REST + gRPC                                                 │
│  GET /health · POST /ingest/url · POST /ingest/upload                │
│  GET /manuals · GET /manuals/{id}/download · GET /manuals/{id}/pages │
│  POST /search/text · POST /search/semantic · GET /lineage/{id}       │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   CONSUMER APPS (separate)                           │
│  Any app that serves manuals to end-users                            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Content ID
- SHA-256 hex digest of the canonical blob bytes
- Immutable — same content always same ID
- Used as S3 key: `blobs/sha256/{prefix2}/{sha256}`

### Logical ID
- Format: `{make}:{model}:{year}:{trim}:{lang}:{region}:{revision}`
- Example: `toyota:camry:2012:le:es:us:1`
- Multiple logical IDs can point to the same content_id (same PDF, different editions)

### Document Versions
- Immutable — never overwrite, always insert new version
- `previous_content_id` links the chain
- Diff metadata: added/removed pages, text similarity score

---

## CDC Events

Published to Kafka topic `vmw-events`:

| Event Type | Trigger |
|-----------|---------|
| `manual.created` | New document ingested |
| `manual.versioned` | Updated version of existing manual |
| `parse.completed` | PDF/HTML parsing finished |
| `ocr.completed` | Tesseract OCR finished |
| `index.updated` | OpenSearch index upserted |

---

## Compliance

- `robots.txt` parsed and respected per-adapter before every fetch
- `Crawl-delay` directive honoured (minimum 2 s default)
- OEM ToS reviewed per adapter; non-compliant adapters disabled
- Audit log via `events` table + Kafka events
- Legal hold flag on `documents` table

---

## SLOs

| Metric | Target |
|--------|--------|
| Manual availability after discovery | 95% within 24 h |
| Search latency (p95) | < 300 ms |
| Ingestion success rate | ≥ 95% |
| Parse latency (p95) | < 60 s |
