.PHONY: bootstrap dev test lint fmt compose-up compose-down seed-ingest reindex smoke help

PYTHON := python3.12
PIP := pip
DOCKER_COMPOSE := docker compose

help:
@echo "Usage: make <target>"
@echo ""
@echo "Targets:"
@echo "  bootstrap      Install all Python deps and dev tools"
@echo "  dev            Start local dev environment (compose-up)"
@echo "  test           Run all tests"
@echo "  lint           Lint all Python code (ruff)"
@echo "  fmt            Format all Python code (ruff format)"
@echo "  compose-up     Start all Docker Compose services"
@echo "  compose-down   Stop all Docker Compose services"
@echo "  seed-ingest    Run the demo seed ingest (mock OEM adapter)"
@echo "  reindex        Rebuild OpenSearch and pgvector indexes"
@echo "  smoke          Run smoke tests against running stack"

bootstrap:
$(PIP) install --upgrade pip
$(PIP) install -r requirements-dev.txt
$(PIP) install -e libs/common
$(PIP) install -e services/api
$(PIP) install -e services/ingestion
$(PIP) install -e services/parse
$(PIP) install -e services/indexer
$(PIP) install -e cli

dev: compose-up

test:
pytest tests/ -v --tb=short

lint:
ruff check .

fmt:
ruff format .

compose-up:
$(DOCKER_COMPOSE) -f docker/docker-compose.yml up -d

compose-down:
$(DOCKER_COMPOSE) -f docker/docker-compose.yml down

seed-ingest:
vmw seed run --adapter mock_oem

reindex:
vmw index rebuild --scope all

smoke:
pytest tests/e2e/ -v --tb=short -m smoke
