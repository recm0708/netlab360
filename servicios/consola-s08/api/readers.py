"""Lectura delimitada S04/S05; sin redirecciones, proxy ni destinos del cliente."""
from __future__ import annotations

from datetime import datetime, timezone
import http.client
import json
import math
from types import MappingProxyType

from .contracts import source_metadata

ENDPOINTS = MappingProxyType({
    "EXPORTER_S04": (9110, "/api/v1/state"),
    "NOC_S05": (9130, "/api/v1/graph"),
})
MAX_BYTES = 262144
TIMEOUT = 3
SITES = ("HQ", "S1", "S2")
ROUTERS = {"R-" + site for site in SITES}


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def unique_pairs(pairs):
    """Rechazar claves duplicadas en todos los niveles JSON."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("NONFINITE_JSON")


def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("NONFINITE_JSON")
    return result


def decode(raw, max_bytes=None):
    """Validar tamaño, estructura y números antes de proyectar."""
    if len(raw) > (MAX_BYTES if max_bytes is None else max_bytes):
        raise ValueError("BODY_TOO_LARGE")
    value = json.loads(raw, object_pairs_hook=unique_pairs,
                       parse_constant=reject_constant, parse_float=finite_float)
    if not isinstance(value, dict):
        raise ValueError("JSON_NOT_OBJECT")
    return value


def fetch(source):
    """Usar exclusivamente GET local fijo; distinguir transporte y datos inválidos."""
    if source not in ENDPOINTS:
        raise ValueError("INVALID_SOURCE")
    port, path = ENDPOINTS[source]
    return _fetch_fixed(port, path, MAX_BYTES)


def _fetch_fixed(port, path, max_bytes):
    """Transporte interno para destinos definidos por el código, no por HTTP."""
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=TIMEOUT)
    try:
        conn.request("GET", path, headers={"Accept": "application/json",
                                          "Accept-Encoding": "identity",
                                          "Connection": "close"})
        with conn.getresponse() as response:
            if response.status != 200:
                status = "UNAVAILABLE" if response.status >= 500 else "INVALID"
                return None, now_utc(), status
            if response.getheader("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                return None, now_utc(), "INVALID"
            if response.getheader("Content-Encoding", "identity").lower() != "identity":
                return None, now_utc(), "INVALID"
            payload = decode(response.read(max_bytes + 1), max_bytes)
        return payload, now_utc(), "OK"
    except (OSError, http.client.HTTPException):
        return None, now_utc(), "UNAVAILABLE"
    except (ValueError, UnicodeError, RecursionError):
        return None, now_utc(), "INVALID"
    finally:
        conn.close()


def obj(value):
    return value if isinstance(value, dict) else {}


def observation(source, resource, scope, received, transport, stamp=None,
                state="UNKNOWN", details=None):
    """No entregar detalles antiguos, futuros, ausentes ni inválidos."""
    result = source_metadata(source=source, transport=transport,
                             observed_at_utc=stamp, received_at_utc=received, state=state)
    result.update(resource=resource, scope=scope,
                  details=(details or {}) if result["quality"] == "VALID" else {})
    return result


def exporter(payload, received, transport):
    """Existencia de routers, no OSPF, forwarding ni disponibilidad HTTP."""
    root = obj(payload)
    routers = obj(root.get("routers"))
    status = root.get("topology")
    if transport == "OK":
        if root.get("project") != "NETLAB360" or root.get("phase") != "S04":
            transport = "INVALID"
        elif root.get("source_ok") is not True:
            transport = "UNAVAILABLE" if root.get("source_ok") is False else "INVALID"
        elif (set(routers) != ROUTERS
              or any(type(value) is not int or value not in (0, 1) for value in routers.values())
              or status != ("active" if sum(routers.values()) == 3 else
                            "partial" if sum(routers.values()) else "offline")):
            transport = "INVALID"
    return [observation("EXPORTER_S04", "MULTISEDE", "ROUTER_EXISTENCE_ONLY",
                        received, transport, root.get("observed_at_utc"),
                        details={"reported_topology": status, **routers})]


def noc(payload, received, transport):
    """Conservar fechas independientes y alcance de las observaciones S05."""
    root = obj(payload)
    if transport == "OK" and (root.get("project") != "NETLAB360"
            or root.get("phase") != "S05" or type(root.get("schema_version")) is not int
            or root["schema_version"] != 1):
        transport = "INVALID"
    rows = []

    def add(resource, scope, stamp, valid, details, state="UNKNOWN"):
        status = transport if transport != "OK" else ("OK" if valid else "UNAVAILABLE")
        rows.append(observation("NOC_S05", resource, scope, received, status,
                                stamp, state, details))

    tele = obj(root.get("telemetry"))
    topology = tele.get("topology")
    add("MULTISEDE", "TOPOLOGY_OBSERVATION", tele.get("last_sample_utc"),
        tele.get("available") is True and topology in ("active", "offline", "partial"),
        {"reported_topology": topology})
    lacp = obj(root.get("lacp"))
    for site in SITES:
        row = obj(obj(lacp.get("sites")).get(site))
        a, b = row.get("switch_members"), row.get("client_members")
        valid = (lacp.get("status") in ("observed", "partial")
                 and type(a) is int and type(b) is int and 0 <= a <= 2 and 0 <= b <= 2)
        status = ("up" if min(a,b)==2 else "degraded" if min(a,b)==1 else "down") if valid else None
        valid = valid and row.get("status") == status
        add("LACP-"+site, "BOND_MEMBER_STATE", lacp.get("observed_at_utc"), valid,
            {"switch_members": a, "client_members": b},
            {"up":"NORMAL","degraded":"DEGRADED","down":"FAULT"}.get(status,"UNKNOWN"))
    sdn = obj(root.get("sdn"))
    connected, flows = sdn.get("connected"), sdn.get("flow_count")
    valid = (sdn.get("available") is True
             and ((connected is True and sdn.get("status")=="connected"
                   and type(flows) is int and 0 < flows <= 10**9)
                  or (connected is False and sdn.get("status")=="disconnected" and flows is None)))
    add("FAUCET", "CONTROLLER_ONLY", sdn.get("observed_at_utc"), valid,
        {"connected":connected,"flow_count":flows}, "NORMAL" if connected is True else "FAULT")
    ha = obj(root.get("ha_service"))
    status, backend, selected = (ha.get(k) for k in ("status","active_backend","selected_path"))
    valid = (ha.get("available") is True and status in ("running","offline","unknown")
             and (backend,selected) in ((None,None),("BACKEND_HQ","PRINCIPAL"),("BACKEND_S1","RESPALDO"))
             and (status=="running" or backend is None))
    state = ("FAULT" if status=="offline" else
             {"BACKEND_HQ":"NORMAL","BACKEND_S1":"DEGRADED"}.get(backend,"UNKNOWN")
             if status=="running" and isinstance(backend,str) else "UNKNOWN")
    add("FRONTAL_HQ", "HTTP_FROM_S2", ha.get("observed_at_utc"), valid,
        {"status":status,"active_backend":backend,"selected_path":selected},state)
    return rows


def collect():
    """Obtener ambos orígenes por separado, sin alterar el laboratorio."""
    observations = []
    for source, adapter in (("EXPORTER_S04", exporter), ("NOC_S05", noc)):
        payload, received, transport = fetch(source)
        observations.extend(adapter(payload, received, transport))
    return observations
