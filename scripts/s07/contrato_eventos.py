"""Contrato de observaciones S07. Sin acceso a red, archivos ni ejecución."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import re
from uuid import NAMESPACE_URL, uuid5

SCHEMA = "NETLAB360_S07_EVENT_V1"
SITES = frozenset({"HQ", "S1", "S2"})
STATES = frozenset({"NORMAL", "DEGRADED", "FAULT", "RECOVERY", "UNKNOWN"})
SOURCES = {
    "NOC_S05": {
        "subjects": frozenset({"TOPOLOGY", "WAN", "OSPF", "FIB", "VLAN", "LACP", "SDN", "HTTP_HA"}),
        "endpoint": "/api/v1/graph",
        "max_age": 60,
        "kind": "OBSERVATION",
    },
    "PROMETHEUS_S04": {
        "subjects": frozenset({"METRIC", "WAN", "OSPF", "VLAN", "TOPOLOGY", "EXPORTER"}),
        "endpoint": "/api/v1/query",
        "max_age": 60,
        "kind": "OBSERVATION",
    },
    "IA_S06": {
        "subjects": frozenset({"ICMP_DIAGNOSIS"}),
        "endpoint": "/api/v1/s06/diagnostics",
        "max_age": 30,
        "kind": "INFERENCE",
    },
}
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}\Z")
DETAIL_KEY = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,47}\Z")


def utc(value: str) -> datetime:
    """Exigir fecha con zona y normalizar a UTC; nunca suponer zona local."""
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError("INVALID_TIMESTAMP")
    try:
        stamp = datetime.fromisoformat(value)
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError("INVALID_TIMESTAMP_ZONE")
        return stamp.astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise ValueError("INVALID_TIMESTAMP") from exc


def _identifier(value: object) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError("INVALID_RESOURCE_ID")
    return value


def _details(value: dict | None) -> dict:
    """Admitir únicamente escalares finitos y acotados; sin objetos ejecutables."""
    if value is None:
        return {}
    if not isinstance(value, dict) or len(value) > 24:
        raise ValueError("INVALID_DETAILS")
    out = {}
    for key, item in value.items():
        if not isinstance(key, str) or not DETAIL_KEY.fullmatch(key):
            raise ValueError("INVALID_DETAIL_KEY")
        if item is None or type(item) is bool:
            pass
        elif type(item) is int:
            if abs(item) > 10**18:
                raise ValueError("INVALID_DETAIL_NUMBER")
        elif type(item) is float:
            if not math.isfinite(item):
                raise ValueError("INVALID_DETAIL_NUMBER")
        elif isinstance(item, str):
            if len(item) > 160 or any(ord(ch) < 32 for ch in item):
                raise ValueError("INVALID_DETAIL_TEXT")
        else:
            raise ValueError("INVALID_DETAIL_TYPE")
        out[key] = item
    return out


def _canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def make_event(*, source: str, subject: str, resource_id: str,
               observed_at_utc: str | None, received_at_utc: str,
               state: str, available: bool, site: str | None = None,
               peer_site: str | None = None, details: dict | None = None) -> dict:
    """Normalizar una observación sin elevarla a incidente ni autorización.

    El estado de origen solo se proyecta si la muestra es válida y vigente.
    Para IA se conserva el carácter inferencial y ground truth UNKNOWN.
    """
    if source not in SOURCES or subject not in SOURCES[source]["subjects"]:
        raise ValueError("INVALID_SOURCE_SUBJECT")
    resource = _identifier(resource_id)
    if site is not None and site not in SITES:
        raise ValueError("INVALID_SITE")
    if peer_site is not None and (peer_site not in SITES or site is None or peer_site == site):
        raise ValueError("INVALID_PEER_SITE")
    if state not in STATES or type(available) is not bool:
        raise ValueError("INVALID_STATE")
    if source == "IA_S06" and state not in {"NORMAL", "UNKNOWN"}:
        raise ValueError("UNSUPPORTED_INFERENCE_STATE")
    received = utc(received_at_utc)
    observed = None
    age = None
    if not available:
        quality = "MISSING"
    elif observed_at_utc is None:
        quality = "MISSING"
    else:
        try:
            observed = utc(observed_at_utc)
        except ValueError:
            quality = "INVALID"
        else:
            age = (received - observed).total_seconds()
            if age < 0:
                quality = "FUTURE"
            elif age > SOURCES[source]["max_age"]:
                quality = "STALE"
            else:
                quality = "VALID"
    projected = state if quality == "VALID" else "UNKNOWN"
    safe_details = _details(details)
    event = {
        "schema": SCHEMA,
        "source": source,
        "kind": SOURCES[source]["kind"],
        "subject": subject,
        "resource_id": resource,
        "site": site,
        "peer_site": peer_site,
        "observed_at_utc": observed.isoformat() if observed else None,
        "received_at_utc": received.isoformat(),
        "age_seconds": round(age, 3) if age is not None else None,
        "quality": quality,
        "state": projected,
        "ground_truth": "UNKNOWN",
        "network_mutations_authorized": False,
        "evidence": {
            "endpoint": SOURCES[source]["endpoint"],
            "resource_id": resource,
        },
        "details": safe_details if quality == "VALID" else {},
    }
    # La identidad representa el contenido normalizado de la observación.
    # Un mismo dato recibido repetidamente conserva el ID mientras su calidad
    # no cambie. Los registros sin timestamp usan la recepción como referencia.
    identity = {k: v for k, v in event.items()
                if k not in {"received_at_utc", "age_seconds"}}
    if observed is None:
        identity["received_at_utc"] = event["received_at_utc"]
    event["event_id"] = str(uuid5(NAMESPACE_URL, _canonical(identity)))
    return event


def normalize_batch(events: list[dict]) -> dict:
    """Deduplicar eventos idénticos y ordenar por tiempo de observación.

    Detectar muestras fuera de orden por fuente/recurso sin suprimirlas.
    No deduplicar observaciones contradictorias con identificadores distintos.
    """
    unique = {}
    latest = {}
    duplicate_count = 0
    out_of_order_count = 0
    for event in events:
        if event.get("schema") != SCHEMA or not event.get("event_id"):
            raise ValueError("INVALID_EVENT_CONTRACT")
        key = event["event_id"]
        if key in unique:
            old = unique[key]
            excluded = {"received_at_utc", "age_seconds"}
            if ({k: v for k, v in old.items() if k not in excluded}
                    != {k: v for k, v in event.items() if k not in excluded}):
                raise ValueError("EVENT_ID_CONFLICT")
            duplicate_count += 1
            continue
        unique[key] = event
        if event["observed_at_utc"] is not None:
            stamp = utc(event["observed_at_utc"])
            stream = (event["source"], event["subject"], event["resource_id"],
                      event["site"], event["peer_site"])
            if stream in latest and stamp < latest[stream]:
                out_of_order_count += 1
            latest[stream] = max(stamp, latest.get(stream, stamp))
    ordered = sorted(unique.values(), key=lambda e: (
        e["observed_at_utc"] is None,
        utc(e["observed_at_utc"] or e["received_at_utc"]),
        e["event_id"],
    ))
    return {"schema": "NETLAB360_S07_EVENT_BATCH_V1",
            "events": ordered, "duplicates": duplicate_count,
            "out_of_order": out_of_order_count,
            "network_mutations_authorized": False}
