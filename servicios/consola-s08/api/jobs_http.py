"""Integración HTTP optativa de trabajos, sin instalar ni activar el servicio web."""
import json
import logging
import uuid

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from . import jobs, sessions
from .auth_http import COOKIE, MAX_BODY, require_origin
from .job_contract import catalog, select
from .probe_broker import unique_object

LOG = logging.getLogger(__name__)


def dispatch(directory, job_id, transport, stream_transport=None):
    """Ejecutar una sola vez; conservar la reserva si no hay confirmación de limpieza."""
    try:
        job = jobs.claim(directory, job_id)
    except (ValueError, OSError):
        LOG.warning("No se pudo reclamar el trabajo %s", job_id)
        return
    try:
        if job["data"].get("stream_enabled") is True:
            if stream_transport is None:
                raise ValueError("STREAM_NOT_CONFIGURED")
            reply = stream_transport(job["data"]["selection"],
                lambda event: jobs.append_progress(directory, job_id, event),
                lambda: jobs.cancellation_requested(directory, job_id))
            if reply.get("kind") != "final" or reply.get("cleanup_verified") is not True:
                jobs.note_uncertain(directory, job_id, "BROKER_UNCONFIRMED")
                return
            if reply.get("status") == "CANCELLED":
                jobs.finish_cancelled(directory, job_id, cleanup_verified=True)
                return
            reply = dict(reply, schema="NETLAB360_S08_BROKER_V1")
        else:
            reply = transport(job["data"]["selection"])
        if (reply.get("schema") != "NETLAB360_S08_BROKER_V1"
                or reply.get("status") != "OK"
                or type(reply.get("result")) is not dict):
            jobs.note_uncertain(directory, job_id, "BROKER_UNCONFIRMED")
            return
        result = reply["result"]
        if result.get("transport") != "OK":
            jobs.note_uncertain(directory, job_id, "EXECUTION_UNCONFIRMED")
            return
        jobs.finish(directory, job_id, result, cleanup_verified=True)
    except Exception:
        # No liberar ni reintentar una ejecución cuyo resultado se desconoce.
        LOG.warning("Resultado no confirmado del trabajo %s", job_id)
        try:
            jobs.note_uncertain(directory, job_id, "EXECUTION_UNCONFIRMED")
        except Exception:
            LOG.error("No se pudo registrar incertidumbre del trabajo %s", job_id)


def identifier(value):
    try:
        if str(uuid.UUID(value)) != value:
            raise ValueError()
    except (ValueError, AttributeError):
        raise HTTPException(404) from None
    return value


def translate(exc):
    codes = {"OPERATOR_REQUIRED": 403, "JOB_NOT_FOUND": 404, "JOB_BUSY": 409,
             "INVALID_JOB_TRANSITION": 409, "JOB_SCHEMA_UNSUPPORTED": 404}
    return HTTPException(codes.get(str(exc), 400))


async def payload(request):
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        raise HTTPException(415)
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > MAX_BODY:
            raise HTTPException(413)
        raw.extend(chunk)
    try:
        body = json.loads(bytes(raw), object_pairs_hook=unique_object)
        return select(body).parameters()
    except (ValueError, TypeError, RecursionError, UnicodeError):
        raise HTTPException(400) from None


def register_jobs(app: FastAPI, directory, transport, stream_transport=None):
    """Registrar exclusivamente con transporte explícito; no hay activación implícita."""
    async def operator(request, *, write=False):
        token = request.cookies.get(COOKIE)
        user = await run_in_threadpool(sessions.resolve, directory, token)
        if user is None:
            raise HTTPException(401)
        if user["role"] != "OPERATOR":
            raise HTTPException(403)
        if write:
            require_origin(request)
            verified = await run_in_threadpool(
                sessions.resolve, directory, token, csrf=request.headers.get("x-csrf-token"),
                require_csrf=True)
            if verified is None or verified != user:
                raise HTTPException(403)
        return user["username"]

    @app.get("/api/v1/jobs/catalog")
    async def job_catalog(request: Request):
        await operator(request)
        rows = [dict(row, execution_enabled=True,
                     live_progress=stream_transport is not None and row["action"] == "test.content.tcp",
                     active_cancel=stream_transport is not None and row["action"] == "test.content.tcp")
                for row in catalog()]
        return {"selections": rows, "transport_configured": True,
                "network_mutations_authorized": False}

    @app.get("/api/v1/jobs")
    async def job_history(request: Request):
        actor = await operator(request)
        return {"jobs": await run_in_threadpool(jobs.history, directory, actor), "limit": 50}

    @app.post("/api/v1/jobs", status_code=202)
    async def submit(request: Request, background: BackgroundTasks):
        actor = await operator(request, write=True)
        selection = await payload(request)
        try:
            job = await run_in_threadpool(jobs.enqueue, directory, actor, selection,
                                          stream_enabled=stream_transport is not None)
        except ValueError as exc:
            raise translate(exc) from None
        background.add_task(dispatch, directory, job["job_id"], transport, stream_transport)
        return job

    @app.get("/api/v1/jobs/{job_id}")
    async def read_job(job_id: str, request: Request):
        actor = await operator(request)
        try:
            return await run_in_threadpool(jobs.get, directory, actor, identifier(job_id))
        except ValueError as exc:
            raise translate(exc) from None

    @app.post("/api/v1/jobs/{job_id}/cancel")
    async def cancel(job_id: str, request: Request):
        actor = await operator(request, write=True)
        try:
            return await run_in_threadpool(jobs.request_cancel, directory, actor, identifier(job_id))
        except ValueError as exc:
            raise translate(exc) from None
