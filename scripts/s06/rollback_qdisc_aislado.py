#!/usr/bin/env python3
"""S06-038B: ensayar restauracion tc real en un namespace SIN conectividad.

El unico entorno que puede cambiarse es nl360-s06-isotest/dummy0, creado
por este modulo con cero IPv4 y sin enlaces externos. ens33, los 21
namespaces NETLAB360 y todo servicio/cliente de produccion estan excluidos.

Instalar el fichero, root-owned (0750), como ruta INSTALL antes de usar.
El timer systemd se programa y se comprueba ANTES de agregar netem.
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

INSTALL = Path("/usr/local/libexec/netlab360/s06-rollback-isotest.py")
DIR = Path("/run/netlab360-s06-isotest")
STATE = DIR / "state.json"
LOCK = DIR / "lock"
NS = "nl360-s06-isotest"
IFACE = "dummy0"
HANDLE = "106:"
TTL = 20
SCHEMA = "NETLAB360_S06_ISOLATED_WATCHDOG_V1"
MGMT_IP = "192.168.47.40/24"
MGMT_GW = "192.168.47.2"
ALLOWED_NEXT = frozenset(
    {"PREPARING", "PREPARED", "ARMING", "ARMED",
     "APPLY_PENDING", "APPLIED", "APPLY_UNKNOWN",
     "RESTORED", "RESTORED_NO_CHANGE", "ESCALATED"}
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def run(*argv: str) -> str:
    p = subprocess.run(argv, capture_output=True, text=True,
                       check=False, timeout=12)
    if p.returncode:
        raise RuntimeError(f"command_failed_{argv[0]}_{p.returncode}: {p.stderr[-250:]}")
    return p.stdout


def verify_installed() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("root_required")
    if Path(__file__) != INSTALL or INSTALL.is_symlink() or not INSTALL.is_file():
        raise RuntimeError("trusted_install_required")
    for path in (INSTALL.parent, INSTALL):
        s = path.lstat()
        if s.st_uid != 0 or s.st_mode & 0o022:
            raise RuntimeError("untrusted_installed_file_or_directory")
    if stat.S_IMODE(INSTALL.stat().st_mode) != 0o750:
        raise RuntimeError("installed_mode_not_0750")


def private_dir() -> None:
    if DIR.is_symlink():
        raise RuntimeError("runtime_symlink")
    if not DIR.exists():
        DIR.mkdir(mode=0o700)
    s = DIR.lstat()
    if (not stat.S_ISDIR(s.st_mode) or s.st_uid != os.geteuid()
            or stat.S_IMODE(s.st_mode) != 0o700):
        raise RuntimeError("runtime_directory_not_private")


@contextmanager
def exclusive(*, wait: bool = False):
    private_dir()
    fd = os.open(LOCK, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        s = os.fstat(fd)
        if (s.st_uid != os.geteuid() or not stat.S_ISREG(s.st_mode)
                or stat.S_IMODE(s.st_mode) != 0o600):
            raise RuntimeError("untrusted_lock")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX if wait else fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("concurrent_test_forbidden") from exc
        yield
    finally:
        os.close(fd)


def read_state() -> dict | None:
    if STATE.is_symlink():
        raise RuntimeError("state_symlink")
    if not STATE.exists():
        return None
    s = STATE.lstat()
    if (not stat.S_ISREG(s.st_mode) or s.st_uid != os.geteuid()
            or stat.S_IMODE(s.st_mode) != 0o600):
        raise RuntimeError("state_not_private")
    data = json.loads(STATE.read_text(encoding="utf-8"))
    if (data.get("schema") != SCHEMA or data.get("state") not in ALLOWED_NEXT
            or not isinstance(data.get("token"), str)):
        raise RuntimeError("invalid_state_schema")
    return data


def save_state(data: dict) -> None:
    private_dir()
    read_state()
    fd, tmp = tempfile.mkstemp(dir=DIR, prefix=".state-")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, STATE)
    finally:
        if os.path.lexists(tmp):
            os.unlink(tmp)


def namespace_names() -> set[str]:
    return {r.split()[0] for r in run("ip", "netns", "list").splitlines()
            if r.strip()}


def management() -> None:
    address = run("ip", "-4", "-o", "addr", "show", "dev", "ens33")
    route = run("ip", "-4", "route", "show", "default")
    if MGMT_IP not in address or f"default via {MGMT_GW} dev ens33" not in route:
        raise RuntimeError("management_not_in_reference")


def namespace_identity() -> list[int]:
    p = Path("/run/netns") / NS
    if p.is_symlink() or not p.exists():
        raise RuntimeError("isolated_namespace_missing")
    s = p.stat()
    return [s.st_dev, s.st_ino]


def inspect_dummy() -> None:
    info = json.loads(run("ip", "-n", NS, "-j", "-d", "link",
                          "show", "dev", IFACE))
    if (len(info) != 1 or info[0].get("ifname") != IFACE
            or info[0].get("linkinfo", {}).get("info_kind") != "dummy"
            or info[0].get("operstate") not in ("UNKNOWN", "UP")):
        raise RuntimeError("unexpected_isolated_device")
    addresses = json.loads(run("ip", "-n", NS, "-j", "addr", "show", "dev", IFACE))
    if len(addresses) != 1:
        raise RuntimeError("isolated_address_ambiguous")
    if any(x.get("family") in ("inet", "inet6")
           for x in addresses[0].get("addr_info", [])):
        raise RuntimeError("isolated_device_has_ip_address")
    routes = run("ip", "-n", NS, "route", "show", "default")
    if routes.strip():
        raise RuntimeError("isolated_namespace_has_default_route")


def qdisc_state(raw: object) -> str:
    if not isinstance(raw, list):
        raise ValueError("invalid_qdisc_json")
    roots = [x for x in raw if isinstance(x, dict)
             and (x.get("root") is True or x.get("parent") == "root")]
    if len(roots) != 1:
        return "FOREIGN"
    q = roots[0]
    if q.get("kind") == "noqueue":
        return "BASELINE"
    if (q.get("kind") == "netem" and
            str(q.get("handle", "")).startswith(HANDLE)):
        return "OWN_NETEM"
    return "FOREIGN"


def qdisc() -> str:
    return qdisc_state(json.loads(run(
        "ip", "netns", "exec", NS,
        "tc", "-j", "qdisc", "show", "dev", IFACE
    )))


def verify_owned_namespace(state: dict) -> None:
    if NS not in namespace_names() or state.get("ns_identity") != namespace_identity():
        raise RuntimeError("test_namespace_identity_changed")
    inspect_dummy()


def prepare() -> dict:
    with exclusive():
        management()
        if read_state() is not None:
            raise RuntimeError("previous_test_state_exists")
        names = namespace_names()
        if len(names) != 21 or NS in names:
            raise RuntimeError("unexpected_namespace_inventory")
        token = secrets.token_hex(8)
        state = {
            "schema": SCHEMA, "token": token,
            "state": "PREPARING", "created_at_utc": utc(),
            "namespace": NS, "device": IFACE, "handle": HANDLE,
            "ttl_seconds": TTL, "network_changes_outside_test": False,
            "ground_truth_verified": False,
        }
        save_state(state)
        # Solo crea un espacio de red nuevo sin veth, IP ni puente.
        run("ip", "netns", "add", NS)
        run("ip", "-n", NS, "link", "add", IFACE, "type", "dummy")
        # Desactivar IPv6 solamente en dummy0 para evitar link-local automatica.
        run("ip", "netns", "exec", NS, "sysctl", "-qw",
            "net.ipv6.conf.dummy0.disable_ipv6=1")
        run("ip", "-n", NS, "link", "set", IFACE, "up")
        inspect_dummy()
        if qdisc() != "BASELINE":
            raise RuntimeError("unexpected_initial_qdisc")
        state["ns_identity"] = namespace_identity()
        state["state"] = "PREPARED"
        state["prepared_at_utc"] = utc()
        save_state(state)
        return state


def timer_command(token: str) -> tuple[str, ...]:
    if (len(token) != 16
            or any(ch not in "0123456789abcdef" for ch in token)):
        raise ValueError("invalid_timer_token")
    return (
        "systemd-run", "--unit=netlab360-s06-isotest-" + token,
        "--collect", f"--on-active={TTL}s",
        "--timer-property=AccuracySec=1s",
        "/usr/bin/python3", str(INSTALL), "expire", "--token", token,
    )


def start() -> dict:
    with exclusive():
        state = read_state()
        if state is None or state["state"] != "PREPARED":
            raise RuntimeError("isolated_test_not_prepared")
        management()
        verify_owned_namespace(state)
        if len(namespace_names()) != 22 or qdisc() != "BASELINE":
            raise RuntimeError("isolated_qdisc_or_inventory_changed")
        token = state["token"]
        state["state"] = "ARMING"
        save_state(state)
        try:
            run(*timer_command(token))
            timer = "netlab360-s06-isotest-" + token + ".timer"
            if run("systemctl", "is-active", timer).strip() != "active":
                raise RuntimeError("watchdog_timer_not_active")
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            state["state"] = "PREPARED"
            state["arm_error_at_utc"] = utc()
            save_state(state)
            raise
        state["state"] = "ARMED"
        state["armed_at_utc"] = utc()
        save_state(state)
        # Una expiracion simultanea acepta APPLY_PENDING y comprueba el estado real.
        state["state"] = "APPLY_PENDING"
        save_state(state)
        try:
            run("ip", "netns", "exec", NS, "tc", "qdisc", "add",
                "dev", IFACE, "root", "handle", HANDLE,
                "netem", "delay", "20ms")
            if qdisc() != "OWN_NETEM":
                raise RuntimeError("installed_qdisc_identity_mismatch")
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            state["state"] = "APPLY_UNKNOWN"
            state["apply_error_at_utc"] = utc()
            save_state(state)
            raise
        state["state"] = "APPLIED"
        state["applied_at_utc"] = utc()
        save_state(state)
        return state


def expire(token: str) -> dict:
    timer_command(token)  # Valida estrictamente el token, sin ejecutar systemd.
    # El timer espera la liberacion del lock; si el proceso principal cae,
    # el kernel libera flock y el watchdog conserva su oportunidad de actuar.
    with exclusive(wait=True):
        state = read_state()
        if state is None or state["token"] != token:
            raise RuntimeError("foreign_timer_or_state")
        if state["state"] in ("RESTORED", "RESTORED_NO_CHANGE", "ESCALATED"):
            return state
        if state["state"] not in (
            "ARMED", "APPLY_PENDING", "APPLIED", "APPLY_UNKNOWN"
        ):
            raise RuntimeError("expiration_not_authorized")
        try:
            management()
            verify_owned_namespace(state)
            observed = qdisc()
            if observed == "BASELINE":
                state["state"] = "RESTORED_NO_CHANGE"
            elif observed == "OWN_NETEM":
                run("ip", "netns", "exec", NS, "tc",
                    "qdisc", "del", "dev", IFACE, "root")
                if qdisc() != "BASELINE":
                    raise RuntimeError("qdisc_not_restored")
                state["state"] = "RESTORED"
            else:
                raise RuntimeError("foreign_qdisc_preserved")
        except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as e:
            state["state"] = "ESCALATED"
            state["failure"] = type(e).__name__ + ": " + str(e)[:200]
        state["expired_at_utc"] = utc()
        save_state(state)
        return state


def cleanup() -> None:
    with exclusive():
        state = read_state()
        if state is None or state["state"] not in (
            "RESTORED", "RESTORED_NO_CHANGE"
        ):
            raise RuntimeError("cannot_cleanup_before_verified_restore")
        management()
        verify_owned_namespace(state)
        if qdisc() != "BASELINE":
            raise RuntimeError("qdisc_not_at_baseline")
        # Solo elimina el dispositivo dummy y el namespace efimero de la prueba.
        run("ip", "-n", NS, "link", "del", IFACE)
        run("ip", "netns", "del", NS)
        if NS in namespace_names():
            raise RuntimeError("isotest_namespace_still_present")
        STATE.unlink()


def status() -> None:
    with exclusive():
        s = read_state()
        if s is None:
            print("S06_038B_STATE=NONE")
            return
        print("S06_038B_STATE=" + s["state"])
        print("S06_038B_TOKEN=" + s["token"])
        print("S06_038B_NAMESPACE=" + s["namespace"])
        print("S06_038B_QDISC=" + qdisc() if NS in namespace_names() else
              "S06_038B_QDISC=NAMESPACE_MISSING")
        if s.get("failure"):
            print("S06_038B_FAILURE=" + s["failure"])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    actions = p.add_subparsers(dest="action", required=True)
    for name in ("prepare", "start", "status", "cleanup"):
        actions.add_parser(name)
    ex = actions.add_parser("expire")
    ex.add_argument("--token", required=True)
    args = p.parse_args()
    os.umask(0o077)
    verify_installed()
    if args.action == "prepare":
        data = prepare()
        print("S06_038B_PREPARED=" + data["token"])
    elif args.action == "start":
        data = start()
        print("S06_038B_WATCHDOG_ARMED=BEFORE_TC")
        print("S06_038B_APPLIED_IN_ISOLATED_DUMMY=YES")
        print("S06_038B_TOKEN=" + data["token"])
    elif args.action == "expire":
        data = expire(args.token)
        print("S06_038B_EXPIRY_STATE=" + data["state"])
    elif args.action == "cleanup":
        cleanup()
        print("S06_038B_CLEANUP=OK")
    else:
        status()
    print("S06_038B_PRODUCTION_NETWORK_CHANGED=NO")
    print("S06_038B_PRODUCTION_QDISC_CHANGED=NO")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, KeyError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"S06_038B_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
