#!/usr/bin/env python3
"""Pilotos aislados de Blackbox, Alertmanager e iPerf3; sin modificar Prometheus."""
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import math
from pathlib import Path
import pwd
import re
import shutil
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
    result = sudo("/usr/bin/systemctl", "stop", unit, check=False)
    state = run(["/usr/bin/systemctl", "show", unit, "--property=ActiveState", "--value"],
                check=False).stdout.strip()
    if state not in ("inactive", "failed") or (result.returncode and state != "inactive"):
        raise RuntimeError("UNIT_STOP_UNCONFIRMED:" + unit + ":" + state)


def unit_args(unit, namespace=None, lifetime=90, root=False, icmp_raw=False):
    """Conceder capacidad ICMP solo al exporter de los contextos autorizados."""
    if icmp_raw and (root or namespace not in (
            catalog.ENDPOINTS["HQ"].namespace, catalog.ENDPOINTS["S2"].namespace)
            or not unit.endswith(("-bb-hq", "-bb-s2"))):
        raise ValueError("INVALID_ICMP_PRIVILEGE_SCOPE")
    capability = "CAP_NET_RAW" if icmp_raw else ""
    command = ["/usr/bin/sudo", "-n", "--", "/usr/bin/systemd-run", "--quiet",
               "--collect", "--unit=" + unit,
               "--property=Type=exec", "--property=NoNewPrivileges=yes",
               "--property=UMask=0077", "--property=KillMode=control-group",
               "--property=TimeoutStopSec=3", f"--property=RuntimeMaxSec={lifetime}s",
               "--property=LimitFSIZE=2097152", "--property=LimitCORE=0"]
    if not root:
        command += [f"--property=User={ACCOUNT}", f"--property=Group={ACCOUNT}",
                    "--property=CapabilityBoundingSet=" + capability,
                    "--property=AmbientCapabilities=" + capability,
                    "--property=ProtectHome=yes"]
    if namespace:
        command += ["--property=NetworkNamespacePath=/run/netns/" + namespace]
    return command


@contextmanager
def service(unit, command, namespace=None, lifetime=90, root=False, icmp_raw=False):
    """Confinar duración y retirar la unidad aunque falle una comprobación."""
    if active(unit):
        raise RuntimeError("UNIT_ALREADY_ACTIVE")
    try:
        run(unit_args(unit, namespace, lifetime, root, icmp_raw) + command)
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


def package_digest(path, metadata, name, version):
    """Validar tamaño y resumen contra el índice APT local de versión exacta."""
    if not path.is_file() or path.is_symlink():
        raise ValueError("PACKAGE_FILE")
    entries = []
    for block in metadata.split("\n\n"):
        fields = dict(line.split(": ", 1) for line in block.splitlines()
                      if not line.startswith((" ", "\t")) and ": " in line)
        if (fields.get("Package"), fields.get("Version"), fields.get("Architecture")) == (name, version, "amd64"):
            entries.append((fields.get("Size", ""), fields.get("SHA256", "")))
    unique = set(entries)
    if len(unique) != 1:
        raise ValueError("PACKAGE_APT_METADATA")
    size, expected = unique.pop()
    if not size.isdecimal() or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("PACKAGE_APT_DIGEST")
    if path.stat().st_size != int(size):
        raise ValueError("PACKAGE_SIZE")
    with path.open("rb") as handle:
        actual = hashlib.file_digest(handle, "sha256").hexdigest()
    if actual != expected:
        raise ValueError("PACKAGE_DIGEST")
    return actual


def package(stage, name, version, binary_names, cache=None):
    """Reutilizar un paquete verificado o descargar por APT sin instalar."""
    target = stage / name
    target.mkdir(mode=0o755)
    target.chmod(0o755)
    metadata = run(["/usr/bin/apt-cache", "show", f"{name}={version}"]).stdout
    if cache is None:
        run(["/usr/bin/apt-get", "download", f"{name}={version}"], timeout=120, cwd=target)
    else:
        source = cache / name
        if source.is_symlink() or not source.is_dir():
            raise ValueError("PACKAGE_CACHE_DIRECTORY")
        candidates = list(source.glob("*.deb"))
        if len(candidates) != 1:
            raise ValueError("PACKAGE_CACHE_COUNT")
        package_digest(candidates[0], metadata, name, version)
        shutil.copyfile(candidates[0], target / candidates[0].name)
        print("PAQUETE_REUTILIZADO=" + name, flush=True)
    debs = list(target.glob("*.deb"))
    if len(debs) != 1:
        raise ValueError("PACKAGE_COUNT")
    deb = debs[0]
    package_digest(deb, metadata, name, version)
    print("PAQUETE_INTEGRIDAD_APT=OK:" + name, flush=True)
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
    for folder in (extracted, extracted / "usr", extracted / "usr/bin"):
        folder.chmod(0o755)
    binary.chmod(0o755)
    print("PAQUETE_EXTRAIDO=" + name + "=" + version, flush=True)
    version_result = run([str(binary), "--version"])
    print((version_result.stdout + version_result.stderr).strip(), flush=True)
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


