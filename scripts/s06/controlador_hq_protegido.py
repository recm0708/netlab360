#!/usr/bin/env python3
"""S06-042: intervención breve/recuperación SOLO egreso HQ VLAN120.

Objeto: nl360-s02-h-hq-120/eth0, IP 10.70.20.20/24.
No crea interfaces, namespaces ni rutas. No ejecuta comandos arbitrarios.
El cambio requiere --approve literal, copia root-owned, qdisc noqueue,
topología/NOC saludables, timer systemd independiente ACTIVO antes de tc.
Tras 35 s, el timer devuelve la qdisc propia a noqueue incluso si el
controlador termina. No instalar ni utilizar en otras máquinas.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys
import tempfile
from urllib.request import urlopen

INSTALL = Path("/usr/local/libexec/netlab360/s06-hq-controlador.py")
RUNTIME = Path("/run/netlab360-s06-hq")
STATE = RUNTIME / "state.json"
LOCK = RUNTIME / "lock"
NS = "nl360-s02-h-hq-120"
PEER = "nl360-s02-sw-hq"
DEV = "eth0"
CLIENT_IP = "10.70.20.20"
CLIENT_PREFIX = 24
CLIENT_GW = "10.70.20.1"
HOST_IP = "192.168.47.40/24"
HOST_GW = "192.168.47.2"
DESTS = ("10.71.20.20", "10.72.20.20")
HANDLE = "142:"
LATENCY = 40
TTL = 35
SCHEMA = "NETLAB360_S06_HQ_EXPERIMENT_GUARD_V1"
APPROVAL = "AUTORIZO_HQ_VLAN120_NETEM_40MS_35S"
STATES = frozenset({
    "ARMING", "ARMED", "APPLY_PENDING", "APPLIED", "APPLY_UNKNOWN",
    "RESTORED", "RESTORED_NO_CHANGE", "ESCALATED"
})
SERVICE_NAMES = (
    "netlab360-s04-exporter", "netlab360-s04-prometheus",
    "netlab360-s05-noc", "netlab360-s05-ha-backend-hq",
    "netlab360-s05-ha-backend-s1", "netlab360-s05-ha-frontal-hq",
    "netlab360-s05-ha-monitor-s2",
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def run(*args: str) -> str:
    p = subprocess.run(args, capture_output=True, text=True,
                       timeout=12, check=False)
    if p.returncode:
        raise RuntimeError(
            "command_failed=" + " ".join(args[:5])
            + " rc=" + str(p.returncode) + " " + p.stderr[-220:]
        )
    return p.stdout


def trusted_install() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("root_required")
    if Path(__file__) != INSTALL or INSTALL.is_symlink() or not INSTALL.is_file():
        raise RuntimeError("protected_install_required")
    for p in (INSTALL, INSTALL.parent):
        s = p.lstat()
        if s.st_uid != 0 or s.st_mode & 0o022:
            raise RuntimeError("untrusted_install_permissions")
    if stat.S_IMODE(INSTALL.stat().st_mode) != 0o750:
        raise RuntimeError("script_mode_not_0750")


def private_dir() -> None:
    if RUNTIME.is_symlink():
        raise RuntimeError("runtime_symlink")
    if not RUNTIME.exists():
        RUNTIME.mkdir(mode=0o700)
    s = RUNTIME.lstat()
    if (not stat.S_ISDIR(s.st_mode) or s.st_uid != os.geteuid()
            or stat.S_IMODE(s.st_mode) != 0o700):
        raise RuntimeError("runtime_untrusted")


@contextmanager
def exclusive(*, wait: bool = False):
    private_dir()
    fd = os.open(LOCK, os.O_NOFOLLOW | os.O_RDWR | os.O_CREAT, 0o600)
    try:
        s = os.fstat(fd)
        if (s.st_uid != os.geteuid() or not stat.S_ISREG(s.st_mode)
                or stat.S_IMODE(s.st_mode) != 0o600):
            raise RuntimeError("lock_untrusted")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX if wait else
                        fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("concurrent_operation") from exc
        yield
    finally:
        os.close(fd)


def load() -> dict | None:
    if STATE.is_symlink():
        raise RuntimeError("state_symlink")
    if not STATE.exists():
        return None
    s = STATE.lstat()
    if (not stat.S_ISREG(s.st_mode) or s.st_uid != os.geteuid()
            or stat.S_IMODE(s.st_mode) != 0o600):
        raise RuntimeError("state_untrusted")
    value = json.loads(STATE.read_text(encoding="utf-8"))
    if (value.get("schema") != SCHEMA or value.get("state") not in STATES
            or not isinstance(value.get("token"), str)):
        raise RuntimeError("unexpected_state")
    return value


def save(d: dict) -> None:
    private_dir()
    load()
    fd, temp = tempfile.mkstemp(dir=RUNTIME, prefix=".state-")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(d, out, ensure_ascii=False, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, STATE)
    finally:
        if os.path.lexists(temp):
            os.unlink(temp)


def netns_identity() -> list[int]:
    p = Path("/run/netns") / NS
    if p.is_symlink() or not p.exists():
        raise RuntimeError("client_namespace_not_mounted")
    statinfo = p.stat()
    return [statinfo.st_dev, statinfo.st_ino]


def check_management() -> None:
    host = run("ip", "-4", "-o", "addr", "show", "dev", "ens33")
    route = run("ip", "-4", "route", "show", "default")
    if HOST_IP not in host or f"default via {HOST_GW} dev ens33" not in route:
        raise RuntimeError("host_management_changed")


def check_network(*, strict_noc: bool) -> dict:
    names = [x.split()[0] for x in run("ip", "netns", "list").splitlines()
             if x.strip()]
    if (len(names) != 21 or len(set(names)) != 21
            or NS not in names or any(x.startswith("nl360-s06-") for x in names)):
        raise RuntimeError("namespace_inventory_not_original")
    addrs = json.loads(run("ip", "-n", NS, "-j", "-4",
                           "addr", "show", "dev", DEV))
    if len(addrs) != 1:
        raise RuntimeError("client_ip_info_ambiguous")
    infos = addrs[0].get("addr_info", [])
    if (len(infos) != 1 or infos[0].get("local") != CLIENT_IP
            or infos[0].get("prefixlen") != CLIENT_PREFIX):
        raise RuntimeError("client_ip_not_in_reference")
    link_txt = run("ip", "-n", NS, "-d", "link", "show", "dev", DEV)
    if "veth " not in link_txt or ("link-netns " + PEER) not in link_txt:
        raise RuntimeError("client_peer_link_unexpected")
    for target in DESTS:
        rows = json.loads(run("ip", "-n", NS, "-j", "-4", "route", "get", target))
        if (len(rows) != 1 or rows[0].get("dst") != target
                or rows[0].get("dev") != DEV
                or rows[0].get("prefsrc", rows[0].get("src")) != CLIENT_IP
                or rows[0].get("gateway") != CLIENT_GW):
            raise RuntimeError("client_route_unexpected_" + target)
    if strict_noc:
        for svc in SERVICE_NAMES:
            if run("systemctl", "is-active", svc).strip() != "active":
                raise RuntimeError("service_not_active_" + svc)
        with urlopen("http://127.0.0.1:9130/healthz", timeout=6) as f:
            health = json.load(f)
        with urlopen("http://127.0.0.1:9130/api/v1/graph", timeout=6) as f:
            graph = json.load(f)
        if (health.get("healthy") is not True
                or len(graph.get("nodes", [])) != 18
                or len(graph.get("links", [])) != 21
                or graph.get("routing", {}).get("available") is not True
                or graph.get("ha_service", {}).get("active_backend") != "BACKEND_HQ"
                or graph.get("source_warnings")):
            raise RuntimeError("noc_not_healthy")
    return {"namespace_id": netns_identity(), "ip": CLIENT_IP,
            "peer": PEER, "routes": list(DESTS), "namespace_count": 21}


def qdisc() -> str:
    arr = json.loads(run("ip", "netns", "exec", NS,
                         "tc", "-j", "qdisc", "show", "dev", DEV))
    if not isinstance(arr, list):
        return "FOREIGN"
    root = [x for x in arr if isinstance(x, dict)
            and (x.get("root") is True or x.get("parent") == "root")]
    if not root:
        root = [x for x in arr if isinstance(x, dict)
                and x.get("kind") == "noqueue"]
    if len(root) != 1 or len(arr) != 1:
        return "FOREIGN"
    kind = root[0].get("kind")
    if kind == "noqueue":
        return "BASELINE"
    if kind == "netem" and root[0].get("handle") == HANDLE:
        raw = run("ip", "netns", "exec", NS,
                  "tc", "qdisc", "show", "dev", DEV)
        if re.search(r"\bdelay\s+40(?:\.0+)?ms\b", raw):
            return "OWN_NETEM"
    return "FOREIGN"


def token_check(token: str) -> None:
    if len(token) != 16 or any(c not in "0123456789abcdef" for c in token):
        raise ValueError("invalid_timer_token")


def timer_args(token: str) -> tuple[str, ...]:
    token_check(token)
    return (
        "systemd-run", "--unit=netlab360-s06-hq-" + token,
        "--collect", f"--on-active={TTL}s",
        "--timer-property=AccuracySec=1s",
        "/usr/bin/python3", str(INSTALL), "expire", "--token", token,
    )


def authorize(arg: str) -> None:
    if arg != APPROVAL:
        raise RuntimeError("explicit_human_approval_required")


def audit() -> dict:
    with exclusive():
        if load() is not None:
            raise RuntimeError("previous_experiment_state_requires_review")
        check_management()
        target = check_network(strict_noc=True)
        if qdisc() != "BASELINE":
            raise RuntimeError("existing_qdisc_not_baseline")
        return target


def start(approval: str) -> dict:
    authorize(approval)
    with exclusive():
        if load() is not None:
            raise RuntimeError("previous_experiment_state_requires_review")
        check_management()
        network = check_network(strict_noc=True)
        if qdisc() != "BASELINE":
            raise RuntimeError("foreign_or_existing_qdisc")
        token = secrets.token_hex(8)
        data = {
            "schema": SCHEMA, "token": token, "state": "ARMING",
            "started_at_utc": utc(), "target": f"{NS}/{DEV}",
            "ns_identity": network["namespace_id"],
            "baseline": network, "netem_handle": HANDLE,
            "latency_ms": LATENCY, "ttl_seconds": TTL,
            "scope": "HQ_EGRESS_ONLY", "management_changed": False,
            "root_ownership_checked": True, "human_approval": True,
            "ground_truth_degraded_verified": False,
        }
        save(data)
        try:
            run(*timer_args(token))
            active = run("systemctl", "is-active",
                         "netlab360-s06-hq-" + token + ".timer")
            if active.strip() != "active":
                raise RuntimeError("timer_not_active")
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            # Si el timer no se armó, no se ha ejecutado ninguna mutación.
            data["state"] = "ARMING"
            data["arming_failure_at_utc"] = utc()
            save(data)
            raise
        data["state"] = "ARMED"
        data["armed_at_utc"] = utc()
        save(data)
        data["state"] = "APPLY_PENDING"
        save(data)
        try:
            run("ip", "netns", "exec", NS, "tc", "qdisc",
                "add", "dev", DEV, "root", "handle", HANDLE,
                "netem", "delay", str(LATENCY) + "ms")
            if qdisc() != "OWN_NETEM":
                raise RuntimeError("applied_qdisc_not_identified")
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            data["state"] = "APPLY_UNKNOWN"
            data["apply_error_at_utc"] = utc()
            save(data)
            raise
        data["state"] = "APPLIED"
        data["applied_at_utc"] = utc()
        data["ground_truth_degraded_verified"] = True
        save(data)
        return data


def expire(token: str) -> dict:
    token_check(token)
    # Bloqueo de espera: el watchdog no pierde su disparo si el padre
    # está usando el lock o muere inesperadamente.
    with exclusive(wait=True):
        data = load()
        if data is None or data.get("token") != token:
            raise RuntimeError("watchdog_token_or_state_not_ours")
        if data["state"] in ("RESTORED", "RESTORED_NO_CHANGE", "ESCALATED"):
            return data
        if data["state"] not in ("ARMED", "APPLY_PENDING",
                                 "APPLIED", "APPLY_UNKNOWN"):
            raise RuntimeError("watchdog_state_not_ready")
        try:
            # NO depender de NOC u observabilidad para restaurar;
            # podrían fallar por el propio estímulo.
            if netns_identity() != data["ns_identity"]:
                raise RuntimeError("client_namespace_replaced")
            observed = qdisc()
            if observed == "OWN_NETEM":
                run("ip", "netns", "exec", NS, "tc", "qdisc",
                    "del", "dev", DEV, "root")
                if qdisc() != "BASELINE":
                    raise RuntimeError("baseline_not_recovered")
                data["state"] = "RESTORED"
            elif observed == "BASELINE":
                data["state"] = "RESTORED_NO_CHANGE"
            else:
                raise RuntimeError("foreign_qdisc_preserved")
        except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
            data["state"] = "ESCALATED"
            data["failure"] = f"{type(exc).__name__}: {exc}"[:220]
        data["expired_at_utc"] = utc()
        data["final_qdisc_state"] = qdisc() if data["state"] != "ESCALATED" else "REVIEW"
        save(data)
        return data


def cleanup() -> None:
    with exclusive():
        data = load()
        if data is None or data["state"] not in (
            "RESTORED", "RESTORED_NO_CHANGE"
        ):
            raise RuntimeError("restore_must_be_verified_before_cleanup")
        check_management()
        check_network(strict_noc=True)
        if netns_identity() != data["ns_identity"] or qdisc() != "BASELINE":
            raise RuntimeError("postconditions_not_at_baseline")
        STATE.unlink()


def status() -> dict:
    with exclusive():
        data = load()
        if data is None:
            return {
                "schema": SCHEMA, "state": "NONE",
                "qdisc": qdisc(), "target": f"{NS}/{DEV}",
            }
        return {
            **data, "qdisc": qdisc(),
            "read_at_utc": utc(),
        }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    cmds = p.add_subparsers(dest="action", required=True)
    cmds.add_parser("audit")
    t = cmds.add_parser("start")
    t.add_argument("--approve", required=True)
    cmds.add_parser("status")
    e = cmds.add_parser("expire")
    e.add_argument("--token", required=True)
    cmds.add_parser("cleanup")
    args = p.parse_args()
    os.umask(0o077)
    trusted_install()
    if args.action == "audit":
        data = audit()
        print("S06_042_GUARD_AUDIT=OK_READONLY")
        print("S06_042_TARGET=" + NS + "/" + DEV)
        print("S06_042_QDISC=BASELINE")
    elif args.action == "start":
        data = start(args.approve)
        print("S06_042_TIMER_ARMED_BEFORE_TC=OK")
        print("S06_042_PRODUCTION_QDISC=APPLIED")
        print("S06_042_TOKEN=" + data["token"])
    elif args.action == "expire":
        data = expire(args.token)
        print("S06_042_EXPIRY_STATE=" + data["state"])
    elif args.action == "cleanup":
        cleanup()
        print("S06_042_CLEANUP=OK")
    else:
        data = status()
        print("S06_042_STATE=" + data["state"])
        print("S06_042_QDISC=" + data["qdisc"])
        print("S06_042_STATE_JSON=" +
              json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    print("S06_042_INTERFACE_SCOPE=HQ_CLIENT_EGRESS_ONLY")
    print("S06_042_HOST_MANAGEMENT_TARGETED=NO")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError,
            subprocess.TimeoutExpired) as exc:
        print(f"S06_042_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
