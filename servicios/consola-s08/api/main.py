"""Servidor de arranque S08: metadatos públicos, loopback y ninguna mutación."""
from __future__ import annotations

from datetime import datetime, timezone
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .models import ApiError, Capabilities, Health

HOST = "127.0.0.1"
PORT = 9140


def create_app() -> FastAPI:
    """Crear una aplicación sin E/S de red, persistencia ni procesos auxiliares."""
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
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response

    # Rechazar Host arbitrario; no confiar en cabeceras de proxy.
    app.add_middleware(TrustedHostMiddleware,
                       allowed_hosts=["127.0.0.1", "localhost"],
                       www_redirect=False)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        code = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(
            exc.status_code, "HTTP_ERROR")
        payload = ApiError(error=code)
        return JSONResponse(payload.model_dump(mode="json"),
                            status_code=exc.status_code, headers=exc.headers)

    @app.get("/healthz", response_model=Health)
    async def health() -> Health:
        return Health(generated_at_utc=datetime.now(timezone.utc))

    @app.get("/api/v1/capabilities", response_model=Capabilities)
    async def capabilities() -> Capabilities:
        return Capabilities()

    return app


def main() -> None:
    """Iniciar solo en loopback, sin recarga ni cabeceras de proxy."""
    import uvicorn

    uvicorn.run(create_app(), host=HOST, port=PORT, reload=False,
                proxy_headers=False, server_header=False, access_log=False)


if __name__ == "__main__":
    main()
