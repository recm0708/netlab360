#!/usr/bin/env python3
"""Conectar Prometheus a Alertmanager y a un registro local autenticado."""
import base64
import ctypes
import grp
import hashlib
import json
import os
from pathlib import Path
import pwd
import runpy
import secrets
import shutil
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request
import re

REPO = Path(__file__).resolve().parents[2]
D = runpy.run_path(str(REPO / "scripts/s08/desplegar_sondas_continuas.py"))
P = D["PILOT"]
run, sudo, free = (P[key] for key in ("run", "sudo", "free"))
query, promql, wait, reload = (D[key] for key in ("query", "promql", "wait", "reload"))
CONFIG, CACHE, PROMTOOL = (D[key] for key in ("CONFIG", "CACHE", "PROMTOOL"))
ACCOUNT = "netlab360-s08-alerts"
INSTALL = Path("/usr/local/libexec/netlab360/s08-alertas")
STATE = Path("/var/lib/netlab360/s08-alertas")
DB = STATE / "notificaciones.sqlite3"
PROM_SECRET = Path.home() / "netlab360-bootstrap/s08/alertmanager-prometheus.secret"
RECEIVER = "netlab360-s08-alert-receiver"
AM = "netlab360-s08-alert-am"
OPEN = D["OPEN"]


def bcrypt_hash(password):
    """Generar bcrypt mediante libcrypt local; verificar soporte antes de aprovisionar."""
    library = ctypes.CDLL("libcrypt.so.1")
    crypt = library.crypt
    crypt.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
    crypt.restype = ctypes.c_char_p
    alphabet = "./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    salt = "$2b$12$" + "".join(secrets.choice(alphabet) for _ in range(21)) + secrets.choice(".Oeu")
    digest = crypt(password.encode(), salt.encode())
    if not digest or len(digest) != 60 or not digest.startswith(b"$2b$12$"):
        raise RuntimeError("BCRYPT_UNAVAILABLE")
    digest = bytes(digest)
    if crypt(password.encode(), digest) != digest:
        raise RuntimeError("BCRYPT_VERIFY_FAILED")
    return digest.decode("ascii")


def render(original, secret_path, validation=None):
    """Añadir destino único; mantener íntegramente los trabajos y reglas existentes."""
    if "alerting:" in original or original.count("rule_files:\n") != 1:
        raise ValueError("UNEXPECTED_ALERTING_CONFIGURATION")
    result = original
    if validation is not None:
        result = result.replace("rule_files:\n", "rule_files:\n  - " + str(validation) + "\n")
    return result + (
        "\nalerting:\n"
        "  alertmanagers:\n"
        "    - api_version: v2\n"
        "      timeout: 5s\n"
        "      basic_auth:\n"
        "        username: prometheus\n"
        f"        password_file: {secret_path}\n"
        "      static_configs:\n"
        '        - targets: ["127.0.0.1:9093"]\n'
    )


def validation_rule(run_id, deadline):
    """Un evento sintético temporal, sin cambiar interfaces ni procesos de red."""
    return (
        "groups:\n"
        "  - name: netlab360-s08-validation\n"
        "    interval: 2s\n"
        "    rules:\n"
        "      - alert: NETLAB360S08Validation\n"
        f"        expr: vector(time()) < {deadline}\n"
        "        for: 10s\n"
        "        labels:\n"
        "          phase: validation\n"
        '          synthetic: "true"\n'
        f'          run_id: "{run_id}"\n'
        "        annotations:\n"
        '          summary: "Validación sintética de entrega; no incidente real"\n'
    )


def mkdir(path, owner="root", group="root", mode="0755"):
    sudo("/usr/bin/install", "-d", "-o", owner, "-g", group, "-m", mode, str(path))


def install(source, destination, mode="0644", group="root"):
    sudo("/usr/bin/install", "-o", "root", "-g", group, "-m", mode, str(source), str(destination))
    actual = sudo("/usr/bin/sha256sum", str(destination)).stdout.split()[0]
    if actual != hashlib.sha256(source.read_bytes()).hexdigest():
        raise ValueError("INSTALL_DIGEST")


