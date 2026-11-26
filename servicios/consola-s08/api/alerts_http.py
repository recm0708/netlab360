"""Consulta autenticada de alertas y transiciones históricas, sin destinos libres."""
import asyncio
import time

from fastapi import HTTPException, Request
from starlette.concurrency import run_in_threadpool

from . import alerts_reader, notification_reader, sessions
from .auth_http import COOKIE


def register_alerts(app, directory):
    gate = asyncio.Lock()
    last = float("-inf")

    async def actor(request):
        identity = await run_in_threadpool(sessions.resolve, directory, request.cookies.get(COOKIE))
        if identity is None:
            raise HTTPException(401)
        return identity

    @app.get("/api/v1/alerts")
    async def alerts(request: Request):
        nonlocal last
        identity = await actor(request)
        if request.query_params:
            raise HTTPException(400)
        if gate.locked() or time.monotonic() - last < 2:
            raise HTTPException(429, headers={"Retry-After": "2"})
        async with gate:
            last = time.monotonic()
            result = await run_in_threadpool(alerts_reader.collect, directory)
            if await actor(request) != identity:
                raise HTTPException(403)
        return result


    notification_gate = asyncio.Lock()
    notification_last = float("-inf")

    @app.get("/api/v1/alerts/notifications/{scope}")
    async def notifications(request: Request, scope: str):
        nonlocal notification_last
        identity = await actor(request)
        if request.query_params or scope not in notification_reader.SCOPES:
            raise HTTPException(400)
        if scope == "validation" and identity["role"] != "OPERATOR":
            raise HTTPException(403)
        if notification_gate.locked() or time.monotonic() - notification_last < 2:
            raise HTTPException(429, headers={"Retry-After": "2"})
        async with notification_gate:
            notification_last = time.monotonic()
            result = await run_in_threadpool(notification_reader.collect, scope)
            if await actor(request) != identity:
                raise HTTPException(403)
        return result
