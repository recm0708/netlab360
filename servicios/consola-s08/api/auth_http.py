"""Rutas de identidad S08; límites locales y protección de escrituras de sesión."""
from __future__ import annotations

import asyncio
from collections import deque
import time

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from . import security, sessions, storage
from .models import Identity, LoginInput, LoginResult, LogoutResult

COOKIE = "netlab360_session"
ORIGINS = frozenset({"http://127.0.0.1:9140", "http://localhost:9140"})
MAX_BODY = 4096
MAX_ATTEMPTS = 8
WINDOW = 60


def require_origin(request: Request) -> None:
    """Exigir el origen exacto de la consola local en toda escritura."""
    origin = request.headers.get("origin")
    if origin not in ORIGINS or origin != "http://" + request.headers.get("host", ""):
        raise HTTPException(403)


async def credentials(request: Request) -> LoginInput:
    """Limitar el cuerpo antes de validar; no reflejar valores de entrada."""
    if request.headers.get("content-type", "").split(";",1)[0].strip().lower() != "application/json":
        raise HTTPException(415)
    content = bytearray()
    async for chunk in request.stream():
        if len(content) + len(chunk) > MAX_BODY:
            raise HTTPException(413)
        content.extend(chunk)
    try:
        return LoginInput.model_validate_json(bytes(content))
    except (ValidationError, ValueError):
        raise HTTPException(400) from None


def register(app: FastAPI, directory) -> None:
    """Registrar autenticación solo si existe una base v2 íntegra."""
    if storage.inspect(directory)["schema_version"] not in (2, 3):
        raise ValueError("SECURITY_SCHEMA_REQUIRED")
    attempts = deque()
    gate = asyncio.Lock()

    async def identity(request: Request) -> Identity:
        result = await run_in_threadpool(sessions.resolve,directory,request.cookies.get(COOKIE))
        if result is None:
            raise HTTPException(401)
        return Identity(**result)

    @app.post("/api/v1/auth/login", response_model=LoginResult)
    async def login(request: Request, response: Response) -> LoginResult:
        require_origin(request)
        data = await credentials(request)
        # Límite global por proceso y una derivación costosa simultánea.
        # No acumulamos una cola de solicitudes scrypt.
        now = time.monotonic()
        while attempts and now-attempts[0] >= WINDOW:
            attempts.popleft()
        if len(attempts) >= MAX_ATTEMPTS or gate.locked():
            raise HTTPException(429,headers={"Retry-After":str(WINDOW)})
        attempts.append(now)
        async with gate:
            user = await run_in_threadpool(security.authenticate,directory,data.username,data.password)
            if user is None:
                raise HTTPException(401)
            try:
                issued = await run_in_threadpool(sessions.issue,directory,user["username"])
            except ValueError:
                raise HTTPException(401) from None
        token = issued.pop("token")
        # HTTP exclusivamente local por túnel SSH; Secure exige HTTPS.
        response.set_cookie(COOKIE,token,max_age=sessions.TTL,httponly=True,
                            secure=False,samesite="strict",path="/")
        return LoginResult(**issued)

    @app.get("/api/v1/auth/me", response_model=Identity)
    async def me(request: Request) -> Identity:
        return await identity(request)

    @app.post("/api/v1/auth/resume", response_model=LoginResult)
    async def resume(request: Request) -> LoginResult:
        # La cookie HttpOnly y el origen exacto permiten recuperar CSRF sin
        # guardar secretos en el navegador ni aceptar solicitudes simples.
        require_origin(request)
        if request.headers.get("x-netlab360-resume") != "1":
            raise HTTPException(403)
        result = await run_in_threadpool(sessions.resume,directory,request.cookies.get(COOKIE))
        if result is None:
            raise HTTPException(401)
        return LoginResult(**result)

    async def activity(request: Request, *, confirmed: bool) -> LoginResult:
        require_origin(request)
        await identity(request)
        result = await run_in_threadpool(sessions.touch,directory,request.cookies.get(COOKIE),
                                         request.headers.get("x-csrf-token"),confirmed=confirmed)
        if result is None:
            raise HTTPException(403)
        return LoginResult(**result)

    @app.post("/api/v1/auth/activity", response_model=LoginResult)
    async def record_activity(request: Request) -> LoginResult:
        return await activity(request, confirmed=False)

    @app.post("/api/v1/auth/continue", response_model=LoginResult)
    async def continue_session(request: Request) -> LoginResult:
        return await activity(request, confirmed=True)

    @app.get("/api/v1/auth/operator-check", response_model=Identity)
    async def operator_check(request: Request) -> Identity:
        user = await identity(request)
        if user.role != "OPERATOR":
            raise HTTPException(403)
        return user

    @app.post("/api/v1/auth/logout", response_model=LogoutResult)
    async def logout(request: Request, response: Response) -> LogoutResult:
        require_origin(request)
        await identity(request)
        removed = await run_in_threadpool(sessions.revoke,directory,
                                          request.cookies.get(COOKIE),request.headers.get("x-csrf-token"))
        if not removed:
            raise HTTPException(403)
        response.delete_cookie(COOKIE,path="/",httponly=True,samesite="strict")
        return LogoutResult()
