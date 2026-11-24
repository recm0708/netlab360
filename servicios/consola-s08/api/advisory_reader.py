"""Consulta asesora S07 por socket Unix; sin acceso a rutas de intervención."""
from __future__ import annotations

import http.client
from pathlib import Path
import socket
import stat
import struct
from types import MappingProxyType

from . import readers

SOCKET = Path("/run/netlab360-s07-api/api.sock")
SECTIONS = MappingProxyType({
    "incidents": "CANDIDATE_INCIDENTS",
    "hypotheses": "RCA_AND_RECOMMENDATIONS",
    "runbooks": "DECLARATIVE_RUNBOOKS",
})
MAX_BYTES = 2_000_000


class UnixHTTP(http.client.HTTPConnection):
    """Comprobar el servidor conectado, no solo los permisos del nombre."""

    def connect(self):
        info = SOCKET.lstat()
        parent = SOCKET.parent.lstat()
        if (not stat.S_ISSOCK(info.st_mode) or info.st_uid != 0
                or stat.S_IMODE(info.st_mode) != 0o660
                or not stat.S_ISDIR(parent.st_mode) or parent.st_uid != 0
                or parent.st_mode & 0o022):
            raise ValueError("UNTRUSTED_UNIX_SOCKET")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.settimeout(self.timeout)
            sock.connect(str(SOCKET))
            _, uid, _ = struct.unpack("3i", sock.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
            if uid != 0:
                raise ValueError("UNTRUSTED_UNIX_PEER")
        except BaseException:
            sock.close()
            raise
        self.sock = sock


def fetch(section):
    """Solo tres GET fijos; nunca reenviar rutas o cuerpos del navegador."""
    if section not in SECTIONS:
        raise ValueError("INVALID_ADVISORY_SECTION")
    conn = UnixHTTP("localhost", timeout=3)
    try:
        conn.request("GET", "/api/v1/" + section, headers={
            "Accept": "application/json", "Accept-Encoding": "identity", "Connection": "close"})
        with conn.getresponse() as response:
            if response.status != 200:
                return None, readers.now_utc(), "UNAVAILABLE"
            if response.getheader("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                return None, readers.now_utc(), "INVALID"
            if response.getheader("Content-Encoding", "identity").lower() != "identity":
                return None, readers.now_utc(), "INVALID"
            payload = readers.decode(response.read(MAX_BYTES+1), MAX_BYTES)
        return payload, readers.now_utc(), "OK"
    except FileNotFoundError:
        return None, readers.now_utc(), "NOT_STARTED"
    except (OSError, http.client.HTTPException):
        return None, readers.now_utc(), "UNAVAILABLE"
    except (ValueError, UnicodeError, RecursionError):
        return None, readers.now_utc(), "INVALID"
    finally:
        conn.close()


def count_rows(value, predicate):
    if not isinstance(value, list) or len(value) > 4096:
        raise ValueError("INVALID_ADVISORY_ROWS")
    if any(not isinstance(row, dict) or not predicate(row) for row in value):
        raise ValueError("INVALID_ADVISORY_ROW")
    return len(value)


def summary(section, data):
    """Proyectar únicamente cantidades con semántica no autorizante."""
    if section == "incidents":
        return {"candidates": count_rows(data, lambda row:
            row.get("schema") == "NETLAB360_S07_INCIDENT_V1"
            and row.get("status") == "CANDIDATE" and row.get("confirmed") is False
            and row.get("root_cause") is None and row.get("ground_truth") == "UNKNOWN"
            and row.get("network_mutations_authorized") is False)}
    root = readers.obj(data)
    if section == "hypotheses":
        diagnosis = readers.obj(root.get("diagnosis"))
        recommendations = readers.obj(root.get("recommendations"))
        if (diagnosis.get("schema") != "NETLAB360_S07_RCA_V1"
                or diagnosis.get("root_cause") is not None
                or type(diagnosis.get("confirmed_incidents")) is not int
                or diagnosis["confirmed_incidents"] != 0
                or diagnosis.get("network_mutations_authorized") is not False
                or recommendations.get("schema") != "NETLAB360_S07_RECOMMENDATION_V1"
                or recommendations.get("approval_granted") is not False
                or recommendations.get("requires_fresh_evidence") is not True
                or recommendations.get("network_mutations_authorized") is not False):
            raise ValueError("INVALID_RCA_ENVELOPE")
        return {
            "hypotheses": count_rows(diagnosis.get("hypotheses"), lambda row:
                row.get("status") == "HYPOTHESIS" and row.get("confirmed") is False
                and row.get("root_cause") is None and row.get("network_mutations_authorized") is False),
            "recommendations": count_rows(recommendations.get("recommendations"), lambda row:
                row.get("requires_fresh_evidence") is True
                and row.get("network_mutations_authorized") is False),
            "coverage_gaps": count_rows(diagnosis.get("coverage_gaps"), lambda row:
                isinstance(row.get("context_id"), str)),
        }
    if section != "runbooks" or root.get("schema") != "NETLAB360_S07_RUNBOOK_CATALOG_V1":
        raise ValueError("INVALID_RUNBOOK_SCHEMA")
    actions = root.get("actions")
    if (type(root.get("version")) is not int or root["version"] != 1
            or root.get("network_mutations_authorized") is not False
            or not isinstance(actions, dict) or len(actions) > 128
            or any(not isinstance(row, dict) or row.get("execution_authorized") is not False
                   or type(row.get("mutation")) is not bool
                   or row.get("approval_required") is not row["mutation"] for row in actions.values())):
        raise ValueError("INVALID_RUNBOOK_CATALOG")
    return {"read_only_runbooks": sum(not row["mutation"] for row in actions.values()),
            "controlled_change_runbooks": sum(row["mutation"] for row in actions.values())}


def project(section, payload, received, transport):
    """Conservar fecha histórica; nunca proyectar una causa o salud confirmada."""
    if section not in SECTIONS:
        raise ValueError("INVALID_ADVISORY_SECTION")
    root = readers.obj(payload)
    result = readers.obj(root.get("result"))
    details = {}
    if transport == "OK":
        try:
            if (root.get("schema") != "NETLAB360_S07_API_V1" or root.get("ok") is not True
                    or result.get("source") != "OPERATOR_ADVISORY_SNAPSHOT"
                    or result.get("historical") is not True
                    or result.get("authorization_evidence") is not False):
                raise ValueError("INVALID_ADVISORY_ENVELOPE")
            details = summary(section, result.get("data"))
            details.update(historical=True, authorization_evidence=False)
        except ValueError:
            transport = "INVALID"
    return readers.observation("ADVISORY_S07", section.upper(), SECTIONS[section],
                               received, transport, result.get("observed_at_utc"),
                               details=details)


def collect():
    """Consultar secciones independientes sin iniciar la API protegida."""
    return [project(section, *fetch(section)) for section in SECTIONS]
