"""Lectura de series reales de Blackbox con catálogo y corte temporal fijos."""
from datetime import datetime, timezone
import math
import time
from urllib.parse import urlencode

from . import readers, slo_contract as S, slo_window as W

JOB = "netlab360-s08-blackbox"
METRICS = ("up", "probe_success", "probe_duration_seconds", "probe_http_status_code")
MAX_BYTES = 524288


def expression(metric):
    if metric not in METRICS:
        raise ValueError("UNKNOWN_OBSERVATION_METRIC")
    return metric + '{job="' + JOB + '"}[60m]'


def series(payload, metric, end):
    """Rechazar duplicados, identidades externas y valores inválidos."""
    root = readers.obj(payload)
    data = readers.obj(root.get("data"))
    if (root.get("status") != "success" or root.get("warnings") or root.get("infos")
            or data.get("resultType") != "matrix" or not isinstance(data.get("result"), list)):
        raise ValueError("INVALID_OBSERVATION_RESPONSE")
    result = {}
    for item in data["result"]:
        labels = item["metric"]
        key = labels["probe_id"]
        probe = S.probe(key)
        if (key in result or labels.get("__name__") != metric or labels.get("job") != JOB
                or labels.get("instance") != "127.0.0.1:9116"
                or labels.get("laboratory") != "netlab360-lab"
                or labels.get("origin") != probe["origin"] or labels.get("module") != probe["module"]
                or (metric == "probe_http_status_code" and probe["module"] != "http_service")):
            raise ValueError("OBSERVATION_SERIES_IDENTITY")
        values = item["values"]
        if metric in ("up", "probe_success"):
            result[key] = W.samples(values, end - 3600, end)
            continue
        if not isinstance(values, list) or len(values) > 400:
            raise ValueError("INVALID_OBSERVATION_SERIES")
        points = {}
        for stamp, raw in values:
            if (type(stamp) not in (int, float) or not math.isfinite(stamp)
                    or not end - 3600 < stamp <= end or type(raw) not in (str, int, float)):
                raise ValueError("INVALID_OBSERVATION_SAMPLE")
            value = float(raw)
            if not math.isfinite(value) or value < 0:
                raise ValueError("INVALID_OBSERVATION_VALUE")
            if (metric == "probe_duration_seconds" and value > 5
                    or metric == "probe_http_status_code" and (value > 599 or value != int(value))):
                raise ValueError("INVALID_OBSERVATION_VALUE")
            stamp = round(stamp * 1000)
            if stamp in points:
                raise ValueError("DUPLICATE_OBSERVATION_TIMESTAMP")
            points[stamp] = value
        result[key] = points
    return result


def fetch(metric, end):
    path = "/api/v1/query?" + urlencode({"query": expression(metric), "time": str(end)})
    payload, _, transport = readers._fetch_fixed(9091, path, MAX_BYTES)
    if transport != "OK":
        return transport, {}
    try:
        return "OK", series(payload, metric, end)
    except (ValueError, TypeError, KeyError, OverflowError):
        return "INVALID", {}


def stamp(unix):
    return datetime.fromtimestamp(unix, timezone.utc).isoformat()


def collect(end=None):
    """Evaluar las tres ventanas a un corte común, sin interpolar scrapes."""
    end = round(time.time(), 3) if end is None else end
    if type(end) not in (int, float) or not math.isfinite(end) or end <= 3600:
        raise ValueError("INVALID_OBSERVATION_END")
    sources = {metric: fetch(metric, end) for metric in METRICS}
    transport = {metric: row[0] for metric, row in sources.items()}
    rows = []
    for key in S.PROBES:
        row = {"probe": S.probe(key), "windows": [], "samples": [],
               "latest": None, "quality": "UNKNOWN"}
        rows.append(row)
        if any(transport[m] != "OK" for m in ("up", "probe_success")):
            continue
        up, success = (sources[m][1].get(key, {}) for m in ("up", "probe_success"))
        duration = sources["probe_duration_seconds"][1].get(key, {})
        status = sources["probe_http_status_code"][1].get(key, {})
        if any(up.get(t) != 1 for t in success):
            row["quality"] = "INVALID"
            continue
        for minutes in S.WINDOWS_MIN:
            def values(points):
                return [[t / 1000, v] for t, v in sorted(points.items())
                        if end - minutes * 60 < t / 1000 <= end]
            row["windows"].append(W.evaluate(key, minutes, end, values(up), values(success)))
        for t, acquired in sorted(up.items()):
            measured = success.get(t) if acquired == 1 else None
            row["samples"].append({"timestamp_unix": t / 1000, "scrape_up": acquired,
                                   "probe_success": measured,
                                   "duration_seconds": duration.get(t) if measured is not None else None,
                                   "http_status_code": status.get(t) if measured is not None else None})
        if row["samples"]:
            row["latest"] = row["samples"][-1]
            row["quality"] = ("STALE" if end - row["latest"]["timestamp_unix"] > 20 else
                              "VALID" if row["latest"]["probe_success"] is not None else "UNKNOWN")
        else:
            row["quality"] = "ABSENT"
    return {"schema": "NETLAB360_S08_OBSERVABILITY_V1", "source": "PROMETHEUS_REAL",
            "generated_at_utc": stamp(time.time()), "window_end_utc": stamp(end),
            "window_end_unix": end, "transport": transport, "probes": rows,
            "cadence_s": S.CADENCE_S, "target_pct": S.TARGET_PCT}
