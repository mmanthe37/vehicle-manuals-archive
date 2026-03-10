# ADR-001: Content-Addressable Storage

## Status: Accepted

## Context
Need immutable, deduplicated storage for potentially millions of PDFs.

## Decision
Store all blobs keyed by SHA-256 hash: `s3://oem-manuals/blobs/sha256/{prefix2}/{hash}`

## Consequences
- Automatic deduplication (same content → same key)
- Immutable once written
- Logical pointers separate from physical storage
- Cross-language/region editions of same PDF share one blob

---

# ADR-002: Postgres + pgvector as Primary Metadata Store

## Status: Accepted

## Context
Need structured metadata queries, versioning, and vector similarity search.

## Decision
Use Postgres (RDS) with pgvector extension for both relational metadata and
HNSW vector index.

## Consequences
- Single database for metadata + embeddings
- pgvector HNSW supports fast approximate nearest-neighbour search
- OpenSearch used for full-text BM25 (not Postgres FTS) for language-aware analysis

---

# ADR-003: Python 3.12 + FastAPI

## Status: Accepted

## Context
Need async, high-throughput API with good OpenAPI support.

## Decision
Python 3.12 (improved typing, performance), FastAPI for REST, grpcio for gRPC.

---

# ADR-004: Airflow for Orchestration

## Status: Accepted

## Context
Need scheduled DAGs with retry, backoff, idempotency, and monitoring.

## Decision
Apache Airflow (MWAA in production, docker-compose locally). Temporal as
alternative for event-driven workflows.

---

# ADR-005: Redpanda (Kafka-compatible) for CDC

## Status: Accepted

## Context
Need CDC event stream for indexer to consume parse/ingest completions.

## Decision
Redpanda in local dev (lightweight, Kafka API compatible), MSK in production.
Events: `manual.created`, `parse.completed`, etc.
