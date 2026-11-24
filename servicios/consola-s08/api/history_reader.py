"""Lectura histórica de scrapes reales, sin interpolación ni PromQL del cliente."""
from datetime import datetime, timezone
import math
from types import MappingProxyType
from urllib.parse import urlencode

from . import readers, prometheus_reader

adapter = prometheus_reader.adapter
WINDOWS = MappingProxyType({"5m": 300, "15m": 900, "1h": 3600})
MAX_BYTES = 1048576
MAX_POINTS = 2000
UP = adapter.labels_for("up")
COLLECTOR = adapter.labels_for(adapter.PREFIX + "source_up")
GROUPS = MappingProxyType({
    "collection": (("exporter", "SCRAPE_AVAILABILITY", UP),
                   ("collector", "COLLECTOR_READ", COLLECTOR)),
    "routers": tuple(("R-"+site, "CONTAINER_RUNNING_ONLY",
                     adapter.labels_for(adapter.PREFIX+"router_running", router="R-"+site))
                     for site in adapter.WAN),
    "wan": tuple(("WAN-END-"+site+"-"+interface, "ADMIN_STATE_ONLY",
                  adapter.labels_for(adapter.PREFIX+"wan_admin_up", site=site, interface=interface))
                 for site, interfaces in adapter.WAN.items() for interface in interfaces),
    "vlan": tuple(("VLAN-"+str(vlan), "ADMIN_STATE_ONLY",
                   adapter.labels_for(adapter.PREFIX+"vlan_admin_up", site=site, vlan=str(vlan)))
                  for site, vlans in adapter.VLANS.items() for vlan in vlans),
})


def _allowed(group, window):
    if group not in GROUPS or window not in WINDOWS:
        raise ValueError("INVALID_HISTORY_SELECTION")


def query_path(group, window, end):
    """Construir selector con nombres, etiquetas y ventana del catálogo interno."""
    _allowed(group, window)
    names = sorted({dict(key)["__name__"] for _, _, key in GROUPS[group]}
                   | {"up", adapter.PREFIX+"source_up"})
    query = ('{__name__=~"' + "|".join(names) + '",job="' + adapter.JOB
             + '",instance="' + adapter.INSTANCE + '"}[' + window + ']')
    return "/api/v1/query?" + urlencode({"query": query, "time": str(end)})


def _parse(payload, allowed, start, end):
    root = readers.obj(payload)
    data = readers.obj(root.get("data"))
    series = data.get("result")
    if (root.get("status") != "success" or root.get("warnings")
            or data.get("resultType") != "matrix" or not isinstance(series, list)
            or len(series) > len(allowed)):
        raise ValueError("INVALID_HISTORY_MATRIX")
    result = {}
    for row in series:
        row = readers.obj(row)
        metric = readers.obj(row.get("metric"))
        if (not all(isinstance(k, str) and isinstance(v, str) for k, v in metric.items())
                or metric.get("context", "s04") != "s04"
                or metric.get("laboratory", "netlab360-lab") != "netlab360-lab"):
            raise ValueError("INVALID_HISTORY_LABELS")
        key = tuple(sorted((k, v) for k, v in metric.items()
                           if k not in ("context", "laboratory")))
        values = row.get("values")
        if (key not in allowed or key in result or not isinstance(values, list)
                or len(values) > MAX_POINTS):
            raise ValueError("INVALID_HISTORY_SERIES")
        points = {}
        last = start
        for pair in values:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ValueError("INVALID_HISTORY_SAMPLE")
            stamp, value = pair
            if (type(stamp) not in (int, float) or not start < stamp <= end
                    or not math.isfinite(stamp) or stamp <= last
                    or value not in ("-1", "0", "1")):
                raise ValueError("INVALID_HISTORY_SAMPLE")
            points[stamp] = int(value) if value != "-1" else None
            last = stamp
        result[key] = points
    return result


def project(group, window, end, payload, transport):
    """Mantener muestras originales y separar ausencia de un cero medido."""
    _allowed(group, window)
    start = end - WINDOWS[window]
    selected = GROUPS[group]
    allowed = {key for _, _, key in selected} | {UP, COLLECTOR}
    parsed = {}
    if transport == "OK":
        try:
            parsed = _parse(payload, allowed, start, end)
        except (ValueError, TypeError, OverflowError):
            transport = "INVALID"
    series = []
    for name, scope, key in selected:
        points = []
        for stamp, value in parsed.get(key, {}).items():
            if key != UP and parsed.get(UP, {}).get(stamp) != 1:
                value = None
            if key not in (UP, COLLECTOR) and parsed.get(COLLECTOR, {}).get(stamp) != 1:
                value = None
            points.append([stamp, value])
        series.append({"id": name, "scope": scope, "points": points})
    return {"project": "NETLAB360", "schema_version": 1,
            "source": "PROMETHEUS_S04", "group": group, "window": window,
            "transport": transport, "start_epoch": start, "end_epoch": end,
            "scrape_interval_seconds": 2, "series": series,
            "network_mutations_authorized": False}


def collect(group, window):
    """Consultar un intervalo fijo de TSDB con tiempo de evaluación del servidor."""
    end = int(datetime.now(timezone.utc).timestamp())
    payload, _, transport = readers._fetch_fixed(
        9091, query_path(group, window, end), MAX_BYTES)
    return project(group, window, end, payload, transport)
