"""Transferencias manuales iPerf3 con perfiles cerrados y receptor temporal."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import math
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import time

from .probe_catalog import IPERF_PORT, resolve
from .probe_executor import ENV, invoke, verify_identity

ROUTES = ("HQ_A_S1", "HQ_A_S2")
PROFILES = {
    "tcp-10s": ("TCP", 10, 0, 20_000_000, 20, 25),
    "udp-10s": ("UDP", 10, 0, 20_000_000, 20, 25),
    "tcp-100mb": ("TCP", 0, 100_000_000, 20_000_000, 60, 70),
    "tcp-500mb": ("TCP", 0, 500_000_000, 100_000_000, 65, 75),
    "tcp-1gb": ("TCP", 0, 1_000_000_000, 100_000_000, 115, 125),
    "tcp-2gb": ("TCP", 0, 2_000_000_000, 100_000_000, 220, 230),
    "tcp-5gb": ("TCP", 0, 5_000_000_000, 100_000_000, 520, 530),
}
MAX_JSON = 2_000_000


def commands(profile, route):
    """Seleccionar exclusivamente perfiles enumerados y endpoints verificados."""
    if type(profile) is not str or type(route) is not str or profile not in PROFILES or route not in ROUTES:
        raise ValueError("INVALID_TRANSFER_SELECTION")
    protocol, seconds, volume, bitrate, client_timeout, server_timeout = PROFILES[profile]
    src, dst, limits = resolve("test.iperf." + protocol.lower(), route)
    # Los perfiles extendidos son exclusivamente TCP por volumen y tasa objetivo fija.
    if bitrate != limits.bitrate_bps and not (protocol == "TCP" and volume >= 500_000_000 and bitrate == 100_000_000):
        raise ValueError("INVALID_TRANSFER_RATE")
    interval = "10" if volume >= 1_000_000_000 else "1"
    server = ["/usr/bin/iperf3", "-s", "-1", "-B", dst.address, "-p", str(IPERF_PORT), "-i", interval, "-J"]
    client = ["/usr/bin/iperf3", "-c", dst.address, "-B", src.address,
              "-p", str(IPERF_PORT), "-b", str(bitrate), "-P", "1", "-i", interval,
              "--connect-timeout", "2000", "-J"]
    if volume:
        client += ["-n", str(volume), "-l", "10000"]
    else:
        client += ["-t", str(seconds)]
    if protocol == "UDP":
        client += ["-u", "-l", "1200"]
    return src, dst, server, client, client_timeout, server_timeout


def number(value):
    """Rechazar valores ausentes, no finitos, booleanos o negativos."""
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("INVALID_NUMERIC_METRIC")
    return value


def count(value):
    if type(value) is not int or value < 0:
        raise ValueError("INVALID_COUNT")
    return value


def intervals(document):
    """Conservar los intervalos observados de cada extremo por separado."""
    rows = document["intervals"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 80:
        raise ValueError("INVALID_INTERVAL_COUNT")
    result = []
    previous = 0
    for row in rows:
        sample = row["sum"]
        start, end = number(sample["start"]), number(sample["end"])
        if end <= start or start + 0.02 < previous:
            raise ValueError("INVALID_INTERVAL_TIME")
        previous = end
        result.append({"start_s": start, "end_s": end, "bytes": count(sample["bytes"]),
                       "mbps": round(number(sample["bits_per_second"]) / 1_000_000, 3)})
    return result


def parse_results(profile, route, sender, receiver):
    """Normalizar métricas finales, sin confundir pérdida UDP con retransmisión TCP."""
    src, dst, _, _, _, _ = commands(profile, route)
    protocol, seconds, volume, bitrate, _, _ = PROFILES[profile]
    for doc, local, remote in ((sender, src.address, dst.address),
                               (receiver, dst.address, src.address)):
        if not isinstance(doc, dict) or doc.get("error"):
            raise ValueError("IPERF_REPORTED_ERROR")
        if doc["start"]["test_start"]["protocol"] != protocol:
            raise ValueError("PROTOCOL_MISMATCH")
        connections = doc["start"]["connected"]
        if len(connections) != 1 or connections[0]["local_host"] != local or connections[0]["remote_host"] != remote:
            raise ValueError("ENDPOINT_MISMATCH")
    sent = sender["end"]["sum_sent"]
    reported_rx = sender["end"]["sum_received"]
    received = receiver["end"]["sum_received"]
    tx, rx = count(sent["bytes"]), count(received["bytes"])
    if count(reported_rx["bytes"]) != rx:
        raise ValueError("RECEIVER_SUMMARIES_MISMATCH")
    duration = number(received["seconds"])
    if duration <= 0:
        raise ValueError("INVALID_DURATION")
    tx_intervals, rx_intervals = intervals(sender), intervals(receiver)
    result = {
        "protocol": protocol, "target_bytes": volume or None,
        "target_duration_s": seconds or None, "target_bitrate_bps": bitrate,
        "bytes_sent": tx, "bytes_received": rx, "duration_s": duration,
        "sender_mbps": round(number(sent["bits_per_second"]) / 1_000_000, 3),
        "receiver_mbps": round(number(received["bits_per_second"]) / 1_000_000, 3),
        "retransmissions": None, "jitter_ms": None, "lost_packets": None, "loss_pct": None,
        "sender_intervals": tx_intervals, "receiver_intervals": rx_intervals,
        "status": "OK" if tx > 0 and rx > 0 else "INCOMPLETE",
        "content_integrity_verified": False,
    }
    # Los totales finales y las ventanas de muestreo son contadores distintos.
    # No inventamos muestras ni convertimos diferencias de intervalos en pérdidas.
    tx_interval_bytes = sum(row["bytes"] for row in tx_intervals)
    rx_interval_bytes = sum(row["bytes"] for row in rx_intervals)
    result["interval_accounting"] = {
        "status": "MATCH" if tx_interval_bytes == tx and rx_interval_bytes == rx else "DISCREPANT",
        "sender_interval_bytes": tx_interval_bytes,
        "receiver_interval_bytes": rx_interval_bytes,
        "sender_delta_bytes": tx_interval_bytes - tx,
        "receiver_delta_bytes": rx_interval_bytes - rx,
    }
    result["receiver_summary_source"] = "receiver.end.sum_received"
    result["client_reported_receiver_bytes"] = count(reported_rx["bytes"])
    if protocol == "TCP":
        result["retransmissions"] = count(sent["retransmits"])
        # -n es el objetivo de una medición iPerf3, no una garantía de tamaño exacto.
        # La exactitud estricta pertenece al ejecutor de contenido.
        if volume:
            result["volume_target_met"] = rx >= volume
            result["volume_excess_bytes"] = max(0, rx - volume)
            result["volume_shortfall_bytes"] = max(0, volume - rx)
            result["volume_status"] = "SHORT" if rx < volume else "EXACT" if rx == volume else "EXCEEDED"
        if tx != rx or (volume and rx < volume):
            result["status"] = "INCOMPLETE"
    else:
        lost, packets = count(received["lost_packets"]), count(received["packets"])
        loss = number(received["lost_percent"])
        if (count(reported_rx["lost_packets"]) != lost
                or count(reported_rx["packets"]) != packets
                or not math.isclose(number(reported_rx["lost_percent"]), loss, abs_tol=1e-9)
                or not math.isclose(number(reported_rx["jitter_ms"]), number(received["jitter_ms"]), abs_tol=1e-9)):
            raise ValueError("UDP_SUMMARIES_MISMATCH")
        if lost > packets or loss > 100 or not packets or abs(loss - 100 * lost / packets) > 0.11:
            raise ValueError("INVALID_UDP_LOSS")
        result.update(jitter_ms=number(received["jitter_ms"]), lost_packets=lost, loss_pct=loss,
                      receiver_packets=packets)
        if lost and result["status"] == "OK":
            result["status"] = "PARTIAL"
    return result


def port_free(endpoint):
    reply = invoke(endpoint.namespace, ["/usr/bin/ss", "-H", "-lntu", "sport", "=", f":{IPERF_PORT}"], 5)
    return reply.returncode == 0 and not reply.stdout.strip()


def server_argv(namespace, args, deadline):
    return ["/usr/bin/sudo", "-n", "--", "/usr/sbin/ip", "netns", "exec", namespace,
            "/usr/bin/env", "-i", "PATH=/usr/sbin:/usr/bin", "LC_ALL=C",
            "/usr/bin/timeout", "--kill-after=2", str(deadline), *args]


def read_json(handle):
    handle.seek(0)
    data = handle.read(MAX_JSON + 1)
    if len(data) > MAX_JSON:
        raise ValueError("TRANSFER_OUTPUT_LIMIT")
    return json.loads(data)


def execute(profile, route):
    """Supervisar un servidor de una conexión, con timeout independiente del cliente."""
    src, dst, server, client, client_timeout, server_timeout = commands(profile, route)
    result = {"schema": "NETLAB360_S08_TRANSFER_V1", "profile": profile, "route": route,
              "origin": src.address, "destination": dst.address,
              "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "transport": "ERROR", "measurement": None, "error": None}
    started = time.monotonic()
    try:
        verify_identity(src, dst, invoke)
        if not port_free(src) or not port_free(dst):
            raise ValueError("PORT_NOT_FREE")
        with tempfile.TemporaryFile() as server_out, tempfile.TemporaryFile() as server_err:
            process = subprocess.Popen(server_argv(dst.namespace, server, server_timeout),
                                       stdout=server_out, stderr=server_err, env=ENV)
            try:
                # No conectar un cliente de prueba al receptor de una sola sesión.
                ready = False
                for _ in range(30):
                    if process.poll() is not None:
                        break
                    probe = invoke(dst.namespace, ["/usr/bin/ss", "-H", "-ltn", "sport", "=", f":{IPERF_PORT}"], 2)
                    if probe.returncode == 0 and f"{dst.address}:{IPERF_PORT}" in probe.stdout:
                        ready = True
                        break
                    time.sleep(0.2)
                if not ready:
                    raise ValueError("RECEIVER_NOT_READY")
                reply = invoke(src.namespace, client, client_timeout)
                if reply.returncode in (124, 137):
                    raise subprocess.TimeoutExpired(client, client_timeout)
                if reply.returncode:
                    raise ValueError("SENDER_FAILED")
                if process.wait(timeout=server_timeout + 5):
                    raise ValueError("RECEIVER_FAILED")
                result["measurement"] = parse_results(profile, route, json.loads(reply.stdout),
                                                       read_json(server_out))
                result["transport"] = "OK"
            finally:
                # El timeout dentro del namespace termina incluso si el supervisor falla.
                # No usamos pkill ni terminamos servidores ajenos.
                process.wait(timeout=server_timeout + 5)
        if not port_free(dst) or not port_free(src):
            raise ValueError("PORT_NOT_RELEASED")
    except subprocess.TimeoutExpired:
        result.update(transport="TIMEOUT", measurement=None, error="TRANSFER_TIMEOUT")
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        code = str(exc)
        result.update(transport="ERROR", measurement=None,
                      error=code if code.isupper() and code.replace("_", "").isalnum()
                      else "INVALID_OR_UNAVAILABLE_OUTPUT")
    result["elapsed_ms"] = round((time.monotonic() - started) * 1000, 3)
    return result


@contextmanager
def manual_lock():
    """Compartir el bloqueo por operador con las pruebas manuales ICMP/HTTP."""
    path = Path.home() / "netlab360-bootstrap/s08/probe-manual.lock"
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "rb+") as lock:
        info = os.fstat(lock.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
            raise ValueError("UNSAFE_LOCK")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def main():
    """Ejecutar como operador local no root, sin instalar privilegios adicionales."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=tuple(PROFILES))
    parser.add_argument("--route", required=True, choices=ROUTES)
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error("No ejecutar Python del repositorio como root")
    with manual_lock():
        result = execute(args.profile, args.route)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0 if result["transport"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
