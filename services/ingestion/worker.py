"""Ingestion worker: consumes ingest jobs from Kafka topic and runs pipeline."""

from __future__ import annotations

import asyncio
import json
import os
import sys

from libs.common.logging import configure_logging, get_logger

configure_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

KAFKA_BOOTSTRAP = os.getenv("VMW_KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "vmw-ingest-jobs"


async def run_worker() -> None:
    logger.info("ingestion_worker_start", kafka=KAFKA_BOOTSTRAP, topic=TOPIC)
    try:
        from aiokafka import AIOKafkaConsumer

        consumer = AIOKafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id="ingestion-workers",
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        await consumer.start()
        logger.info("kafka_consumer_started")
        async for msg in consumer:
            await _handle_message(msg.value)
    except Exception as exc:
        logger.error("ingestion_worker_error", exc=str(exc))
        sys.exit(1)


async def _handle_message(payload: dict) -> None:
    from libs.common.schemas.ingestion import IngestRequest
    from services.ingestion.fetchers.pipeline import IngestionPipeline

    req = IngestRequest(**payload)
    pipeline = IngestionPipeline()
    result = pipeline.ingest(req)
    logger.info("ingest_done", content_id=result.content_id, logical_id=result.logical_id)


if __name__ == "__main__":
    asyncio.run(run_worker())
