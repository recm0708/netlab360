"""Contrato de metadatos de fuentes S08, sin E/S ni autorización de acciones."""
from __future__ import annotations

from datetime import datetime, timezone
from types import MappingProxyType

SCHEMA = "NETLAB360_S08_SOURCE_V1"
STATES = frozenset({"NORMAL", "DEGRADED", "FAULT", "RECOVERY", "UNKNOWN"})
TRANSPORTS = frozenset({"OK", "UNAVAILABLE", "NOT_STARTED", "INVALID"})
# Los límites temporales proceden del contrato S07; el asesor usa
# una política inicial S08 y no se considera una observación en vivo.
SOURCES = MappingProxyType({
    "EXPORTER_S04": (60, "OBSERVATION"),
    "NOC_S05": (60, "OBSERVATION"),
    "PROMETHEUS_S04": (60, "OBSERVATION"),
    "IA_S06": (30, "INFERENCE"),
    "ADVISORY_S07": (60, "ADVISORY_SNAPSHOT"),
})


def utc(value: str) -> datetime:
    """Normalizar fechas con zona explícita; no asumir hora local."""
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError("INVALID_TIMESTAMP")
    try:
        stamp = datetime.fromisoformat(value)
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError("INVALID_TIMESTAMP_ZONE")
        return stamp.astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise ValueError("INVALID_TIMESTAMP") from exc


def source_metadata(*, source: str, transport: str,
                    observed_at_utc: str | None,
                    received_at_utc: str,
                    state: str = "UNKNOWN") -> dict:
    """Proyectar exclusivamente metadatos de una observación validada.

    El adaptador aporta la fecha real de la muestra y el estado dentro
    de su alcance. Una fecha de recepción no reemplaza esa evidencia.
    No se trata de una evaluación global de salud de la red.
    """
    if not isinstance(source, str) or source not in SOURCES:
        raise ValueError("INVALID_SOURCE")
    if not isinstance(transport, str) or transport not in TRANSPORTS:
        raise ValueError("INVALID_TRANSPORT")
    if not isinstance(state, str) or state not in STATES:
        raise ValueError("INVALID_STATE")
    received = utc(received_at_utc)
    maximum, kind = SOURCES[source]
    observed = None
    age = None
    if transport == "INVALID":
        quality = "INVALID"
    elif transport != "OK" or observed_at_utc is None:
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
            elif age > maximum:
                quality = "STALE"
            else:
                quality = "VALID"

    # El snapshot asesor y las fuentes no vigentes no acreditan salud.
    projected = state if quality == "VALID" and kind != "ADVISORY_SNAPSHOT" else "UNKNOWN"
    if kind == "INFERENCE" and projected != "NORMAL":
        projected = "UNKNOWN"
    return {
        "schema": SCHEMA,
        "source": source,
        "kind": kind,
        "transport": transport,
        "quality": quality,
        "state": projected,
        "observed_at_utc": observed.isoformat() if observed is not None else None,
        "received_at_utc": received.isoformat(),
        "age_seconds": round(age, 3) if age is not None else None,
        "max_age_seconds": maximum,
        "network_mutations_authorized": False,
    }
