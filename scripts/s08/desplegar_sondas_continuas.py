#!/usr/bin/env python3
"""Activar adquisición continua S08 y recargar Prometheus sin sustituir TSDB."""
import hashlib
import json
import os
from pathlib import Path
import pwd
import runpy
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlencode
from urllib.request import ProxyHandler, build_opener

REPO = Path(__file__).resolve().parents[2]
PILOT = runpy.run_path(str(REPO / "scripts/s08/piloto_sondas_y_stream.py"))
S = PILOT["slo"]
C = PILOT["catalog"]
run, sudo, free = (PILOT[key] for key in ("run", "sudo", "free"))
ACCOUNT = PILOT["ACCOUNT"]
INSTALL = Path("/usr/local/libexec/netlab360/s08-observacion")
RUNTIME = Path("/run/netlab360-s08-observacion")
HOME = Path.home()
CONFIG = HOME / "netlab360-bootstrap/s06/recuperacion-prometheus-20261122_232957/prometheus-runtime.yml"
PROMTOOL = HOME / "netlab360-bootstrap/prometheus/bin/promtool"
CACHE = HOME / "netlab360-bootstrap/s08/paquetes/s08-008"
JOB = "netlab360-s08-blackbox"
PREFIX = "netlab360-s08-observe"
OPEN = build_opener(ProxyHandler({}))
UNITS = [PREFIX + "-" + suffix for suffix in ("bb-hq", "bb-s2", "relay-hq", "relay-s2", "gateway")]


def query(path, params=None, raw=False):
    url = "http://127.0.0.1:9091" + path
    if params:
        url += "?" + urlencode(params)
    with OPEN.open(url, timeout=7) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("PROM_RESPONSE_LIMIT")
    if raw:
        return data
    result = json.loads(data)
    if result.get("status") != "success" or result.get("warnings"):
        raise ValueError("PROM_RESPONSE")
    return result["data"]


def promql(expression, end=None):
    params = {"query": expression}
    if end is not None:
        params["time"] = str(end)
    return query("/api/v1/query", params)


def render(original):
    """Preservar íntegramente el YAML S04; añadir solo un archivo y un job."""
    if original.count("rule_files:\n") != 1 or original.count("scrape_configs:\n") != 1:
        raise ValueError("UNEXPECTED_PROM_CONFIG")
    if JOB in original or "s08-probe-alerts.yml" in original:
        raise ValueError("S08_ALREADY_CONFIGURED")
    result = original.replace("rule_files:\n", "rule_files:\n  - "
                              + str(INSTALL / "s08-probe-alerts.yml") + "\n")
    result += "\n  - job_name: " + JOB + "\n    scrape_interval: 10s\n    scrape_timeout: 8s\n    static_configs:\n"
    for identifier in S.PROBES:
        row = S.probe(identifier)
        result += ('      - targets: ["127.0.0.1:9116"]\n'
                   '        labels:\n'
                   f'          probe_id: "{identifier}"\n'
                   f'          origin: "{row["origin"]}"\n'
                   f'          module: "{row["module"]}"\n'
                   '          laboratory: netlab360-lab\n'
                   f'          probe_path: "/probe/{identifier}"\n')
    return result + (
        '    relabel_configs:\n'
        '      - source_labels: [probe_path]\n'
        '        target_label: __metrics_path__\n'
        '      - action: labeldrop\n'
        '        regex: probe_path\n'
    )


