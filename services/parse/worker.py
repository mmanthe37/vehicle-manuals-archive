"""Parse worker: consumes parse jobs from Kafka and runs PDF/OCR pipeline."""
from __future__ import annotations

import asyncio
import json
import os
import sys

from libs.common.logging import configure_logging, get_logger

configure_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

KAFKA_BOOTSTRAP = os.getenv("VMW_KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "vmw-parse-jobs"


async def run_worker() -> None:
    logger.info("parse_worker_start", kafka=KAFKA_BOOTSTRAP, topic=TOPIC)
    try:
        from aiokafka import AIOKafkaConsumer

        consumer = AIOKafkaConsumer(
            TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id="parse-workers",
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        await consumer.start()
        logger.info("kafka_consumer_started")
        async for msg in consumer:
            await _handle_message(msg.value)
    except Exception as exc:
        logger.error("parse_worker_error", exc=str(exc))
        sys.exit(1)


async def _handle_message(payload: dict) -> None:
    from services.parse.parsers.pdf import parse_pdf

    content_id = payload.get("content_id", "unknown")
    data = payload.get("data", b"")
    if isinstance(data, str):
        import base64
        data = base64.b64decode(data)
    result = parse_pdf(data, content_id)
    logger.info("parse_done", content_id=content_id, pages=result.page_count)


if __name__ == "__main__":
    asyncio.run(run_worker())
