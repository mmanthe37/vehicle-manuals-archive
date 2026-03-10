# Local Dev Quickstart

## Prerequisites

- Docker + Docker Compose v2
- Python 3.12
- Make

## 1. Bootstrap Python environment

```bash
make bootstrap
```

This installs all Python dependencies and editable service packages.

## 2. Start the local stack

```bash
make compose-up
# or: docker compose -f docker/docker-compose.yml up -d
```

Services started:
- MinIO (S3-compatible): http://localhost:9001 (admin/minioadmin)
- Postgres (pgvector): localhost:5432 (vmw/vmwpass/vmw)
- OpenSearch: http://localhost:9200
- Redpanda (Kafka): localhost:19092
- Airflow: http://localhost:8080 (airflow/airflow)
- API: http://localhost:8000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Jaeger: http://localhost:16686

## 3. Run the demo seed ingest

```bash
make seed-ingest
# or: vmw seed run --adapter mock_oem
```

This runs the mock OEM adapter end-to-end:
1. Discovers Toyota Camry 2012 (en, es) and Honda Civic 2015 (en)
2. Reads fixture PDFs from `tests/fixtures/corpus/`
3. Computes SHA-256 content IDs
4. Stores blobs in MinIO
5. Queues parse and index jobs

## 4. Verify via API

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"vehicle-manuals-archive-api"}

curl "http://localhost:8000/manuals?make=toyota&model=camry&year=2012&language=es"
```

## 5. Run tests

```bash
make test
# or for smoke tests only:
pytest tests/e2e/ -v -m smoke
```

## 6. Stop the stack

```bash
make compose-down
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VMW_MINIO_ENDPOINT` | `http://localhost:9000` | MinIO/S3 endpoint |
| `VMW_PG_DSN` | `postgresql://vmw:vmwpass@localhost:5432/vmw` | Postgres DSN |
| `VMW_OPENSEARCH_HOST` | `http://localhost:9200` | OpenSearch host |
| `VMW_KAFKA_BOOTSTRAP` | `localhost:19092` | Kafka bootstrap servers |
| `LOG_LEVEL` | `INFO` | Log level |
