"""Explorador técnico de lectura, con catálogo fijo y proyección de datos."""
import asyncio
from datetime import datetime, timezone
import re
import time

from fastapi import FastAPI, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from . import advisory_reader, inference_reader, prometheus_reader, readers, sessions
from .auth_http import COOKIE

CATALOG = (
    ("health", "/healthz", "Disponibilidad del proceso", "Metadatos públicos"),
    ("capabilities", "/api/v1/capabilities", "Capacidades de la aplicación", "Metadatos públicos"),
    ("sources", "/api/v1/sources", "Exportador y supervisión de red", "Observaciones"),
    ("metrics", "/api/v1/metrics", "Prometheus", "Observaciones"),
    ("diagnostics", "/api/v1/diagnostics", "Inferencia diagnóstica", "Inferencias"),
    ("advisory", "/api/v1/advisory", "Consulta asesora", "Resúmenes históricos"),
)
SOURCE_NAMES = {"EXPORTER_S04": "Exportador", "NOC_S05": "Supervisión de red",
                "PROMETHEUS_S04": "Prometheus", "IA_S06": "Inferencia diagnóstica",
                "ADVISORY_S07": "Consulta asesora"}
RESOURCE_NAMES = {"S04-EXPORTER": "Exportador", "S04-COLLECTOR": "Colector"}
MAX_RECORDS = 128
COOLDOWN = 2


def label(value):
    """Aceptar identificadores delimitados, nunca rutas, trazas ni texto libre."""
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value):
        return "No identificado"
    if re.search(r"(?i)(?:^|[-_])S0[1-9](?:$|[-_])", value):
        return "Recurso interno"
    return value


def project_rows(batch):
    """Exponer metadatos de observación, no cuerpos crudos ni secretos."""
    if len(batch.observations) > MAX_RECORDS:
        raise HTTPException(503)
    return [{
        "source": SOURCE_NAMES[row.source],
        "resource": RESOURCE_NAMES.get(row.resource, label(row.resource)),
        "scope": label(row.scope),
        "transport": row.transport, "quality": row.quality, "state": row.state,
        "observed_at_utc": row.observed_at_utc, "received_at_utc": row.received_at_utc,
        "age_seconds": row.age_seconds, "max_age_seconds": row.max_age_seconds,
    } for row in batch.observations]


def register_debug(app: FastAPI, directory, acquire, health, capabilities):
    """Reutilizar adquisición normalizada y autorización de operador."""
    catalog = {entry[0]: entry for entry in CATALOG}
    gate = asyncio.Lock()
    last = float("-inf")

    async def authorize(request):
        actor = await run_in_threadpool(sessions.resolve, directory, request.cookies.get(COOKIE))
        if actor is None:
            raise HTTPException(401)
        if actor["role"] != "OPERATOR":
            raise HTTPException(403)
        if request.query_params:
            raise HTTPException(400)
        return actor

    @app.get("/api/v1/debug/catalog")
    async def list_catalog(request: Request):
        await authorize(request)
        return {"endpoints": [
            {"id": key, "method": "GET", "path": path, "description": description,
             "schema": schema, "probe": "/api/v1/debug/probe/" + key,
             "role": "OPERATOR"} for key, path, description, schema in CATALOG
        ], "network_mutations_authorized": False}

    @app.get("/api/v1/debug/probe/{key}")
    async def probe(request: Request, key: str):
        nonlocal last
        actor = await authorize(request)
        if key not in catalog:
            raise HTTPException(404)
        if gate.locked() or time.monotonic() - last < COOLDOWN:
            raise HTTPException(429, headers={"Retry-After": str(COOLDOWN)})
        async with gate:
            last = time.monotonic()
            started = last
            records, summary = [], {}
            try:
                if key == "health":
                    data = await health()
                    summary = {"healthy": data.healthy, "infrastructure_state": data.infrastructure_state,
                               "generated_at_utc": data.generated_at_utc.isoformat()}
                elif key == "capabilities":
                    data = await capabilities()
                    summary = {name: value for name, value in data.model_dump().items()
                               if name.endswith("_enabled") or name == "health_available"}
                else:
                    collector = {"sources": readers.collect, "metrics": prometheus_reader.collect,
                                 "diagnostics": inference_reader.collect,
                                 "advisory": advisory_reader.collect}[key]
                    records = project_rows(await acquire(request, key, collector))
            except HTTPException:
                raise
            except Exception:
                # No propagamos excepciones, trazas ni rutas de los lectores.
                raise HTTPException(503) from None
            if await authorize(request) != actor:
                raise HTTPException(403)
            return {"endpoint": catalog[key][1], "method": "GET",
                    "queried_at_utc": datetime.now(timezone.utc).isoformat(),
                    "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    "summary": summary, "records": records,
                    "network_mutations_authorized": False}
