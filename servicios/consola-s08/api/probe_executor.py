"""Ejecutor manual de diagnóstico acotado; no es un servicio privilegiado de la API."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import time

from .probe_catalog import HTTP_PATH, HTTP_PORT, resolve

ACTIONS = ("test.ping.short", "test.ping.long", "test.traceroute", "test.http")
ENV = {"PATH": "/usr/sbin:/usr/bin", "LC_ALL": "C"}
LIMIT = 131072


def command(action, route):
    """Construir argv desde el catálogo; nunca interpolar una entrada en shell."""
    src, dst, profile = resolve(action, route)
    if action not in ACTIONS:
        raise ValueError("EXECUTION_NOT_IMPLEMENTED")
    if action.startswith("test.ping."):
        args = ["/usr/bin/ping", "-4", "-n", "-c", str(profile.packets),
                "-i", "1", "-W", "1", "-w", str(profile.timeout_s), dst.address]
    elif action == "test.traceroute":
        args = ["/usr/sbin/traceroute", "-4", "-n", "-I", "-m", str(profile.hops),
                "-q", "1", "-w", "1", dst.address]
    else:
        args = ["/usr/bin/curl", "-q", "--noproxy", "*", "--proto", "=http",
                "--connect-timeout", "2", "--max-time", str(profile.timeout_s),
                "--max-filesize", "65536", "--silent", "--show-error",
                "--write-out", "\nHTTP_STATUS=%{http_code}\nHTTP_TOTAL_S=%{time_total}\n",
                f"http://{dst.address}:{HTTP_PORT}{HTTP_PATH}"]
    return src, dst, profile, args


def invoke(namespace, args, seconds):
    """Aplicar timeout dentro del namespace y otro límite en el proceso supervisor."""
    argv = ["/usr/bin/sudo", "-n", "--", "/usr/sbin/ip", "netns", "exec",
            namespace, "/usr/bin/env", "-i", "PATH=/usr/sbin:/usr/bin", "LC_ALL=C",
            "/usr/bin/timeout", "--kill-after=1", str(seconds), *args]
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=ENV, timeout=seconds + 5, check=False)
    if len(result.stdout) + len(result.stderr) > LIMIT:
        raise ValueError("OUTPUT_LIMIT")
    return result


def verify_identity(src, dst, runner):
    """Comprobar identidad de ambos endpoints y ruta de salida antes de emitir tráfico."""
    for endpoint in (src, dst):
        reply = runner(endpoint.namespace, ["/usr/sbin/ip", "-j", "-4", "addr",
                                            "show", "dev", endpoint.interface], 5)
        if reply.returncode:
            raise ValueError("IDENTITY_UNAVAILABLE")
        rows = json.loads(reply.stdout)
        if len(rows) != 1 or rows[0].get("ifname") != endpoint.interface:
            raise ValueError("IDENTITY_MISMATCH")
        addresses = [x["local"] for x in rows[0].get("addr_info", [])
                     if x.get("family") == "inet" and x.get("prefixlen") == 24]
        if addresses != [endpoint.address]:
            raise ValueError("IDENTITY_MISMATCH")
    reply = runner(src.namespace, ["/usr/sbin/ip", "-j", "-4", "route", "get",
                                   dst.address], 5)
    if reply.returncode:
        raise ValueError("ROUTE_UNAVAILABLE")
    rows = json.loads(reply.stdout)
    if len(rows) != 1:
        raise ValueError("ROUTE_MISMATCH")
    row = rows[0]
    if (row.get("dst") != dst.address or row.get("dev") != src.interface
            or row.get("prefsrc", row.get("src")) != src.address
            or row.get("gateway") != src.gateway):
        raise ValueError("ROUTE_MISMATCH")


def percentile(values):
    """P95 lineal sobre las respuestas observadas, sin imputar paquetes perdidos."""
    if not values:
        return None
    ordered = sorted(values)
    rank = (len(ordered) - 1) * 0.95
    lo = math.floor(rank)
    hi = math.ceil(rank)
    return round(ordered[lo] + (rank - lo) * (ordered[hi] - ordered[lo]), 3)


def parse_ping(raw, expected, rc):
    summary = re.search(r"(\d+) packets transmitted, (\d+) (?:packets )?received, "
                        r"(?:\+\d+ errors, )?([\d.]+)% packet loss", raw)
    if rc not in (0, 1) or not summary:
        raise ValueError("PING_OUTPUT_INVALID")
    sent, received = map(int, summary.groups()[:2])
    loss = float(summary[3])
    if not (0 < sent <= expected and 0 <= received <= sent
            and abs(loss - 100 * (sent - received) / sent) <= 0.11):
        raise ValueError("PING_COUNTS_INVALID")
    samples = [{"seq": int(seq), "rtt_ms": float(value)}
               for seq, value in re.findall(r"icmp_seq=(\d+)[^\n]*?\btime=([\d.]+) ms", raw)]
    if (len(samples) != received or len({x["seq"] for x in samples}) != received
            or any(not 1 <= x["seq"] <= sent or not math.isfinite(x["rtt_ms"])
                   for x in samples)):
        raise ValueError("PING_SAMPLES_INVALID")
    stats = re.search(r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms", raw)
    if bool(stats) != bool(received):
        raise ValueError("PING_RTT_INVALID")
    numbers = list(map(float, stats.groups())) if stats else [None] * 4
    if stats and not (all(math.isfinite(x) for x in numbers)
                      and 0 <= numbers[0] <= numbers[1] <= numbers[2] and numbers[3] >= 0):
        raise ValueError("PING_RTT_INVALID")
    if (rc == 0) != (received > 0) and sent == expected:
        # Con deadline, ping puede devolver 1 si no recibe todos los paquetes.
        if not (rc == 1 and received < sent):
            raise ValueError("PING_RETURN_CODE_INVALID")
    return {"status": "OK" if sent == received == expected else "PARTIAL" if received else "NO_REPLY",
            "sent": sent, "received": received, "loss_pct": loss,
            "rtt_min_ms": numbers[0], "rtt_avg_ms": numbers[1],
            "rtt_max_ms": numbers[2], "rtt_mdev_ms": numbers[3],
            "rtt_p95_ms": percentile([x["rtt_ms"] for x in samples]), "samples": samples}


def parse_trace(raw, destination, maximum, rc):
    if rc != 0:
        raise ValueError("TRACE_OUTPUT_INVALID")
    hops = []
    for line in raw.splitlines():
        match = re.match(r"^\s*(\d+)\s+(.+)$", line)
        if not match:
            continue
        number, rest = int(match[1]), match[2].strip()
        if number != len(hops) + 1 or number > maximum:
            raise ValueError("TRACE_HOP_INVALID")
        if rest == "*":
            hops.append({"hop": number, "address": None, "rtt_ms": None, "annotation": None})
            continue
        row = re.fullmatch(r"(\d+\.\d+\.\d+\.\d+)\s+([\d.]+)\s+ms(?:\s+(!\S*))?", rest)
        if not row:
            raise ValueError("TRACE_HOP_INVALID")
        address = str(ipaddress.IPv4Address(row[1]))
        rtt = float(row[2])
        if not math.isfinite(rtt):
            raise ValueError("TRACE_HOP_INVALID")
        hops.append({"hop": number, "address": address, "rtt_ms": rtt, "annotation": row[3]})
    if not hops:
        raise ValueError("TRACE_NO_HOPS")
    reached = hops[-1]["address"] == destination and hops[-1]["annotation"] is None
    return {"status": "OK" if reached else "NOT_REACHED", "reached": reached, "hops": hops}


def parse_http(raw, rc):
    match = re.search(r"\nHTTP_STATUS=(\d{3})\nHTTP_TOTAL_S=([\d.]+)\n?$", raw)
    if rc != 0 or not match:
        raise ValueError("HTTP_TRANSPORT_ERROR")
    code, elapsed = int(match[1]), float(match[2])
    if not (100 <= code <= 599 and math.isfinite(elapsed) and elapsed >= 0):
        raise ValueError("HTTP_OUTPUT_INVALID")
    result = {"status": "HTTP_ERROR", "http_status": code, "elapsed_ms": round(elapsed * 1000, 3),
              "active_backend": None, "active_site": None, "selected_path": None,
              "availability": None, "backend_status": None}
    if code == 200:
        data = json.loads(raw[:match.start()])
        if not isinstance(data, dict) or data.get("id") != "FRONTAL_HQ" or data.get("service") != "netlab360-s05-ha":
            raise ValueError("HTTP_IDENTITY_INVALID")
        for key in ("active_backend", "active_site", "selected_path", "backend_status"):
            value = data.get(key)
            if value is not None and (not isinstance(value, str) or len(value) > 80):
                raise ValueError("HTTP_FIELD_INVALID")
            result[key] = value
        result["availability"] = data.get("status") if data.get("status") in ("available", "unavailable") else None
        result["status"] = "OK" if result["availability"] == "available" and result["backend_status"] == "healthy" else "SERVICE_UNAVAILABLE"
    return result


def execute(action, route, runner=invoke):
    """Devolver transporte y resultado por separado; no confundir error con pérdida."""
    src, dst, profile, args = command(action, route)
    result = {"schema": "NETLAB360_S08_PROBE_V1", "action": action, "route": route,
              "origin": src.address, "destination": dst.address,
              "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "transport": "ERROR", "measurement": None, "error": None}
    start = time.monotonic()
    try:
        verify_identity(src, dst, runner)
        response = runner(src.namespace, args, profile.timeout_s)
        if response.returncode in (124, 137):
            result["transport"] = "TIMEOUT"
        else:
            if action.startswith("test.ping."):
                measured = parse_ping(response.stdout, profile.packets, response.returncode)
            elif action == "test.traceroute":
                measured = parse_trace(response.stdout, dst.address, profile.hops, response.returncode)
            else:
                measured = parse_http(response.stdout, response.returncode)
            result.update(transport="OK", measurement=measured)
    except subprocess.TimeoutExpired:
        result["transport"] = "TIMEOUT"
    except (ValueError, OSError, KeyError, TypeError) as exc:
        result["error"] = str(exc) if re.fullmatch(r"[A-Z_]+", str(exc)) else "INVALID_OR_UNAVAILABLE_OUTPUT"
    result["duration_ms"] = round((time.monotonic() - start) * 1000, 3)
    return result


def main():
    """CLI de operador local; no instalar permisos sudo ni exponer a FastAPI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", required=True, choices=ACTIONS)
    parser.add_argument("--route", required=True, choices=("HQ_A_S1", "HQ_A_S2", "S2_A_FRONTAL_HQ"))
    args = parser.parse_args()
    command(args.action, args.route)
    if os.geteuid() == 0:
        parser.error("Ejecutar como operador no root con sudo previamente autorizado")
    # Exclusión de ejecuciones de este operador; el gestor futuro impondrá el límite global.
    parent = Path.home() / "netlab360-bootstrap/s08"
    fd = os.open(parent / "probe-manual.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "rb+") as lock:
        info = os.fstat(lock.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
            parser.error("Archivo de exclusión no seguro")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("Otra prueba manual está activa")
        result = execute(args.action, args.route)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0 if result["transport"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
