"""API histórica autenticada con concurrencia y selección delimitadas."""
import asyncio
import time

from fastapi import FastAPI, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from . import history_reader, sessions
from .auth_http import COOKIE


def register_history(app: FastAPI, directory):
    """Permitir lectura a identidades vigentes sin ampliar autoridad."""
    gate = asyncio.Lock()
    last = float("-inf")

    async def identity(request):
        actor = await run_in_threadpool(sessions.resolve, directory, request.cookies.get(COOKIE))
        if actor is None:
            raise HTTPException(401)
        return actor

    @app.get("/api/v1/history/{group}/{window}")
    async def history(request: Request, group: str, window: str):
        nonlocal last
        actor = await identity(request)
        if (request.query_params or group not in history_reader.GROUPS
                or window not in history_reader.WINDOWS):
            raise HTTPException(400)
        if gate.locked() or time.monotonic() - last < 2:
            raise HTTPException(429, headers={"Retry-After": "2"})
        async with gate:
            last = time.monotonic()
            try:
                result = await run_in_threadpool(history_reader.collect, group, window)
            except Exception:
                raise HTTPException(503) from None
            if await identity(request) != actor:
                raise HTTPException(403)
        return result