def verify_blackbox_privileges(unit, namespace, worker, icmp_raw):
    """Comprobar la identidad efectiva, namespace y capacidades del proceso real."""
    pid = int(run(["/usr/bin/systemctl", "show", unit, "--property=MainPID", "--value"]).stdout)
    if pid <= 1:
        raise ValueError("BLACKBOX_PID")
    status = sudo("/usr/bin/cat", f"/proc/{pid}/status").stdout
    fields = dict(line.split(":", 1) for line in status.splitlines() if ":" in line)
    for key, expected in (("Uid", worker.pw_uid), ("Gid", worker.pw_gid)):
        if [int(x) for x in fields[key].split()] != [expected] * 4:
            raise PermissionError("BLACKBOX_IDENTITY:" + key)
    if any(int(x) != worker.pw_gid for x in fields["Groups"].split()):
        raise PermissionError("BLACKBOX_SUPPLEMENTARY_GROUPS")
    expected = 1 << 13 if icmp_raw else 0
    for key in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"):
        if int(fields[key].strip(), 16) != expected:
            raise PermissionError("BLACKBOX_CAPABILITY:" + key)
    if fields["NoNewPrivs"].strip() != "1":
        raise PermissionError("BLACKBOX_NO_NEW_PRIVILEGES")
    actual = sudo("/usr/bin/stat", "-Lc", "%d:%i", f"/proc/{pid}/ns/net").stdout.strip()
    target = sudo("/usr/bin/stat", "-Lc", "%d:%i", "/run/netns/" + namespace).stdout.strip()
    if actual != target:
        raise PermissionError("BLACKBOX_NAMESPACE")
    print(f"BLACKBOX_PRIVILEGIOS={unit} UID={worker.pw_uid} GID={worker.pw_gid} CAP={expected:016x} NNP=1",
          flush=True)
    return {"uid": worker.pw_uid, "gid": worker.pw_gid,
            "capability": "CAP_NET_RAW" if icmp_raw else "NONE",
            "no_new_privileges": True, "namespace_verified": True}


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
        # Un rango vacío impide ping sockets sin privilegios. No modificar sysctl.
        icmp_raw = not low <= worker.pw_gid <= high
        print("ICMP_MODO=" + origin + ":" + ("CAP_NET_RAW" if icmp_raw else "PING_GROUP"),
              flush=True)
        unit = prefix + "-bb-" + origin.lower()
        with service(unit, [str(binary), "--config.file=" + str(config),
                            "--web.listen-address=127.0.0.1:9115"], namespace, icmp_raw=icmp_raw):
            wait_for(lambda: active(unit) and not free(namespace, 9115))
            privileges = verify_blackbox_privileges(unit, namespace, worker, icmp_raw)
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
                row = dict(item, success=success, duration_s=duration,
                           privileges=privileges)
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
        if netns(namespace, "/usr/sbin/sysctl", "-n", "net.ipv4.ping_group_range").stdout.split() != ping_range:
            raise RuntimeError("ICMP_GROUP_RANGE_CHANGED:" + origin)
        print("ICMP_GROUP_RANGE_INTACTO=" + origin, flush=True)
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


def alertmanager_template_args(binary):
    """Usar la plantilla original del paquete extraído, no rutas globales del host."""
    root = binary.parent.parent / "share/prometheus/alertmanager"
    template = root / "default.tmpl"
    if not template.is_file() or template.is_symlink() or not template.stat().st_size:
        raise ValueError("ALERTMANAGER_TEMPLATE_MISSING:" + str(template))
    help_result = run([str(binary), "--help"])
    help_text = help_result.stdout + help_result.stderr
    if not re.search(r"--template\.default(?:[=\s]|$)", help_text):
        raise ValueError("ALERTMANAGER_TEMPLATE_FLAG_UNAVAILABLE")
    print("ALERTMANAGER_PLANTILLA_LOCAL=" + str(template), flush=True)
    return ["--template.default=" + str(template)]


