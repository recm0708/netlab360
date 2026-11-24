"""Ruta de observaciones protegida por sesión y adquisición acotada."""
from __future__ import annotations

import asyncio

from fastapi import FastAPI, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from . import readers, sessions, prometheus_reader, inference_reader, advisory_reader
from .auth_http import COOKIE
from .models import SourceBatch, SourceObservation


def register_sources(app: FastAPI, directory) -> None:
    """Exponer solo observaciones normalizadas; sin URL ni comandos del cliente."""
    gate = asyncio.Lock()

    async def acquire(request: Request, collector) -> SourceBatch:
        identity = await run_in_threadpool(sessions.resolve, directory, request.cookies.get(COOKIE))
        if identity is None:
            raise HTTPException(401)
        if request.query_params:
            raise HTTPException(400)
        if gate.locked():
            raise HTTPException(429, headers={"Retry-After": "3"})
        async with gate:
            rows = await run_in_threadpool(collector)
        return SourceBatch(observations=[SourceObservation(**row) for row in rows])

    @app.get("/api/v1/sources", response_model=SourceBatch)
    async def sources(request: Request) -> SourceBatch:
        return await acquire(request, readers.collect)

    @app.get("/api/v1/metrics", response_model=SourceBatch)
    async def metrics(request: Request) -> SourceBatch:
        return await acquire(request, prometheus_reader.collect)

    @app.get("/api/v1/diagnostics", response_model=SourceBatch)
    async def diagnostics(request: Request) -> SourceBatch:
        return await acquire(request, inference_reader.collect)

    @app.get("/api/v1/advisory", response_model=SourceBatch)
    async def advisory(request: Request) -> SourceBatch:
        return await acquire(request, advisory_reader.collect)
