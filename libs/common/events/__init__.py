"""Event bus: publish CDC events to Kafka and persist to Postgres."""
from __future__ import annotations

import json
from typing import Any

from libs.common.schemas.events import EventEnvelope, EventType


class EventBus:
    """Thin event bus wrapper. Publishes to Kafka topic if configured,
    otherwise falls back to in-memory no-op for testing."""

    def __init__(self, kafka_bootstrap: str | None = None, topic: str = "vmw-events"):
        self.topic = topic
        self._producer = None
        if kafka_bootstrap:
            try:
                from aiokafka import AIOKafkaProducer  # noqa: F401
                self._kafka_bootstrap = kafka_bootstrap
            except ImportError:
                self._kafka_bootstrap = None
        else:
            self._kafka_bootstrap = None

    async def start(self) -> None:
        if self._kafka_bootstrap:
            from aiokafka import AIOKafkaProducer

            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._kafka_bootstrap,
                value_serializer=lambda v: json.dumps(v).encode(),
            )
            await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def publish(self, event: EventEnvelope) -> None:
        if self._producer:
            await self._producer.send(
                self.topic,
                key=event.content_id.encode(),
                value=event.model_dump(mode="json"),
            )

    async def emit(
        self,
        event_type: EventType,
        content_id: str,
        logical_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> EventEnvelope:
        envelope = EventEnvelope(
            event_type=event_type,
            content_id=content_id,
            logical_id=logical_id,
            payload=payload or {},
        )
        await self.publish(envelope)
        return envelope
