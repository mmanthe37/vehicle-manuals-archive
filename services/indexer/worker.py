"""Indexer worker: consumes CDC events and upserts OpenSearch / pgvector."""

from __future__ import annotations

import asyncio
import json
import os
import sys

from libs.common.logging import configure_logging, get_logger

configure_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

KAFKA_BOOTSTRAP = os.getenv("VMW_KAFKA_BOOTSTRAP", "localhost:9092")
OPENSEARCH_HOST = os.getenv("VMW_OPENSEARCH_HOST", "http://localhost:9200")
TOPIC = "vmw-events"


async def run_worker() -> None:
    logger.info("indexer_worker_start", kafka=KAFKA_BOOTSTRAP)
    try:
        from aiokafka import AIOKafkaConsumer

        consumer = AIOKafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id="indexer-workers",
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        await consumer.start()
        logger.info("kafka_consumer_started")
        async for msg in consumer:
            await _handle_event(msg.value)
    except Exception as exc:
        logger.error("indexer_worker_error", exc=str(exc))
        sys.exit(1)


async def _handle_event(event: dict) -> None:
    from services.indexer.opensearch.indexer import OpenSearchIndexer

    event_type = event.get("event_type", "")
    if event_type in ("manual.created", "manual.versioned", "parse.completed"):
        indexer = OpenSearchIndexer(hosts=[OPENSEARCH_HOST])
        indexer.ensure_indexes()
        indexer.upsert_manual(event.get("payload", {}))
        logger.info("index_upsert", event_type=event_type, content_id=event.get("content_id"))


if __name__ == "__main__":
    asyncio.run(run_worker())