def account():
    try:
        user = pwd.getpwnam(ACCOUNT)
    except KeyError:
        sudo("/usr/sbin/useradd", "--system", "--user-group", "--no-create-home",
             "--home-dir", "/nonexistent", "--shell", "/usr/sbin/nologin", ACCOUNT)
        user = pwd.getpwnam(ACCOUNT)
    if (user.pw_uid <= 0 or user.pw_dir != "/nonexistent" or not user.pw_shell.endswith("/nologin")
            or grp.getgrnam(ACCOUNT).gr_gid != user.pw_gid
            or set(os.getgrouplist(ACCOUNT, user.pw_gid)) != {user.pw_gid}):
        raise ValueError("ALERT_ACCOUNT_IDENTITY")
    status = sudo("/usr/bin/passwd", "-S", ACCOUNT).stdout.split()
    if len(status) < 2 or status[1] not in ("L", "LK"):
        raise ValueError("ALERT_ACCOUNT_NOT_LOCKED")
    return user


def service(name, command, share=None):
    options = P["unit_args"](name, share_root=share)
    options = [x for x in options if not x.startswith(("--property=RuntimeMaxSec=", "--property=LimitFSIZE="))]
    options = [x.replace("User=" + P["ACCOUNT"], "User=" + ACCOUNT)
               .replace("Group=" + P["ACCOUNT"], "Group=" + ACCOUNT) for x in options]
    run(options + command)


