#!/usr/bin/env python3
"""Pilotos aislados de Blackbox, Alertmanager e iPerf3; sin modificar Prometheus."""
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import pwd
import re
import subprocess
import sys
import tempfile
import threading
import time
from urllib.request import Request, ProxyHandler, build_opener

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "servicios/consola-s08"))
from api import slo_contract as slo, probe_catalog as catalog, probe_executor, transfer_executor

ACCOUNT = "netlab360-s08-worker"
OPEN = build_opener(ProxyHandler({}))
MAX_OUTPUT = 2_000_000
LOCK = "/run/netlab360-s08-broker/active.lock"


def run(args, timeout=20, check=True, cwd=None):
    """Ejecutar una lista fija de argumentos sin shell."""
    return subprocess.run(args, cwd=cwd, check=check, timeout=timeout,
                          capture_output=True, text=True)


def sudo(*args, **kwargs):
    return run(["/usr/bin/sudo", "-n", "--", *args], **kwargs)


def netns(namespace, *args, **kwargs):
    return sudo("/usr/sbin/ip", "netns", "exec", namespace, *args, **kwargs)


def write(path, data):
    """Conservar evidencia sin reemplazar registros previos."""
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def free(namespace, port):
    args = ["/usr/bin/ss", "-H", "-lntu", "sport", "=", f":{port}"]
    result = netns(namespace, *args) if namespace else run(args)
    return not result.stdout.strip()


def active(unit):
    return run(["/usr/bin/systemctl", "is-active", "--quiet", unit],
               check=False).returncode == 0


def stop(unit):
    """Detener únicamente una unidad creada por este piloto."""
    sudo("/usr/bin/systemctl", "stop", unit, check=False)
    if active(unit):
        raise RuntimeError("UNIT_STILL_ACTIVE:" + unit)


def unit_args(unit, namespace=None, lifetime=90, root=False):
    command = ["/usr/bin/sudo", "-n", "--", "/usr/bin/systemd-run", "--quiet",
               "--collect", "--unit=" + unit,
               "--property=Type=exec", "--property=NoNewPrivileges=yes",
               "--property=UMask=0077", "--property=KillMode=control-group",
               "--property=TimeoutStopSec=3", f"--property=RuntimeMaxSec={lifetime}s",
               "--property=LimitFSIZE=2097152", "--property=LimitCORE=0"]
    if not root:
        command += [f"--property=User={ACCOUNT}", f"--property=Group={ACCOUNT}",
                    "--property=CapabilityBoundingSet=", "--property=AmbientCapabilities=",
                    "--property=ProtectHome=yes"]
    if namespace:
        command += ["--property=NetworkNamespacePath=/run/netns/" + namespace]
    return command


@contextmanager
def service(unit, command, namespace=None, lifetime=90, root=False):
    """Confinar duración y retirar la unidad aunque falle una comprobación."""
    if active(unit):
        raise RuntimeError("UNIT_ALREADY_ACTIVE")
    try:
        run(unit_args(unit, namespace, lifetime, root) + command)
        yield
    finally:
        stop(unit)


def wait_for(predicate, seconds=10):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.2)
    raise TimeoutError("PILOT_WAIT_TIMEOUT")


def package(stage, name, version, binary_names):
    """Descargar por APT y extraer sin instalar ni iniciar unidades del paquete."""
    target = stage / name
    target.mkdir(mode=0o755)
    target.chmod(0o755)
    run(["/usr/bin/apt-get", "download", f"{name}={version}"], timeout=120, cwd=target)
    debs = list(target.glob("*.deb"))
    if len(debs) != 1:
        raise ValueError("PACKAGE_COUNT")
    deb = debs[0]
    for field, expected in (("Package", name), ("Version", version), ("Architecture", "amd64")):
        if run(["/usr/bin/dpkg-deb", "-f", str(deb), field]).stdout.strip() != expected:
            raise ValueError("PACKAGE_METADATA:" + field)
    extracted = target / "extract"
    run(["/usr/bin/dpkg-deb", "-x", str(deb), str(extracted)])
    matches = [extracted / "usr/bin" / item for item in binary_names
               if (extracted / "usr/bin" / item).is_file()]
    if len(matches) != 1:
        raise ValueError("PACKAGE_BINARY")
    binary = matches[0]
    print("PAQUETE_EXTRAIDO=" + name + "=" + version, flush=True)
    print(run([str(binary), "--version"]).stdout.strip(), flush=True)
    return binary


