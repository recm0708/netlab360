"""Ruta topológica de solo lectura, con sesión y frecuencia delimitadas."""
import asyncio
import time

from fastapi import HTTPException, Request
from starlette.concurrency import run_in_threadpool

from . import sessions, topology_reader
from .auth_http import COOKIE


def register_topology(app, directory):
    """No aceptar destinos ni parámetros del navegador."""
    gate = asyncio.Lock()
    last = float("-inf")

    async def actor(request):
        identity = await run_in_threadpool(sessions.resolve, directory, request.cookies.get(COOKIE))
        if identity is None:
            raise HTTPException(401)
        return identity

    @app.get("/api/v1/topology")
    async def topology(request: Request):
        nonlocal last
        identity = await actor(request)
        if request.query_params:
            raise HTTPException(400)
        if gate.locked() or time.monotonic() - last < 2:
            raise HTTPException(429, headers={"Retry-After": "2"})
        async with gate:
            last = time.monotonic()
            result = await run_in_threadpool(topology_reader.collect)
            if await actor(request) != identity:
                raise HTTPException(403)
        return result
