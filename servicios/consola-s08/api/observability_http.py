"""Exposición autenticada de observabilidad con consultas predefinidas."""
import asyncio
import time

from fastapi import HTTPException, Request
from starlette.concurrency import run_in_threadpool

from . import observability_reader, sessions
from .auth_http import COOKIE


def register_observability(app, directory):
    gate = asyncio.Lock()
    last = float("-inf")

    async def identity(request):
        actor = await run_in_threadpool(sessions.resolve, directory, request.cookies.get(COOKIE))
        if actor is None:
            raise HTTPException(401)
        return actor

    @app.get("/api/v1/observability/probes")
    async def probes(request: Request):
        nonlocal last
        actor = await identity(request)
        if request.query_params:
            raise HTTPException(400)
        if gate.locked() or time.monotonic() - last < 2:
            raise HTTPException(429, headers={"Retry-After": "2"})
        async with gate:
            last = time.monotonic()
            try:
                result = await run_in_threadpool(observability_reader.collect)
            except Exception:
                raise HTTPException(503) from None
            if await identity(request) != actor:
                raise HTTPException(403)
            return result