def verify_identity(name, user):
    """Comprobar identidad efectiva, capacidades y confinamiento real."""
    pid = int(run(["/usr/bin/systemctl", "show", name, "--property=MainPID", "--value"]).stdout)
    if pid <= 1:
        raise ValueError("ALERT_SERVICE_PID")
    raw = sudo("/usr/bin/cat", f"/proc/{pid}/status").stdout
    fields = dict(line.split(":", 1) for line in raw.splitlines() if ":" in line)
    for key, expected in (("Uid", user.pw_uid), ("Gid", user.pw_gid)):
        if [int(x) for x in fields[key].split()] != [expected] * 4:
            raise ValueError("ALERT_SERVICE_IDENTITY")
    if any(int(fields[key].strip(), 16) for key in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb")):
        raise ValueError("ALERT_SERVICE_CAPABILITIES")
    if fields["NoNewPrivs"].strip() != "1":
        raise ValueError("ALERT_SERVICE_NNP")
    print(f"IDENTIDAD_ALERTAS={name} UID={user.pw_uid} GID={user.pw_gid} CAP=0 NNP=1", flush=True)


def http(port, path, password=None):
    request = Request(f"http://127.0.0.1:{port}{path}")
    if password is not None:
        request.add_header("Authorization", "Basic " + base64.b64encode(
            ("prometheus:" + password).encode()).decode())
    with OPEN.open(request, timeout=5) as response:
        data = response.read(131073)
        if len(data) > 131072:
            raise ValueError("ALERT_RESPONSE_LIMIT")
        return data


def ready(port, path, password=None):
    try:
        return bool(http(port, path, password))
    except (OSError, URLError):
        return False


def inspect(scope):
    result = run(["/usr/bin/sudo", "-n", "-u", ACCOUNT, "--", "/usr/bin/python3", "-I", "-B",
                  str(INSTALL / "recibir_alertas.py"), scope, "--database", str(DB)])
    return json.loads(result.stdout)


def check_windows(evidence):
    """Leer las quince ventanas a un mismo instante sin interpolación de muestras."""
    from api import slo_window as W, slo_contract as S
    end = round(time.time(), 3)
    rows = []
    for minutes in S.WINDOWS_MIN:
        selector = '{job="netlab360-s08-blackbox"}[' + str(minutes) + 'm]'
        sources = []
        for name in ("up", "probe_success"):
            data = promql(name + selector, end)
            if data.get("resultType") != "matrix":
                raise ValueError("WINDOW_RESULT_TYPE")
            series = {}
            for item in data["result"]:
                key = item["metric"]["probe_id"]
                if key not in S.PROBES or key in series:
                    raise ValueError("WINDOW_SERIES_IDENTITY")
                series[key] = item["values"]
            sources.append(series)
        for key in S.PROBES:
            row = W.evaluate(key, minutes, end, sources[0].get(key, []), sources[1].get(key, []))
            rows.append(row)
            print(f"VENTANA={key}/{minutes}m MUESTRAS={row['probe_count']} CALIDAD={row['quality']}", flush=True)
    P["write"](evidence / "ventanas-reales.json", {"source": "PROMETHEUS_REAL", "windows": rows})
    print("VENTANAS_REALES=15/15", flush=True)


def resume_installation(stage):
    """Verificar el aprovisionamiento anterior sin sustituir recursos ni secretos."""
    pwd.getpwnam(ACCOUNT)
    user = account()
    def secure(path, uid, gid, permissions, kind):
        raw = sudo("/usr/bin/stat", "-c", "%u:%g:%a:%F:%h", str(path)).stdout.strip()
        owner, group, mode, file_type, links = raw.split(":")
        if (int(owner) != uid or (gid is not None and int(group) != gid)
                or int(mode, 8) != permissions or file_type != kind
                or (kind == "regular file" and links != "1")):
            # GNU stat distingue el archivo regular vacío.
            raise ValueError("RESUME_PATH_IDENTITY:" + str(path))
    for path in (INSTALL, INSTALL / "share", INSTALL / "share/prometheus",
                 INSTALL / "share/prometheus/alertmanager"):
        secure(path, 0, 0, 0o755, "directory")
    for path in (STATE, STATE / "alertmanager"):
        secure(path, user.pw_uid, user.pw_gid, 0o700, "directory")
    secure(DB, user.pw_uid, user.pw_gid, 0o600, "regular file")
    secure(PROM_SECRET, os.getuid(), None, 0o600, "regular file")
    for name in ("webhook.secret", "web.yml", "alertmanager.yml"):
        secure(INSTALL / name, 0, user.pw_gid, 0o640, "regular file")
    binary = P["package"](stage, "prometheus-alertmanager", "0.28.1+ds-3",
                          ("prometheus-alertmanager", "alertmanager"), CACHE)
    share = P["alertmanager_share"](binary)
    mapping = {INSTALL / "alertmanager": (binary, 0o755),
               INSTALL / "recibir_alertas.py": (REPO / "scripts/s08/recibir_alertas.py", 0o644),
               INSTALL / "alertmanager.yml": (
                   REPO / "servicios/observabilidad/alertmanager/s08-operacional.yml", 0o640)}
    for name in ("default.tmpl", "email.tmpl"):
        relative = Path("prometheus/alertmanager") / name
        mapping[INSTALL / "share" / relative] = (share / relative, 0o644)
    for destination, (source, permissions) in mapping.items():
        secure(destination, 0, user.pw_gid if permissions == 0o640 else 0,
               permissions, "regular file")
        actual = sudo("/usr/bin/sha256sum", str(destination)).stdout.split()[0]
        if actual != hashlib.sha256(source.read_bytes()).hexdigest():
            raise ValueError("RESUME_INSTALL_DIGEST:" + str(destination))
    for scope in ("operational", "validation"):
        previous = inspect(scope)
        print("HISTORIAL_PREVIO=" + scope + ":" + str(previous["total"]), flush=True)
    password = PROM_SECRET.read_text().strip()
    if not re.fullmatch("[A-Za-z0-9_-]{32,128}", password):
        raise ValueError("RESUME_SECRET_FORMAT")
    print("APROVISIONAMIENTO_PREVIO_VERIFICADO=OK", flush=True)
    return user, password


def destination_ready():
    active = query("/api/v1/alertmanagers")["activeAlertmanagers"]
    return len(active) == 1 and active[0]["url"] == "http://127.0.0.1:9093/api/v2/alerts"


def delivery_diagnostics(password, run_id=None):
    """Recoger indicadores de transporte sin exponer credenciales ni otros incidentes."""
    result = {"destination": query("/api/v1/alertmanagers")}
    prefixes = ("prometheus_notifications_", "alertmanager_notifications_",
                "alertmanager_alerts_received", "alertmanager_alerts_invalid")
    for port in (9091, 9093):
        request = Request(f"http://127.0.0.1:{port}/metrics")
        if port == 9093:
            request.add_header("Authorization", "Basic " + base64.b64encode(
                ("prometheus:" + password).encode()).decode())
        with OPEN.open(request, timeout=5) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("DELIVERY_METRICS_LIMIT")
        result[str(port)] = [line for line in raw.decode().splitlines()
                             if line.startswith(prefixes)]
    if run_id is not None:
        expression = 'ALERTS{alertname="NETLAB360S08Validation",run_id="' + run_id + '"}'
        result["prometheus_validation"] = promql(expression)["result"]
        alerts = json.loads(http(9093, "/api/v2/alerts", password))
        result["alertmanager_validation"] = [
            {"state": row.get("status", {}).get("state"), "startsAt": row.get("startsAt"),
             "endsAt": row.get("endsAt")}
            for row in alerts if row.get("labels", {}).get("run_id") == run_id]
        result["sqlite_validation"] = [
            row for row in inspect("validation")["records"]
            if json.loads(row["labels_json"]).get("run_id") == run_id]
    return result


def main(evidence, resume=False):
    os.umask(0o077)
    evidence.mkdir(mode=0o700)
    original = CONFIG.read_bytes()
    mode = CONFIG.stat().st_mode & 0o777
    if CONFIG.is_symlink() or CONFIG.stat().st_uid != os.getuid():
        raise ValueError("CONFIG_OWNERSHIP")
    if "netlab360-s08-blackbox" not in original.decode() or not D["target_check"](True):
        raise ValueError("BASELINE_TARGETS")
    flags = query("/api/v1/status/flags")
    if (flags["config.file"] != str(CONFIG)
            or flags["storage.tsdb.path"] != str(Path.home() / "netlab360-bootstrap/prometheus/s04/data")
            or flags["storage.tsdb.retention.time"] != "180d"):
        raise ValueError("PROMETHEUS_IDENTITY")
    pid = int(run(["/usr/bin/systemctl", "show", "netlab360-s04-prometheus.service",
                   "--property=MainPID", "--value"]).stdout)
    if pid <= 1 or any(P["active"](name) for name in (RECEIVER, AM)):
        raise RuntimeError("SERVICE_BASELINE")
    if not free(None, 9093) or not free(None, 9193):
        raise RuntimeError("ALERT_PORT_BUSY")
    if not resume:
        for path in (INSTALL, STATE, PROM_SECRET):
            if any(sudo("/usr/bin/test", flag, str(path), check=False).returncode == 0
                   for flag in ("-e", "-L")):
                raise RuntimeError("ALERT_PATH_ALREADY_EXISTS:" + str(path))
    password = None
    run_id = None
    final = render(original.decode(), PROM_SECRET).encode()
    (evidence / "prometheus-original.yml").write_bytes(original)
    stage = Path(tempfile.mkdtemp(prefix="netlab360-s08-alerts."))
    stage.chmod(0o755)
    created = []
    applied = None
    try:
        if resume:
            user, password = resume_installation(stage)
        else:
            password = secrets.token_urlsafe(32)
            webhook = secrets.token_urlsafe(32)
            digest = bcrypt_hash(password)
            binary = P["package"](stage, "prometheus-alertmanager", "0.28.1+ds-3",
                              ("prometheus-alertmanager", "alertmanager"), CACHE)
            share = P["alertmanager_share"](binary)
            user = account()
            for path in (INSTALL, INSTALL / "share", INSTALL / "share/prometheus",
                         INSTALL / "share/prometheus/alertmanager"):
                mkdir(path)
            mkdir(STATE, ACCOUNT, ACCOUNT, "0700")
            mkdir(STATE / "alertmanager", ACCOUNT, ACCOUNT, "0700")
            install(binary, INSTALL / "alertmanager", "0755")
            install(REPO / "scripts/s08/recibir_alertas.py", INSTALL / "recibir_alertas.py")
            for name in ("default.tmpl", "email.tmpl"):
                relative = Path("prometheus/alertmanager") / name
                install(share / relative, INSTALL / "share" / relative)
            files = {
                "webhook.secret": webhook + "\n",
                "web.yml": "basic_auth_users:\n  prometheus: '" + digest + "'\n",
                "alertmanager.yml": (REPO / "servicios/observabilidad/alertmanager/s08-operacional.yml").read_text(),
            }
            for name, content in files.items():
                source = stage / name
                with source.open("x") as handle:
                    handle.write(content)
                install(source, INSTALL / name, "0640", ACCOUNT)
            with PROM_SECRET.open("x") as handle:
                handle.write(password + "\n")
            PROM_SECRET.chmod(0o600)
        created.append(RECEIVER)
        service(RECEIVER, ["/usr/bin/python3", "-I", "-B", str(INSTALL / "recibir_alertas.py"),
                            "serve", "--database", str(DB), "--secret", str(INSTALL / "webhook.secret")])
        wait(lambda: ready(9193, "/healthz"))
        verify_identity(RECEIVER, user)
        created.append(AM)
        service(AM, [str(INSTALL / "alertmanager"), "--config.file=" + str(INSTALL / "alertmanager.yml"),
                     "--storage.path=" + str(STATE / "alertmanager"),
                     "--web.listen-address=127.0.0.1:9093", "--cluster.listen-address=",
                     "--web.config.file=" + str(INSTALL / "web.yml")], INSTALL / "share")
        wait(lambda: ready(9093, "/api/v2/status", password))
        verify_identity(AM, user)
        P["verify_alertmanager_mount"](AM, INSTALL / "share")
        try:
            http(9093, "/api/v2/status")
        except HTTPError as error:
            if error.code != 401:
                raise
        else:
            raise RuntimeError("UNAUTHENTICATED_ALERTMANAGER")
        # El receptor también exige credenciales para POST.
        try:
            OPEN.open(Request("http://127.0.0.1:9193/receive", data=b"{}"), timeout=5)
        except HTTPError as error:
            if error.code != 401:
                raise
        else:
            raise RuntimeError("UNAUTHENTICATED_WEBHOOK")
        print("AUTENTICACION_ALERTMANAGER_Y_WEBHOOK=OK", flush=True)
        final_path = evidence / "prometheus-final.yml"
        final_path.write_bytes(final)
        print(run([str(PROMTOOL), "check", "config", str(final_path)]).stdout, flush=True)
        if CONFIG.read_bytes() != original:
            raise RuntimeError("CONFIG_CHANGED_CONCURRENTLY")
        D["write_atomic"](CONFIG, final, mode)
        applied = final
        reload(pid, True)
        wait(destination_ready, timeout=45)
        print("ALERTMANAGER_DESTINO_DESCUBIERTO=OK", flush=True)
        P["write"](evidence / "transporte-antes.json", delivery_diagnostics(password))
        run_id = secrets.token_hex(8)
        rule = evidence / "validacion-sintetica.yml"
        # Mantener la condición más allá del reenvío predeterminado de un minuto.
        rule.write_text(validation_rule(run_id, int(time.time()) + 150))
        candidate = render(original.decode(), PROM_SECRET, rule).encode()
        candidate_path = evidence / "prometheus-candidate.yml"
        candidate_path.write_bytes(candidate)
        print(run([str(PROMTOOL), "check", "config", str(candidate_path)]).stdout, flush=True)
        if CONFIG.read_bytes() != final:
            raise RuntimeError("CONFIG_CHANGED_CONCURRENTLY")
        D["write_atomic"](CONFIG, candidate, mode)
        applied = candidate
        reload(pid, True)
        wait(destination_ready, timeout=45)
        print("ALERTMANAGER_DESTINO_ACTIVO_CON_REGLA=OK", flush=True)
        def validation(status):
            data = inspect("validation")
            return any(row["status"] == status and json.loads(row["labels_json"]).get("run_id") == run_id
                       for row in data["records"])
        wait(lambda: validation("firing"), timeout=100)
        P["write"](evidence / "transporte-firing.json", delivery_diagnostics(password, run_id))
        print("PROMETHEUS_ALERTMANAGER_WEBHOOK_FIRING=OK", flush=True)
        wait(lambda: validation("resolved"), timeout=220)
        P["write"](evidence / "transporte-resolved.json", delivery_diagnostics(password, run_id))
        history = inspect("validation")
        records = [row for row in history["records"]
                   if json.loads(row["labels_json"]).get("run_id") == run_id]
        if (len(records) != 2 or {row["status"] for row in records} != {"firing", "resolved"}
                or len({(row["fingerprint"], row["starts_at_utc"]) for row in records}) != 1):
            raise ValueError("VALIDATION_LIFECYCLE")
        P["write"](evidence / "entrega-validacion.json", {"source": "PROMETHEUS_ALERTMANAGER_REAL",
                                                          "synthetic": True, "records": records})
        print("PROMETHEUS_ALERTMANAGER_WEBHOOK_RESOLVED=OK", flush=True)
        if CONFIG.read_bytes() != candidate:
            raise RuntimeError("CONFIG_CHANGED_CONCURRENTLY")
        D["write_atomic"](CONFIG, final, mode)
        applied = final
        reload(pid, True)
        wait(destination_ready, timeout=45)
        rules = query("/api/v1/rules")["groups"]
        if {g["name"]: len(g["rules"]) for g in rules} != {
                "netlab360-s04-seguridad-de-observacion": 4, "netlab360-s08-sondas": 3}:
            raise ValueError("RULES_NOT_PRESERVED")
        P["write"](evidence / "historial-operacional.json", inspect("operational"))
        check_windows(evidence)
        if int(run(["/usr/bin/systemctl", "show", "netlab360-s04-prometheus.service",
                    "--property=MainPID", "--value"]).stdout) != pid:
            raise RuntimeError("PROMETHEUS_RESTARTED")
        if not all(P["active"](name) for name in (RECEIVER, AM, *D["UNITS"])):
            raise RuntimeError("SERVICE_EXITED")
        print("ALERTMANAGER_OPERACIONAL=OK REGLAS=7/7 TARGETS=6/6", flush=True)
    except BaseException:
        if password is not None and P["active"](AM):
            try:
                P["write"](evidence / "transporte-error.json", delivery_diagnostics(password, run_id))
            except Exception as error:
                print("DIAGNOSTICO_TRANSPORTE_NO_DISPONIBLE=" + type(error).__name__, flush=True)
        for name in (*created, "netlab360-s04-prometheus"):
            log = sudo("/usr/bin/journalctl", "-u", name, "--no-pager", "-n", "40", check=False)
            (evidence / (name + ".log")).write_text(log.stdout)
        if applied is not None:
            if CONFIG.read_bytes() != applied:
                raise RuntimeError("ROLLBACK_CONFIG_CHANGED_CONCURRENTLY")
            D["write_atomic"](CONFIG, original, mode)
            reload(pid, True)
            print("PROMETHEUS_ROLLBACK=OK", flush=True)
        for name in reversed(created):
            P["stop"](name)
        raise
    finally:
        shutil.rmtree(stage)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] != "--resume"):
        raise SystemExit("Uso: desplegar_alertas.py EVIDENCIAS [--resume]")
    main(Path(sys.argv[1]), resume=len(sys.argv) == 3)