def metric(raw, name):
    """Aceptar una sola métrica escalar finita del exporter."""
    rows = re.findall(r"^" + re.escape(name) + r" ([^\s]+)$", raw, re.M)
    if len(rows) != 1:
        raise ValueError("BLACKBOX_METRIC:" + name)
    value = float(rows[0])
    if not math.isfinite(value):
        raise ValueError("BLACKBOX_NONFINITE")
    return value


def blackbox(stage, evidence, prefix, binary):
    config = stage / "blackbox.yml"
    config.write_bytes((REPO / "servicios/observabilidad/blackbox/s08-blackbox.yml").read_bytes())
    config.chmod(0o644)
    worker = pwd.getpwnam(ACCOUNT)
    rows = []
    for origin in ("HQ", "S2"):
        namespace = catalog.ENDPOINTS[origin].namespace
        if not free(namespace, 9115):
            raise RuntimeError("BLACKBOX_PORT_BUSY")
        ping_range = netns(namespace, "/usr/sbin/sysctl", "-n", "net.ipv4.ping_group_range").stdout.split()
        low, high = map(int, ping_range)
        print(f"ICMP_GROUP_RANGE={origin}:{low}:{high}:GID={worker.pw_gid}", flush=True)
        if not low <= worker.pw_gid <= high:
            raise PermissionError("ICMP_GROUP_NOT_ALLOWED:" + origin)
        unit = prefix + "-bb-" + origin.lower()
        with service(unit, [str(binary), "--config.file=" + str(config),
                            "--web.listen-address=127.0.0.1:9115"], namespace):
            wait_for(lambda: active(unit) and not free(namespace, 9115))
            for identifier in slo.PROBES:
                item = slo.probe(identifier)
                if item["origin"] != origin:
                    continue
                route = catalog.ROUTES[item["route"]]
                probe_executor.verify_identity(catalog.ENDPOINTS[route.origin],
                                               catalog.ENDPOINTS[route.destination],
                                               probe_executor.invoke)
                raw = netns(namespace, "/usr/bin/curl", "--noproxy", "*", "-fsS",
                            "--max-time", "6", "--get", "--data-urlencode",
                            "module=" + item["module"], "--data-urlencode",
                            "target=" + item["target"], "http://127.0.0.1:9115/probe").stdout
                (evidence / (identifier + ".prom")).write_text(raw, encoding="utf-8")
                success = metric(raw, "probe_success")
                duration = metric(raw, "probe_duration_seconds")
                row = dict(item, success=success, duration_s=duration)
                if item["module"] == "http_service":
                    row["http_status"] = metric(raw, "probe_http_status_code")
                    if row["http_status"] != 200:
                        raise ValueError("BLACKBOX_HTTP_STATUS")
                if success != 1 or not 0 <= duration <= 3.1:
                    raise ValueError("BLACKBOX_PROBE_FAILED:" + identifier)
                rows.append(row)
                print(f"SONDA={identifier} EXITO={success:.0f} DURACION_S={duration:.6f}", flush=True)
        if not free(namespace, 9115):
            raise RuntimeError("BLACKBOX_PORT_NOT_RELEASED")
    if len(rows) != len(slo.PROBES):
        raise ValueError("BLACKBOX_CATALOG_INCOMPLETE")
    write(evidence / "sondas.json", {"source": "BLACKBOX_REAL", "probes": rows})
    print("SONDAS_REALES=5/5 CONTEXTOS=2/2", flush=True)