def alertmanager(stage, evidence, prefix, binary):
    """Validar webhook local agrupado y resuelto con alertas sintéticas explícitas."""
    if not free(None, 9093) or not free(None, 9193):
        raise RuntimeError("ALERTMANAGER_PILOT_PORT_BUSY")
    template_args = alertmanager_template_args(binary)
    received = []
    guard = threading.Lock()

    class Receiver(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            size = int(self.headers.get("Content-Length", "0"))
            self.connection.settimeout(5)
            if self.path != "/receive" or not 0 < size <= 65536:
                self.send_error(400)
                return
            body = json.loads(self.rfile.read(size))
            with guard:
                if len(received) >= 16:
                    self.send_error(429)
                    return
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
                         "--cluster.listen-address=", *template_args], lifetime=90):
                def ready():
                    if not active(prefix + "-am"):
                        raise RuntimeError("ALERTMANAGER_EXITED_BEFORE_READY")
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


def stream_args(args):
    """Mantener exclusivamente NDJSON; full-output agrega un documento final multilínea."""
    return [x for x in args if x not in ("-J", "--json", "--json-stream-full-output",
                                         "--json-stream", "--forceflush")] + [
        "--json-stream", "--forceflush"]


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
                    args = stream_args(args)
                    out = path.open("xb")
                    err = path.with_suffix(".stderr").open("xb")
                    handles.extend((out, err))
                    process = subprocess.Popen(unit_args(unit, endpoint.namespace, seconds + 5)
                                               + ["--wait", "--pipe", *args],
                                               stdin=subprocess.DEVNULL, stdout=out, stderr=err)
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
    parser.add_argument("--only", choices=("all", "blackbox", "alertmanager", "iperf"),
                        default="all", help="Reanudar solo un piloto pendiente")
    parser.add_argument("--package-cache", type=Path,
                        help="Entorno anterior con archivos deb completos; verificar contra APT")
    args = parser.parse_args()
    cache = args.package_cache
    if cache is not None and (cache.is_symlink() or not cache.is_dir()):
        raise ValueError("PACKAGE_CACHE_DIRECTORY")
    evidence = args.evidence.resolve()
    evidence.mkdir(mode=0o700)
    stage = Path(tempfile.mkdtemp(prefix="netlab360-s08-observe."))
    stage.chmod(0o755)
    prefix = "netlab360-s08-pilot-" + stage.name.split(".")[-1].lower()
    print("ENTORNO_PILOTO=" + str(stage), flush=True)
    completed = False
    try:
        if args.only in ("all", "blackbox"):
            bb = package(stage, "prometheus-blackbox-exporter", "0.26.0-2",
                         ("prometheus-blackbox-exporter", "blackbox_exporter"), cache)
            blackbox(stage, evidence, prefix, bb)
        if args.only in ("all", "alertmanager"):
            am = package(stage, "prometheus-alertmanager", "0.28.1+ds-3",
                         ("prometheus-alertmanager", "alertmanager"), cache)
            alertmanager(stage, evidence, prefix, am)
        if args.only in ("all", "iperf"):
            iperf(evidence, prefix)
        completed = True
    finally:
        units = [prefix + suffix for suffix in
                 ("-bb-hq", "-bb-s2", "-am", "-tcp-10s-rx", "-tcp-10s-tx",
                  "-udp-10s-rx", "-udp-10s-tx", "-lock")]
        if any(active(unit) for unit in units):
            raise RuntimeError("PILOT_CLEANUP_UNCONFIRMED:" + str(stage))
        if completed:
            # Retirar solo el estado sintético de este piloto una vez comprobadas las unidades.
            state = stage / "alert-state"
            if state.exists():
                run(["/usr/bin/sudo", "-n", "-u", ACCOUNT, "--", "/usr/bin/find",
                     str(state), "-mindepth", "1", "-delete"])
                state.rmdir()
            shutil.rmtree(stage)
            print("ENTORNO_PILOTO_ELIMINADO=OK", flush=True)
            print("S08_008_PILOTO=" + args.only + ":OK", flush=True)
        else:
            print("ENTORNO_PILOTO_CONSERVADO=" + str(stage), flush=True)
            for unit in units:
                log = sudo("/usr/bin/journalctl", "-u", unit, "--no-pager", "-n", "60", check=False)
                (evidence / (unit + ".log")).write_text(log.stdout, encoding="utf-8")


if __name__ == "__main__":
    main()