def write_atomic(path, data, mode):
    """Reemplazar de forma atómica en el mismo filesystem."""
    fd, temporary = tempfile.mkstemp(prefix=".s08-config-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def unit(name, argv, namespace=None, raw=False):
    options = PILOT["unit_args"](name, namespace, lifetime=90, icmp_raw=raw)
    options = [x for x in options if not x.startswith("--property=RuntimeMaxSec=")]
    # La función del piloto solo autoriza CAP_NET_RAW en nombres bb-hq/bb-s2.
    run(options + argv)


def target_check(new):
    rows = query("/api/v1/targets")["activeTargets"]
    base = [x for x in rows if x["labels"].get("job") == "netlab360-s04-multisede"]
    if len(base) != 1 or base[0]["health"] != "up":
        return False
    probes = [x for x in rows if x["labels"].get("job") == JOB]
    return (not probes if not new else
            len(probes) == 5 and {x["labels"].get("probe_id") for x in probes} == set(S.PROBES)
            and all(x["health"] == "up" for x in probes))


def wait(predicate, timeout=35):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(1)
    raise TimeoutError("OBSERVATION_WAIT_TIMEOUT")


def reload(pid, new):
    """Verificar recarga efectiva, no solo envío de señal."""
    def last():
        rows = promql("prometheus_config_last_reload_success_timestamp_seconds")["result"]
        # Esta instancia no se auto-scrapea; usar el endpoint /metrics.
        return rows
    # El endpoint /metrics contiene las métricas internas aun sin auto-scrape.
    def state():
        raw = query("/metrics", raw=True).decode()
        return tuple(float(next(line.split()[1] for line in raw.splitlines()
                           if line.startswith(name + " "))) for name in (
            "prometheus_config_last_reload_successful",
            "prometheus_config_last_reload_success_timestamp_seconds"))
    before = state()[1]
    time.sleep(1.1)
    os.kill(pid, signal.SIGHUP)
    wait(lambda: state()[0] == 1 and state()[1] > before)
    wait(lambda: target_check(new), timeout=45)


def cleanup(created):
    for name in reversed(created):
        PILOT["stop"](name)
    if any(PILOT["active"](name) for name in UNITS):
        raise RuntimeError("OBSERVATION_STOP_UNCONFIRMED")
    # Conservar instalación y runtime para diagnóstico; nunca borrar datos del laboratorio.


def main(evidence):
    evidence.mkdir(mode=0o700)
    original = CONFIG.read_bytes()
    mode = CONFIG.stat().st_mode & 0o777
    if CONFIG.is_symlink() or CONFIG.stat().st_uid != os.getuid():
        raise ValueError("CONFIG_OWNERSHIP")
    flags = query("/api/v1/status/flags")
    if (flags["config.file"] != str(CONFIG)
            or flags["storage.tsdb.path"] != str(HOME / "netlab360-bootstrap/prometheus/s04/data")
            or flags["storage.tsdb.retention.time"] != "180d"):
        raise ValueError("PROMETHEUS_IDENTITY")
    pid = int(run(["/usr/bin/systemctl", "show", "netlab360-s04-prometheus.service",
                   "--property=MainPID", "--value"]).stdout)
    if pid <= 1 or not target_check(False):
        raise ValueError("PROMETHEUS_BASELINE")
    if any(PILOT["active"](name) for name in UNITS) or not free(None, 9116):
        raise RuntimeError("OBSERVATION_ALREADY_ACTIVE")
    if sudo("/usr/bin/test", "-e", str(INSTALL), check=False).returncode == 0:
        raise RuntimeError("INSTALL_ALREADY_EXISTS")
    if sudo("/usr/bin/test", "-e", str(RUNTIME), check=False).returncode == 0:
        raise RuntimeError("RUNTIME_ALREADY_EXISTS")
    for origin in ("HQ", "S2"):
        if not free(C.ENDPOINTS[origin].namespace, 9115):
            raise RuntimeError("BLACKBOX_PORT_BUSY")
    (evidence / "prometheus-original.yml").write_bytes(original)
    stage = Path(tempfile.mkdtemp(prefix="netlab360-s08-continuous."))
    stage.chmod(0o755)
    created = []
    changed = False
    try:
        binary = PILOT["package"](stage, "prometheus-blackbox-exporter", "0.26.0-2",
                                  ("prometheus-blackbox-exporter", "blackbox_exporter"), CACHE)
        for directory in (INSTALL, INSTALL / "consola", INSTALL / "consola/api"):
            sudo("/usr/bin/install", "-d", "-o", "root", "-g", "root", "-m", "0755", str(directory))
        mapping = {
            binary: ("blackbox_exporter", "0755"),
            REPO / "scripts/s08/sondas_continuas.py": ("sondas_continuas.py", "0644"),
            REPO / "servicios/observabilidad/blackbox/s08-blackbox.yml": ("blackbox.yml", "0644"),
            REPO / "servicios/observabilidad/prometheus/rules/s08-probe-alerts.yml": ("s08-probe-alerts.yml", "0644"),
        }
        for name in ("__init__.py", "probe_catalog.py", "slo_contract.py"):
            mapping[REPO / "servicios/consola-s08/api" / name] = ("consola/api/" + name, "0644")
        for source, (name, permissions) in mapping.items():
            dest = INSTALL / name
            sudo("/usr/bin/install", "-o", "root", "-g", "root", "-m", permissions, str(source), str(dest))
            if hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(dest.read_bytes()).digest():
                raise ValueError("INSTALL_DIGEST")
        sudo("/usr/bin/install", "-d", "-o", "root", "-g", ACCOUNT, "-m", "0750", str(RUNTIME))
        for origin in ("HQ", "S2"):
            ns = C.ENDPOINTS[origin].namespace
            sudo("/usr/bin/install", "-d", "-o", ACCOUNT, "-g", ACCOUNT, "-m", "0700", str(RUNTIME / origin.lower()))
            group = PILOT["netns"](ns, "/usr/sbin/sysctl", "-n", "net.ipv4.ping_group_range").stdout.split()
            low, high = map(int, group)
            worker = pwd.getpwnam(ACCOUNT)
            raw = not low <= worker.pw_gid <= high
            name = PREFIX + "-bb-" + origin.lower()
            created.append(name)
            unit(name, [str(INSTALL / "blackbox_exporter"), "--config.file=" + str(INSTALL / "blackbox.yml"),
                        "--web.listen-address=127.0.0.1:9115"], ns, raw)
            wait(lambda: PILOT["active"](name) and not free(ns, 9115))
            PILOT["verify_blackbox_privileges"](name, ns, worker, raw)
            name = PREFIX + "-relay-" + origin.lower()
            created.append(name)
            unit(name, ["/usr/bin/python3", "-I", "-B", str(INSTALL / "sondas_continuas.py"), origin], ns)
            wait(lambda: sudo("/usr/bin/test", "-S", str(RUNTIME / origin.lower() / "probe.sock"),
                              check=False).returncode == 0)
        name = PREFIX + "-gateway"
        created.append(name)
        unit(name, ["/usr/bin/python3", "-I", "-B", str(INSTALL / "sondas_continuas.py"), "gateway"])
        wait(lambda: PILOT["active"](name) and not free(None, 9116))
        for identifier in S.PROBES:
            with OPEN.open("http://127.0.0.1:9116/probe/" + identifier, timeout=8) as response:
                body = response.read(65537)
            if b"probe_success 1\n" not in body:
                raise ValueError("INITIAL_PROBE_FAILED:" + identifier)
            (evidence / (identifier + ".prom")).write_bytes(body)
        print("ADQUISICION_CONTINUA_ENDPOINTS=5/5", flush=True)
        candidate = render(original.decode()).encode()
        candidate_path = evidence / "prometheus-candidate.yml"
        candidate_path.write_bytes(candidate)
        run([str(PROMTOOL), "check", "config", str(candidate_path)])
        if CONFIG.read_bytes() != original:
            raise RuntimeError("CONFIG_CHANGED_CONCURRENTLY")
        changed = True
        write_atomic(CONFIG, candidate, mode)
        reload(pid, True)
        # Aceptar al menos dos scrapes reales y preservar series originales de S04.
        def sample_count():
            rows = promql('count_over_time(probe_success{job="' + JOB + '"}[1m])')["result"]
            return len(rows) == 5 and all(float(r["value"][1]) >= 2 for r in rows)
        wait(sample_count, timeout=45)
        from importlib import import_module
        sys.path.insert(0, str(REPO / "servicios/consola-s08"))
        W = import_module("api.slo_window")
        end = int(time.time())
        observations = []
        for identifier in S.PROBES:
            selector = '{job="' + JOB + '",probe_id="' + identifier + '"}[5m]'
            up = promql("up" + selector, end)["result"]
            probes = promql("probe_success" + selector, end)["result"]
            if len(up) != 1 or len(probes) != 1:
                raise ValueError("SERIES_IDENTITY")
            row = W.evaluate(identifier, 5, end, up[0]["values"], probes[0]["values"])
            if row["probe_count"] < 2:
                raise ValueError("INSUFFICIENT_REAL_SAMPLES")
            observations.append(row)
        PILOT["write"](evidence / "ventanas-reales.json", {"source": "PROMETHEUS_REAL", "windows": observations})
        rules = query("/api/v1/rules")["groups"]
        if {g["name"]: len(g["rules"]) for g in rules} != {
                "netlab360-s04-seguridad-de-observacion": 4, "netlab360-s08-sondas": 3}:
            raise ValueError("RULES_NOT_PRESERVED")
        if not all(PILOT["active"](name) for name in UNITS):
            raise RuntimeError("OBSERVATION_SERVICE_EXITED")
        if int(run(["/usr/bin/systemctl", "show", "netlab360-s04-prometheus.service",
                    "--property=MainPID", "--value"]).stdout) != pid:
            raise RuntimeError("PROMETHEUS_RESTARTED")
        print("PROMETHEUS_RELOAD=OK TARGETS=6/6 REGLAS=7/7 VENTANAS_REALES=5/5", flush=True)
        print("SERVICIOS_ADQUISICION=5/5", flush=True)
    except BaseException:
        if changed:
            write_atomic(CONFIG, original, mode)
            reload(pid, False)
            print("PROMETHEUS_ROLLBACK=OK", flush=True)
        cleanup(created)
        raise
    finally:
        shutil.rmtree(stage)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: desplegar_sondas_continuas.py EVIDENCIAS")
    main(Path(sys.argv[1]))
