"""SQLAlchemy ORM models for vehicle-manuals-archive."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def _now():
    return datetime.utcnow()


class Make(Base):
    __tablename__ = "makes"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    aliases = Column(JSONB, default=list)


class ModelYear(Base):
    __tablename__ = "model_years"
    id = Column(Integer, primary_key=True)
    make_id = Column(Integer, ForeignKey("makes.id"), nullable=False)
    model_name = Column(String(256), nullable=False)
    year = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint("make_id", "model_name", "year"),)


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    adapter = Column(String(128), nullable=False)
    base_url = Column(Text, nullable=False)
    robots_txt_hash = Column(String(64))
    crawl_delay = Column(Float, default=1.0)
    active = Column(Boolean, default=True)
    last_crawled_at = Column(DateTime)
    metadata_ = Column("metadata", JSONB, default=dict)


class Crawl(Base):
    __tablename__ = "crawls"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(Integer, ForeignKey("sources.id"))
    started_at = Column(DateTime, default=_now)
    finished_at = Column(DateTime)
    status = Column(String(32), default="running")
    docs_discovered = Column(Integer, default=0)
    docs_new = Column(Integer, default=0)
    error_message = Column(Text)


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(64), nullable=False, unique=True, index=True)
    logical_id = Column(String(512), nullable=False, index=True)
    source_url = Column(Text)
    etag = Column(String(256))
    last_modified = Column(String(128))
    capture_at = Column(DateTime, default=_now)
    make = Column(String(128), index=True)
    model = Column(String(256), index=True)
    year = Column(Integer, index=True)
    trim = Column(String(256))
    language = Column(String(16), index=True)
    region = Column(String(8))
    revision = Column(Integer, default=1)
    title = Column(Text)
    mime_type = Column(String(128), default="application/pdf")
    size_bytes = Column(BigInteger)
    sha256 = Column(String(64), nullable=False)
    parse_status = Column(String(32), default="pending")
    ocr_status = Column(String(32), default="not_required")
    page_count = Column(Integer)
    metadata_ = Column("metadata", JSONB, default=dict)
    versions = relationship("DocumentVersion", back_populates="document")
    pages = relationship("Page", back_populates="document")


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    content_id = Column(String(64), nullable=False)
    logical_id = Column(String(512))
    revision = Column(Integer, nullable=False)
    previous_content_id = Column(String(64))
    added_pages = Column(Integer, default=0)
    removed_pages = Column(Integer, default=0)
    text_similarity = Column(Float)
    created_at = Column(DateTime, default=_now)
    document = relationship("Document", back_populates="versions")


class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), index=True)
    page_number = Column(Integer, nullable=False)
    text = Column(Text)
    language = Column(String(16))
    ocr_confidence = Column(Float)
    document = relationship("Document", back_populates="pages")
    __table_args__ = (UniqueConstraint("document_id", "page_number"),)


class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(64), nullable=False, index=True)
    content_id = Column(String(64), index=True)
    logical_id = Column(String(512))
    payload = Column(JSONB, default=dict)
    emitted_at = Column(DateTime, default=_now)
