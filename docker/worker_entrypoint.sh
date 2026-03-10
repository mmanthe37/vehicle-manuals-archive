#!/usr/bin/env bash
set -euo pipefail

WORKER_TYPE="${WORKER_TYPE:-ingestion}"
echo "Starting worker type: ${WORKER_TYPE}"

case "${WORKER_TYPE}" in
  ingestion)
    exec python -m services.ingestion.worker
    ;;
  parse)
    exec python -m services.parse.worker
    ;;
  indexer)
    exec python -m services.indexer.worker
    ;;
  *)
    echo "Unknown worker type: ${WORKER_TYPE}" >&2
    exit 1
    ;;
esac
