"""FastAPI application for the vehicle-manuals-archive internal API."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.app.routers import health, ingest, lineage, manuals, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vehicle Manuals Archive API",
        description="Internal API for OEM vehicle owner's manuals corpus.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
    app.include_router(manuals.router, prefix="/manuals", tags=["manuals"])
    app.include_router(search.router, prefix="/search", tags=["search"])
    app.include_router(lineage.router, prefix="/lineage", tags=["lineage"])

    return app


app = create_app()