def http_json(port, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(f"http://127.0.0.1:{port}{path}", data=data,
                      headers={"Content-Type": "application/json"})
    with OPEN.open(request, timeout=5) as response:
        raw = response.read(MAX_OUTPUT + 1)
        if len(raw) > MAX_OUTPUT:
            raise ValueError("HTTP_OUTPUT_LIMIT")
        return json.loads(raw) if raw else None


def alertmanager(stage, evidence, prefix, binary):
    """Validar webhook local agrupado y resuelto con alertas sintéticas explícitas."""
    if not free(None, 9093) or not free(None, 9193):
        raise RuntimeError("ALERTMANAGER_PILOT_PORT_BUSY")
    received = []
    guard = threading.Lock()

    class Receiver(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            size = int(self.headers.get("Content-Length", "0"))
            if self.path != "/receive" or not 0 < size <= MAX_OUTPUT:
                self.send_error(400)
                return
            body = json.loads(self.rfile.read(size))
            with guard:
                received.append(body)
            self.send_response(200)
            self.end_headers()

    config = stage / "alertmanager.yml"
    config.write_bytes((REPO / "servicios/observabilidad/alertmanager/s08-piloto.yml").read_bytes())
    config.chmod(0o644)
    state = stage / "alert-state"
    sudo("/usr/bin/install", "-d", "-o", ACCOUNT, "-g", ACCOUNT, "-m", "0700", str(state))
    with ThreadingHTTPServer(("127.0.0.1", 9193), Receiver) as listener:
        thread = threading.Thread(target=listener.serve_forever, daemon=True)
        thread.start()
        try:
            with service(prefix + "-am", [str(binary), "--config.file=" + str(config),
                         "--storage.path=" + str(state), "--web.listen-address=127.0.0.1:9093",
                         "--cluster.listen-address="], lifetime=90):
                def ready():
                    try:
                        status = http_json(9093, "/api/v2/status")
                        return isinstance(status, dict)
                    except OSError:
                        return False
                wait_for(ready)
                now = datetime.now(timezone.utc)
                alerts = [{"labels": {"alertname": "NETLAB360S08SyntheticPilot",
                                       "laboratory": "netlab360-pilot", "instance": instance,
                                       "synthetic": "true"},
                           "annotations": {"summary": "Piloto sintético, no incidente de red"},
                           "startsAt": (now - timedelta(seconds=2)).isoformat(),
                           "endsAt": (now + timedelta(minutes=2)).isoformat()}
                          for instance in ("pilot-a", "pilot-b")]
                http_json(9093, "/api/v2/alerts", alerts)

                def grouped(status):
                    with guard:
                        for message in received:
                            if (message.get("status") == status and
                                {a.get("labels", {}).get("instance") for a in message.get("alerts", [])}
                                    == {"pilot-a", "pilot-b"} and
                                all(a["labels"].get("synthetic") == "true"
                                    and a.get("status") == status for a in message["alerts"])):
                                return True
                    return False

                wait_for(lambda: grouped("firing"), 20)
                print("ALERTAS_SINTETICAS_AGRUPADAS=2/2", flush=True)
                ended = datetime.now(timezone.utc).isoformat()
                http_json(9093, "/api/v2/alerts", [dict(a, endsAt=ended) for a in alerts])
                wait_for(lambda: grouped("resolved"), 25)
                print("ALERTAS_SINTETICAS_RESUELTAS=2/2", flush=True)
        finally:
            listener.shutdown()
            thread.join(5)
            write(evidence / "alertmanager-webhook.json",
                  {"source": "SYNTHETIC_ALERT_DELIVERY_REAL", "notifications": received})
    if not free(None, 9093) or not free(None, 9193):
        raise RuntimeError("ALERTMANAGER_PORT_NOT_RELEASED")


def events(path, partial=False):
    """Leer tramas reales; no inferir resultados de un formato todavía no integrado."""
    raw = path.read_bytes()
    if len(raw) > MAX_OUTPUT:
        raise ValueError("IPERF_STREAM_LIMIT")
    lines = raw.splitlines()
    if partial and not raw.endswith(b"\n"):
        lines = lines[:-1]
    rows = [json.loads(line) for line in lines if line.strip()]
    if any(type(row) is not dict or type(row.get("event")) is not str for row in rows):
        raise ValueError("IPERF_STREAM_FRAME")
    return rows


def iperf(evidence, prefix):
    """Capturar ambos extremos de TCP y UDP en el formato nativo de iPerf3."""
    if not all(free(catalog.ENDPOINTS[name].namespace, 5201) for name in ("HQ", "S1", "S2")):
        raise RuntimeError("IPERF_PORT_BUSY")
    if sudo("/usr/bin/flock", "-n", LOCK, "/usr/bin/true", check=False).returncode:
        raise RuntimeError("BROKER_BUSY")
    with service(prefix + "-lock", ["/usr/bin/flock", "-n", LOCK, "/usr/bin/sleep", "90"],
                 lifetime=95, root=True):
        wait_for(lambda: active(prefix + "-lock") and
                 sudo("/usr/bin/flock", "-n", LOCK, "/usr/bin/true", check=False).returncode == 1)
        summaries = []
        for profile, route in (("tcp-10s", "HQ_A_S1"), ("udp-10s", "HQ_A_S2")):
            src, dst, server, client, ct, st = transfer_executor.commands(profile, route)
            probe_executor.verify_identity(src, dst, probe_executor.invoke)
            units = (prefix + "-" + profile + "-rx", prefix + "-" + profile + "-tx")
            paths = [evidence / (profile + "-" + role + ".jsonl") for role in ("rx", "tx")]
            processes = []
            handles = []
            try:
                for unit, endpoint, args, seconds, path in zip(
                        units, (dst, src), (server, client), (st, ct), paths):
                    if endpoint == src:
                        wait_for(lambda: not free(dst.namespace, 5201))
                    args = [x for x in args if x != "-J"] + [
                        "--json-stream", "--json-stream-full-output", "--forceflush"]
                    out = path.open("xb")
                    err = path.with_suffix(".stderr").open("xb")
                    handles.extend((out, err))
                    process = subprocess.Popen(unit_args(unit, endpoint.namespace, seconds + 5)
                                               + ["--wait", "--pipe", *args],
                                               stdout=out, stderr=err)
                    processes.append(process)
                observed = [False, False]
                deadline = time.monotonic() + ct + 10
                while processes[1].poll() is None:
                    for index, path in enumerate(paths):
                        observed[index] |= any(row["event"] == "interval" for row in events(path, partial=True))
                    if time.monotonic() >= deadline:
                        raise TimeoutError("IPERF_STREAM_TIMEOUT")
                    time.sleep(0.2)
                if any(process.wait(timeout=10) != 0 for process in processes):
                    raise RuntimeError("IPERF_STREAM_PROCESS_FAILED")
                for role, path, live in zip(("receiver", "sender"), paths, observed):
                    rows = events(path)
                    counts = Counter(row["event"] for row in rows)
                    if not live or any(not counts[name] for name in ("start", "interval", "end")):
                        raise ValueError("IPERF_STREAM_NOT_OBSERVED:" + role)
                    summaries.append({"profile": profile, "route": route, "role": role,
                                      "events": dict(counts), "live_interval": live,
                                      "data_keys": {row["event"]: sorted(row["data"])
                                                    for row in rows if isinstance(row.get("data"), dict)}})
                    print(f"IPERF_STREAM={profile}/{role} INTERVALOS={counts['interval']} EN_VIVO=SI",
                          flush=True)
            finally:
                try:
                    for unit in reversed(units):
                        stop(unit)
                    for process in processes:
                        process.wait(timeout=10)
                finally:
                    for handle in handles:
                        handle.close()
            if not free(dst.namespace, 5201) or not free(src.namespace, 5201):
                raise RuntimeError("IPERF_STREAM_PORT_NOT_RELEASED")
        write(evidence / "iperf-stream.json", {"source": "IPERF_NATIVE_STREAM", "streams": summaries})
    if sudo("/usr/bin/flock", "-n", LOCK, "/usr/bin/true", check=False).returncode:
        raise RuntimeError("BROKER_LOCK_NOT_RELEASED")
    print("IPERF_STREAM_REAL=4/4", flush=True)


def main():
    """Ejecutar pilotos delimitados y preservar datos originales incluso si fallan."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(mode=0o700)
    stage = Path(tempfile.mkdtemp(prefix="netlab360-s08-observe."))
    stage.chmod(0o755)
    prefix = "netlab360-s08-pilot-" + stage.name.split(".")[-1].lower()
    print("ENTORNO_PILOTO=" + str(stage), flush=True)
    try:
        bb = package(stage, "prometheus-blackbox-exporter", "0.26.0-2",
                     ("prometheus-blackbox-exporter", "blackbox_exporter"))
        am = package(stage, "prometheus-alertmanager", "0.28.1+ds-3",
                     ("prometheus-alertmanager", "alertmanager"))
        blackbox(stage, evidence, prefix, bb)
        alertmanager(stage, evidence, prefix, am)
        iperf(evidence, prefix)
        print("S08_008_PILOTOS=OK", flush=True)
    finally:
        # La unidad de Alertmanager ya se detuvo; limpiar solo su estado sintético.
        state = stage / "alert-state"
        if state.exists():
            sudo("/usr/bin/sudo", "-n", "-u", ACCOUNT, "/usr/bin/find",
                 str(state), "-mindepth", "1", "-delete")
            state.rmdir()
        import shutil
        shutil.rmtree(stage)
        print("ENTORNO_PILOTO_ELIMINADO=OK", flush=True)


if __name__ == "__main__":
    main()
