"""Servidor de arranque S08: metadatos públicos, loopback y ninguna mutación."""
from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .models import ApiError, Capabilities, Health

HOST = "127.0.0.1"
PORT = 9140


def create_app(directory: Path | None = None) -> FastAPI:
    """Crear la API de arranque o habilitar identidades sobre una base v2 explícita."""
    if os.geteuid() == 0:
        raise RuntimeError("S08_ROOT_FORBIDDEN")

    app = FastAPI(title="NETLAB360 S08", version="0.1.0",
                  docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def response_headers(request: Request, call_next):
        # Las respuestas no deben quedar en cachés ni interpretarse como HTML.
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        return response

    # Rechazar Host arbitrario; no confiar en cabeceras de proxy.
    app.add_middleware(TrustedHostMiddleware,
                       allowed_hosts=["127.0.0.1", "localhost"],
                       www_redirect=False)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        code = {400: "BAD_REQUEST", 401: "UNAUTHENTICATED", 403: "FORBIDDEN",
                404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED", 413: "BODY_TOO_LARGE",
                415: "UNSUPPORTED_MEDIA_TYPE", 429: "RATE_LIMITED", 503: "UNAVAILABLE"}.get(
            exc.status_code, "HTTP_ERROR")
        payload = ApiError(error=code)
        return JSONResponse(payload.model_dump(mode="json"),
                            status_code=exc.status_code, headers=exc.headers)

    mode = "AUTHENTICATED_READ_ONLY" if directory is not None else "BOOTSTRAP_READ_ONLY"

    @app.get("/healthz", response_model=Health)
    async def health() -> Health:
        return Health(generated_at_utc=datetime.now(timezone.utc), mode=mode)

    @app.get("/api/v1/capabilities", response_model=Capabilities)
    async def capabilities() -> Capabilities:
        return Capabilities(mode=mode, persistence_enabled=directory is not None,
                            authentication_enabled=directory is not None,
                            source_readers_enabled=directory is not None,
                            diagnostics_enabled=directory is not None,
                            advisory_enabled=directory is not None,
                            frontend_enabled=directory is not None)

    if directory is not None:
        from .auth_http import register
        register(app, directory)
        from .source_http import register_sources
        acquire = register_sources(app, directory)
        from .debug_http import register_debug
        register_debug(app, directory, acquire, health, capabilities)
        from .history_http import register_history
        register_history(app, directory)
        from .topology_http import register_topology
        register_topology(app, directory)
        from .ui_http import register_ui
        register_ui(app, directory)

    return app


def main() -> None:
    """Iniciar solo en loopback, sin recarga ni cabeceras de proxy."""
    import uvicorn

    from .storage import default_dir

    flag = os.environ.get("NETLAB360_S08_AUTH", "0")
    if flag not in ("0", "1"):
        raise ValueError("INVALID_AUTH_MODE")
    directory = default_dir() if flag == "1" else None
    uvicorn.run(create_app(directory), host=HOST, port=PORT, reload=False,
                proxy_headers=False, server_header=False, access_log=False)


if __name__ == "__main__":
    main()
