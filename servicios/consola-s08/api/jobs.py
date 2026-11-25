"""Persistencia transaccional de trabajos; todavía sin rutas HTTP ni ejecutor."""
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import json
import uuid

from . import storage
from .job_contract import select

ACTIVE = ("QUEUED", "RUNNING")
MAX_RESULT = 2_000_000


def stamp():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


@contextmanager
def transaction(directory):
    path = storage._directory(directory, create=False)
    with closing(storage._connect(path, readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            if (db.execute("PRAGMA application_id").fetchone()[0] != storage.APPLICATION_ID
                    or db.execute("PRAGMA user_version").fetchone()[0] != storage.LATEST_SCHEMA_VERSION):
                raise ValueError("UNSUPPORTED_STORAGE_SCHEMA")
            yield db
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise


def operator(db, actor):
    if type(actor) is not str or not actor or len(actor) > 128:
        raise ValueError("OPERATOR_REQUIRED")
    if db.execute("SELECT role,enabled FROM users WHERE username=?", (actor,)).fetchone() != ("OPERATOR", 1):
        raise ValueError("OPERATOR_REQUIRED")


def audit(db, event, job_id, actor, timestamp):
    db.execute("INSERT INTO audit_events(event_type,observed_at_utc,details_json) VALUES (?,?,?)",
               (event, timestamp, encode({"job_id": job_id, "actor_id": actor})))


def record(db, job_id):
    row = db.execute("SELECT job_id,action_id,actor_id,created_at_utc,status,finished_at_utc,result_json "
                     "FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    if row is None:
        raise ValueError("JOB_NOT_FOUND")
    keys = ("job_id", "action_id", "actor_id", "created_at_utc", "status", "finished_at_utc", "data")
    result = dict(zip(keys, row))
    result["data"] = json.loads(result["data"])
    if result["data"].get("schema") != "NETLAB360_S08_JOB_V1":
        raise ValueError("JOB_SCHEMA_UNSUPPORTED")
    selection = select(result["data"]["selection"])
    if selection.action != result["action_id"]:
        raise ValueError("JOB_SELECTION_MISMATCH")
    return result


def enqueue(directory, actor, payload):
    """Reservar una única plaza global para trabajos activos de esta base."""
    selection = select(payload)
    job_id, now = str(uuid.uuid4()), stamp()
    data = {"schema": "NETLAB360_S08_JOB_V1", "selection": selection.parameters(),
            "deadline_s": selection.deadline_s, "started_at_utc": None, "result": None}
    with transaction(directory) as db:
        operator(db, actor)
        if db.execute("SELECT 1 FROM jobs WHERE status IN ('QUEUED','RUNNING') LIMIT 1").fetchone():
            raise ValueError("JOB_BUSY")
        db.execute("INSERT INTO jobs(job_id,action_id,actor_id,created_at_utc,status,result_json) "
                   "VALUES (?,?,?,?,?,?)", (job_id, selection.action, actor, now, "QUEUED", encode(data)))
        audit(db, "JOB_QUEUED", job_id, actor, now)
        return record(db, job_id)


def get(directory, actor, job_id):
    """Consultar exclusivamente trabajos propios de un operador habilitado."""
    path = storage._directory(directory, create=False)
    with closing(storage._connect(path, readonly=True)) as db:
        db.execute("BEGIN")
        operator(db, actor)
        result = record(db, job_id)
        if result["actor_id"] != actor:
            raise ValueError("JOB_NOT_FOUND")
        return result


def claim(directory, job_id):
    """Transición interna; no se expone al navegador ni inicia tráfico."""
    with transaction(directory) as db:
        job = record(db, job_id)
        if job["status"] != "QUEUED":
            raise ValueError("INVALID_JOB_TRANSITION")
        operator(db, job["actor_id"])
        now = stamp()
        job["data"]["started_at_utc"] = now
        db.execute("UPDATE jobs SET status='RUNNING',result_json=? WHERE job_id=?",
                   (encode(job["data"]), job_id))
        audit(db, "JOB_RUNNING", job_id, job["actor_id"], now)
        return record(db, job_id)


def cancel_queued(directory, actor, job_id):
    """Cancelar solo trabajos no iniciados; los activos requieren limpieza del broker."""
    with transaction(directory) as db:
        operator(db, actor)
        job = record(db, job_id)
        if job["actor_id"] != actor:
            raise ValueError("JOB_NOT_FOUND")
        if job["status"] != "QUEUED":
            raise ValueError("INVALID_JOB_TRANSITION")
        now = stamp()
        db.execute("UPDATE jobs SET status='CANCELLED',finished_at_utc=? WHERE job_id=?", (now, job_id))
        audit(db, "JOB_CANCELLED", job_id, actor, now)
        return record(db, job_id)


def finish(directory, job_id, result, *, cleanup_verified):
    """Registrar resultado interno solo después de confirmar limpieza del ejecutor."""
    if cleanup_verified is not True:
        raise ValueError("CLEANUP_NOT_VERIFIED")
    if type(result) is not dict or result.get("transport") not in ("OK", "ERROR", "TIMEOUT"):
        raise ValueError("INVALID_JOB_RESULT")
    if len(encode(result).encode()) > MAX_RESULT:
        raise ValueError("JOB_RESULT_TOO_LARGE")
    with transaction(directory) as db:
        job = record(db, job_id)
        if job["status"] != "RUNNING":
            raise ValueError("INVALID_JOB_TRANSITION")
        selection = job["data"]["selection"]
        action = selection["action"]
        is_probe = selection["profile"] == "default"
        expected_schema = ("NETLAB360_S08_PROBE_V1" if is_probe else
                           "NETLAB360_S08_CONTENT_V1" if action == "test.content.tcp" else
                           "NETLAB360_S08_TRANSFER_V1")
        field = "action" if is_probe else "profile"
        if (result.get("schema") != expected_schema or result.get("route") != selection["route"]
                or result.get(field) != selection[field]):
            raise ValueError("JOB_RESULT_SELECTION_MISMATCH")
        measurement = result.get("measurement")
        if result["transport"] == "OK":
            if type(measurement) is not dict or type(measurement.get("status")) is not str:
                raise ValueError("INVALID_JOB_RESULT")
        elif measurement is not None:
            raise ValueError("INVALID_JOB_RESULT")
        # SUCCEEDED indica que la medición se obtuvo, no que la red esté saludable.
        status = "SUCCEEDED" if result["transport"] == "OK" else "FAILED"
        now = stamp()
        job["data"]["result"] = result
        db.execute("UPDATE jobs SET status=?,finished_at_utc=?,result_json=? WHERE job_id=?",
                   (status, now, encode(job["data"]), job_id))
        audit(db, "JOB_" + status, job_id, job["actor_id"], now)
        return record(db, job_id)
