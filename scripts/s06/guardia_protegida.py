#!/usr/bin/env python3
"""S06-038A: guardia root-owned para validar watchdog sin alterar redes.

Instalar una COPIA protegida en /usr/local/libexec/netlab360/s06-guardia.py.
La unica accion programable es vencer un marcador de estado bajo /run.
No existe ningun subcomando que aplique o elimine una qdisc.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys
import tempfile
from urllib.request import urlopen

INSTALL = Path("/usr/local/libexec/netlab360/s06-guardia.py")
RUN_DIR = Path("/run/netlab360-s06")
STATE = RUN_DIR / "guardia.json"
LOCK = RUN_DIR / "guardia.lock"

NAMESPACE = "nl360-s02-h-hq-120"
DEVICE = "eth0"
IP = "10.70.20.20"
PREFIX = 24
GATEWAY = "10.70.20.1"
HOST_IP = "192.168.47.40/24"
HOST_GW = "192.168.47.2"
MIN_TTL = 5
MAX_TTL = 30
SCHEMA = "NETLAB360_S06_ROOT_GUARD_TEST_V1"

# Importante: este codigo NO tiene rutas de ejecucion tc add/del/replace,
# ni permite pasar namespace o dispositivo por argumentos.
def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def trusted_install() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("root_required")
    if Path(__file__) != INSTALL or INSTALL.is_symlink() or not INSTALL.is_file():
        raise RuntimeError("protected_install_required")
    for target in (INSTALL.parent, INSTALL):
        info = target.lstat()
        if info.st_uid != 0 or (info.st_mode & 0o022):
            raise RuntimeError("untrusted_owner_or_writable_path")
    mode = stat.S_IMODE(INSTALL.stat().st_mode)
    if mode not in (0o500, 0o550, 0o700, 0o750):
        raise RuntimeError("invalid_executable_mode")


def command(*args: str) -> str:
    result = subprocess.run(args, check=False, text=True,
                            capture_output=True, timeout=12)
    if result.returncode:
        raise RuntimeError(
            "readonly_command_failed " + " ".join(args[:3])
            + " rc=" + str(result.returncode)
        )
    return result.stdout


def baseline() -> dict:
    host = command("ip", "-4", "-o", "addr", "show", "dev", "ens33")
    route = command("ip", "-4", "route", "show", "default")
    if HOST_IP not in host or f"default via {HOST_GW} dev ens33" not in route:
        raise RuntimeError("management_not_at_reference")
    names = {line.split()[0] for line in command(
        "ip", "netns", "list"
    ).splitlines() if line.strip()}
    if len(names) != 21 or NAMESPACE not in names:
        raise RuntimeError("unexpected_namespaces")

    nic = json.loads(command(
        "ip", "-n", NAMESPACE, "-j", "addr", "show", "dev", DEVICE
    ))
    if len(nic) != 1 or nic[0].get("ifname") != DEVICE or nic[0].get("operstate") != "UP":
        raise RuntimeError("unexpected_client_interface")
    ipv4 = [x for x in nic[0].get("addr_info", []) if x.get("family") == "inet"]
    if (len(ipv4) != 1 or ipv4[0].get("local") != IP
            or ipv4[0].get("prefixlen") != PREFIX):
        raise RuntimeError("unexpected_client_ip")

    routes = json.loads(command(
        "ip", "-n", NAMESPACE, "-j", "route", "show", "default"
    ))
    if (len(routes) != 1 or routes[0].get("gateway") != GATEWAY
            or routes[0].get("dev") != DEVICE
            or routes[0].get("dst") != "default"):
        raise RuntimeError("unexpected_client_gateway")

    q = json.loads(command(
        "ip", "netns", "exec", NAMESPACE,
        "tc", "-j", "qdisc", "show", "dev", DEVICE
    ))
    roots = [x for x in q if isinstance(x, dict) and (
        x.get("root") is True or x.get("parent") == "root"
    )]
    if (len(roots) != 1 or roots[0].get("kind") != "noqueue"
            or any(x.get("kind") == "netem" for x in q)):
        raise RuntimeError("foreign_or_unexpected_qdisc")
    return {
        "management": HOST_IP,
        "gateway": HOST_GW,
        "namespace": NAMESPACE, "interface": DEVICE,
        "client_ip": f"{IP}/{PREFIX}",
        "client_gateway": GATEWAY, "qdisc": "noqueue",
        "namespace_count": len(names),
        "checked_at_utc": utc(),
        "network_changes": False,
    }


def ensure_dir() -> None:
    if RUN_DIR.is_symlink():
        raise RuntimeError("run_directory_symlink")
    if not RUN_DIR.exists():
        RUN_DIR.mkdir(mode=0o700)
    info = RUN_DIR.lstat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != 0
            or stat.S_IMODE(info.st_mode) != 0o700):
        raise RuntimeError("run_directory_not_root_private")


def read_state() -> dict | None:
    if STATE.is_symlink():
        raise RuntimeError("state_symlink_forbidden")
    if not STATE.exists():
        return None
    info = STATE.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0
            or stat.S_IMODE(info.st_mode) != 0o600):
        raise RuntimeError("state_not_root_private")
    data = json.loads(STATE.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise RuntimeError("state_schema_mismatch")
    return data


def write_state(data: dict) -> None:
    ensure_dir()
    # No reemplazar un estado symlink ni aceptar permisos ambiguos.
    read_state()
    fd, name = tempfile.mkstemp(prefix=".guardia-", dir=RUN_DIR)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, STATE)
    finally:
        if os.path.lexists(name):
            os.unlink(name)


@contextmanager
def exclusive():
    ensure_dir()
    fd = os.open(LOCK, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if (info.st_uid != 0 or not stat.S_ISREG(info.st_mode)
                or stat.S_IMODE(info.st_mode) != 0o600):
            raise RuntimeError("lock_not_root_private")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("concurrent_guard_operation") from exc
        yield
    finally:
        os.close(fd)


def timer_args(token: str, ttl: int) -> list[str]:
    if len(token) != 16 or any(x not in "0123456789abcdef" for x in token):
        raise ValueError("invalid_token")
    if type(ttl) is not int or not MIN_TTL <= ttl <= MAX_TTL:
        raise ValueError("invalid_ttl")
    return [
        "systemd-run", "--unit=netlab360-s06-guard-" + token,
        "--collect", "--on-active=" + str(ttl) + "s",
        "--timer-property=AccuracySec=1s",
        "/usr/bin/python3", str(INSTALL), "expire", "--token", token,
    ]


def schedule_test(ttl: int) -> dict:
    if type(ttl) is not int or not MIN_TTL <= ttl <= MAX_TTL:
        raise ValueError("invalid_ttl")
    with exclusive():
        if read_state() is not None:
            raise RuntimeError("existing_state_requires_cleanup")
        current = baseline()
        token = secrets.token_hex(8)
        plan = {
            "schema": SCHEMA, "token": token,
            "state": "ARMING", "created_at_utc": utc(),
            "ttl_seconds": ttl, "baseline": current,
            "network_changes": False, "qdisc_changes": False,
            "operation": "root_only_state_timer_noop",
        }
        write_state(plan)
        args = timer_args(token, ttl)
        try:
            command(*args)
        except (RuntimeError, subprocess.TimeoutExpired):
            plan["state"] = "TIMER_ARM_ERROR"
            plan["updated_at_utc"] = utc()
            write_state(plan)
            raise
        plan["state"] = "ARMED_NOOP"
        plan["updated_at_utc"] = utc()
        write_state(plan)
        return plan


def expire(token: str) -> dict:
    if len(token) != 16 or any(c not in "0123456789abcdef" for c in token):
        raise ValueError("invalid_token")
    with exclusive():
        plan = read_state()
        if plan is None or plan.get("token") != token:
            raise RuntimeError("timer_token_or_state_mismatch")
        if plan["state"] not in ("ARMED_NOOP", "EXPIRED_NOOP", "ESCALATED"):
            raise RuntimeError("unexpected_timer_state")
        if plan["state"] in ("EXPIRED_NOOP", "ESCALATED"):
            return plan
        try:
            observed = baseline()
        except (ValueError, RuntimeError, OSError):
            plan["state"] = "ESCALATED"
            plan["reason"] = "baseline_changed_no_automated_mutation"
        else:
            plan["state"] = "EXPIRED_NOOP"
            plan["final_baseline"] = observed
        plan["updated_at_utc"] = utc()
        write_state(plan)
        return plan


def cleanup() -> None:
    with exclusive():
        plan = read_state()
        if plan is None:
            raise RuntimeError("no_state_to_clean")
        if plan["state"] != "EXPIRED_NOOP":
            raise RuntimeError("cannot_clean_unverified_or_armed_state")
        baseline()
        STATE.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("audit")
    p = sub.add_parser("arm-test")
    p.add_argument("--ttl", type=int, default=8)
    p = sub.add_parser("expire")
    p.add_argument("--token", required=True)
    sub.add_parser("status")
    sub.add_parser("cleanup")
    args = parser.parse_args()
    os.umask(0o077)
    trusted_install()
    if args.action == "audit":
        result = baseline()
        print("S06_038_ROOT_AUDIT=OK")
        print("S06_038_BASELINE=" + json.dumps(result, sort_keys=True))
    elif args.action == "arm-test":
        plan = schedule_test(args.ttl)
        print("S06_038_ROOT_TIMER_ARMED=OK")
        print("S06_038_UNIT=netlab360-s06-guard-" + plan["token"])
    elif args.action == "expire":
        plan = expire(args.token)
        print("S06_038_EXPIRY_STATE=" + plan["state"])
    elif args.action == "status":
        with exclusive():
            plan = read_state()
        print("S06_038_ROOT_STATE=" + (plan["state"] if plan else "NONE"))
        if plan:
            print("S06_038_TOKEN=" + plan["token"])
            print("S06_038_ROOT_NETWORK_CHANGED=" + str(plan["network_changes"]))
    elif args.action == "cleanup":
        cleanup()
        print("S06_038_ROOT_STATE_CLEANED=OK")
    print("S06_038_NETEM_APPLIED=NO")
    print("S06_038_REAL_QDISC_ROLLBACK=NOT_IMPLEMENTED")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError,
            json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print("S06_038_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
