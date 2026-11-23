#!/usr/bin/env python3
"""S06-040: restauración tc real en par veth efímero y aislado.

ÚNICO destino mutable: namespace nl360-s06-veth-a, interfaz s06va0,
creados por este script. Su peer vive en nl360-s06-veth-b; no existe
ningún enlace ni ruta hacia NETLAB360 productivo. Al arrancar el ensayo,
programa y verifica un timer systemd ANTES de instalar netem.
La opción --crash-controller provoca SIGKILL al controlador tras guardar
APPLIED para demostrar recuperación por timer independiente.
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
import signal
import stat
import subprocess
import sys
import tempfile

INSTALL = Path("/usr/local/libexec/netlab360/s06-veth-rollback.py")
RUN_DIR = Path("/run/netlab360-s06-veth")
STATE = RUN_DIR / "state.json"
LOCK = RUN_DIR / "lock"
NSA = "nl360-s06-veth-a"
NSB = "nl360-s06-veth-b"
IFA = "s06va0"
IFB = "s06vb0"
IPA = "10.255.239.1"
IPB = "10.255.239.2"
PREFIX = 30
HANDLE = "140:"
TTL = 25
SCHEMA = "NETLAB360_S06_VETH_ISOLATED_ROLLBACK_V1"
HOST_IP = "192.168.47.40/24"
HOST_GW = "192.168.47.2"
STATES = frozenset({
    "PREPARING", "PREPARED", "ARMING", "ARMED", "APPLY_PENDING",
    "APPLIED", "APPLY_UNKNOWN", "RESTORED", "RESTORED_NO_CHANGE", "ESCALATED",
})


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def run(*argv: str) -> str:
    proc = subprocess.run(argv, check=False, capture_output=True,
                          text=True, timeout=12)
    if proc.returncode:
        raise RuntimeError(
            "command_failed=" + " ".join(argv[:4])
            + f" rc={proc.returncode} {proc.stderr[-150:]}"
        )
    return proc.stdout


def trusted_install() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("root_required")
    if Path(__file__) != INSTALL or not INSTALL.is_file() or INSTALL.is_symlink():
        raise RuntimeError("protected_install_required")
    for p in (INSTALL.parent, INSTALL):
        info = p.lstat()
        if info.st_uid != 0 or (info.st_mode & 0o022):
            raise RuntimeError("untrusted_install_owner")
    if stat.S_IMODE(INSTALL.stat().st_mode) != 0o750:
        raise RuntimeError("install_mode_not_0750")


def private_directory() -> None:
    if RUN_DIR.is_symlink():
        raise RuntimeError("runtime_symlink_forbidden")
    if not RUN_DIR.exists():
        RUN_DIR.mkdir(mode=0o700)
    s = RUN_DIR.lstat()
    if (not stat.S_ISDIR(s.st_mode) or s.st_uid != os.geteuid()
            or stat.S_IMODE(s.st_mode) != 0o700):
        raise RuntimeError("runtime_permissions_untrusted")


@contextmanager
def exclusive(*, wait: bool = False):
    private_directory()
    fd = os.open(LOCK, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        s = os.fstat(fd)
        if (s.st_uid != os.geteuid() or not stat.S_ISREG(s.st_mode)
                or stat.S_IMODE(s.st_mode) != 0o600):
            raise RuntimeError("untrusted_lock")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX if wait else
                        fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("concurrent_operation_blocked") from exc
        yield
    finally:
        os.close(fd)


def read_state() -> dict | None:
    if STATE.is_symlink():
        raise RuntimeError("state_symlink_forbidden")
    if not STATE.exists():
        return None
    s = STATE.lstat()
    if (not stat.S_ISREG(s.st_mode) or s.st_uid != os.geteuid()
            or stat.S_IMODE(s.st_mode) != 0o600):
        raise RuntimeError("state_permissions_untrusted")
    data = json.loads(STATE.read_text(encoding="utf-8"))
    if (data.get("schema") != SCHEMA or data.get("state") not in STATES
            or not isinstance(data.get("token"), str)):
        raise RuntimeError("state_schema_untrusted")
    return data


def save_state(data: dict) -> None:
    private_directory()
    read_state()  # rechaza reemplazo de symlink o estado ajeno.
    fd, name = tempfile.mkstemp(prefix=".state-", dir=RUN_DIR)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, STATE)
    finally:
        if os.path.lexists(name):
            os.unlink(name)


def management() -> None:
    host = run("ip", "-4", "-o", "addr", "show", "dev", "ens33")
    routes = run("ip", "-4", "route", "show", "default")
    if HOST_IP not in host or f"default via {HOST_GW} dev ens33" not in routes:
        raise RuntimeError("management_not_in_reference")


def names() -> set[str]:
    return {r.split()[0] for r in run("ip", "netns", "list").splitlines()
            if r.strip()}


def identity(name: str) -> list[int]:
    if name not in (NSA, NSB):
        raise ValueError("namespace_not_in_catalog")
    path = Path("/run/netns") / name
    if not path.exists() or path.is_symlink():
        raise RuntimeError("temporary_namespace_missing")
    s = path.stat()
    return [s.st_dev, s.st_ino]


def qdisc_state(value: object) -> str:
    if not isinstance(value, list):
        raise ValueError("qdisc_invalid_json")
    roots = [
        v for v in value if isinstance(v, dict)
        and (v.get("root") is True or v.get("parent") == "root")
    ]
    if len(roots) != 1:
        return "FOREIGN"
    x = roots[0]
    if x.get("kind") == "noqueue":
        return "BASELINE"
    if (x.get("kind") == "netem"
            and str(x.get("handle", "")) == HANDLE):
        return "OWN_NETEM"
    return "FOREIGN"


def current_qdisc() -> str:
    raw = json.loads(run("ip", "netns", "exec", NSA,
                         "tc", "-j", "qdisc", "show", "dev", IFA))
    return qdisc_state(raw)


def inspect_end(name: str, interface: str, address: str) -> dict:
    if (name, interface) not in ((NSA, IFA), (NSB, IFB)):
        raise ValueError("veth_end_not_in_catalog")
    links = json.loads(run("ip", "-n", name, "-j", "-d", "link", "show"))
    if sorted(x.get("ifname") for x in links) != ["lo", interface] and \
       {x.get("ifname") for x in links} != {"lo", interface}:
        raise RuntimeError("isolated_namespace_has_foreign_links")
    nic = next(x for x in links if x.get("ifname") == interface)
    if (nic.get("linkinfo", {}).get("info_kind") != "veth"
            or nic.get("operstate") != "UP"):
        raise RuntimeError("veth_not_up_or_not_veth")
    addr = json.loads(run("ip", "-n", name, "-j", "addr", "show",
                          "dev", interface))
    if len(addr) != 1:
        raise RuntimeError("unexpected_veth_addresses")
    inet = [x for x in addr[0].get("addr_info", [])
            if x.get("family") == "inet"]
    inet6 = [x for x in addr[0].get("addr_info", [])
             if x.get("family") == "inet6"]
    if (len(inet) != 1 or inet[0].get("local") != address
            or inet[0].get("prefixlen") != PREFIX or inet6):
        raise RuntimeError("isolation_ip_addresses_changed")
    if run("ip", "-n", name, "route", "show", "default").strip():
        raise RuntimeError("isolated_namespace_has_default_route")
    return {
        "name": name, "interface": interface, "ip": address,
        "ifindex": nic.get("ifindex"), "link_index": nic.get("link_index"),
        "link_netnsid": nic.get("link_netnsid"), "kind": "veth",
    }


def inspect_both() -> dict:
    a = inspect_end(NSA, IFA, IPA)
    b = inspect_end(NSB, IFB, IPB)
    if (a["ifindex"] is None or b["ifindex"] is None
            or a["ifindex"] == b["ifindex"]):
        # Namespaces have independent ifindexes; equality is allowed, but this
        # condition only checks ifindex exists. See below.
        if a["ifindex"] is None or b["ifindex"] is None:
            raise RuntimeError("veth_ifindex_missing")
    # link_index may be absent in older iproute2 JSON. If present, compare.
    if a["link_index"] is not None and a["link_index"] != b["ifindex"]:
        raise RuntimeError("veth_peer_index_a_mismatch")
    if b["link_index"] is not None and b["link_index"] != a["ifindex"]:
        raise RuntimeError("veth_peer_index_b_mismatch")
    return {"a": a, "b": b}


def verify_owned_pair(state: dict) -> dict:
    live = names()
    if not {NSA, NSB} <= live or len(live) != 23:
        raise RuntimeError("isolated_namespace_inventory_changed")
    if (state.get("namespace_identity_a") != identity(NSA)
            or state.get("namespace_identity_b") != identity(NSB)):
        raise RuntimeError("isolated_namespace_identity_changed")
    return inspect_both()


def probe() -> str:
    # Solo 3 paquetes de bajo volumen en enlace punto a punto del ensayo.
    return run("ip", "netns", "exec", NSA, "ping", "-n",
               "-c", "3", "-i", "0.2", "-W", "2", IPB)


def prepare() -> dict:
    with exclusive():
        management()
        if read_state() is not None:
            raise RuntimeError("previous_test_state_exists")
        existing = names()
        if len(existing) != 21 or NSA in existing or NSB in existing:
            raise RuntimeError("unexpected_pretest_namespace_inventory")
        data = {
            "schema": SCHEMA, "state": "PREPARING",
            "token": secrets.token_hex(8), "created_at_utc": now(),
            "ttl": TTL, "namespace_a": NSA, "namespace_b": NSB,
            "interface_a": IFA, "interface_b": IFB,
            "production_changed": False,
            "ground_truth_verified": False,
        }
        save_state(data)
        run("ip", "netns", "add", NSA)
        run("ip", "netns", "add", NSB)
        run("ip", "-n", NSA, "link", "add", IFA,
            "type", "veth", "peer", "name", IFB)
        run("ip", "-n", NSA, "link", "set", IFB, "netns", NSB)
        for ns, interface, ip in ((NSA, IFA, IPA), (NSB, IFB, IPB)):
            run("ip", "netns", "exec", ns, "sysctl", "-qw",
                f"net.ipv6.conf.{interface}.disable_ipv6=1")
            run("ip", "-n", ns, "addr", "add", f"{ip}/{PREFIX}", "dev", interface)
            run("ip", "-n", ns, "link", "set", interface, "up")
        data["namespace_identity_a"] = identity(NSA)
        data["namespace_identity_b"] = identity(NSB)
        data["links"] = inspect_both()
        if current_qdisc() != "BASELINE":
            raise RuntimeError("isolated_veth_qdisc_initial_not_baseline")
        data["baseline_probe"] = probe()
        data["state"] = "PREPARED"
        data["prepared_at_utc"] = now()
        save_state(data)
        return data


def timer_args(token: str) -> tuple[str, ...]:
    if len(token) != 16 or any(x not in "0123456789abcdef" for x in token):
        raise ValueError("invalid_timer_token")
    return (
        "systemd-run", "--unit=netlab360-s06-veth-" + token,
        "--collect", f"--on-active={TTL}s",
        "--timer-property=AccuracySec=1s",
        "/usr/bin/python3", str(INSTALL), "expire", "--token", token,
    )


def start(crash: bool = False) -> dict:
    with exclusive():
        data = read_state()
        if data is None or data["state"] != "PREPARED":
            raise RuntimeError("test_not_prepared")
        management()
        verify_owned_pair(data)
        if current_qdisc() != "BASELINE":
            raise RuntimeError("unexpected_qdisc_before_start")
        data["state"] = "ARMING"
        save_state(data)
        token = data["token"]
        try:
            run(*timer_args(token))
            active = run("systemctl", "is-active",
                         "netlab360-s06-veth-" + token + ".timer")
            if active.strip() != "active":
                raise RuntimeError("watchdog_timer_not_active")
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            data["state"] = "PREPARED"
            data["timer_failed_at_utc"] = now()
            save_state(data)
            raise
        data["state"] = "ARMED"
        data["armed_at_utc"] = now()
        save_state(data)
        data["state"] = "APPLY_PENDING"
        save_state(data)
        try:
            run("ip", "netns", "exec", NSA, "tc", "qdisc", "add",
                "dev", IFA, "root", "handle", HANDLE,
                "netem", "delay", "40ms")
            if current_qdisc() != "OWN_NETEM":
                raise RuntimeError("netem_not_owned_after_apply")
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            data["state"] = "APPLY_UNKNOWN"
            data["apply_failure_at_utc"] = now()
            save_state(data)
            raise
        data["state"] = "APPLIED"
        data["applied_at_utc"] = now()
        save_state(data)
        print("S06_040_TIMER_ARMED_BEFORE_TC=OK", flush=True)
        print("S06_040_NETEM_ISOLATED_VETH=APPLIED", flush=True)
        if crash:
            print("S06_040_CONTROLLER_SIMULATED_SIGKILL=NOW", flush=True)
            os.kill(os.getpid(), signal.SIGKILL)
        return data


def expire(token: str) -> dict:
    timer_args(token)
    # Watchdog must wait for controller flock instead of failing and
    # losing its only chance to restore the experiment after TTL.
    with exclusive(wait=True):
        data = read_state()
        if data is None or data.get("token") != token:
            raise RuntimeError("foreign_timer_state_or_token")
        if data["state"] in ("RESTORED", "RESTORED_NO_CHANGE", "ESCALATED"):
            return data
        if data["state"] not in (
            "ARMED", "APPLY_PENDING", "APPLIED", "APPLY_UNKNOWN"
        ):
            raise RuntimeError("expiration_from_wrong_state")
        try:
            management()
            verify_owned_pair(data)
            state = current_qdisc()
            if state == "BASELINE":
                data["state"] = "RESTORED_NO_CHANGE"
            elif state == "OWN_NETEM":
                run("ip", "netns", "exec", NSA, "tc",
                    "qdisc", "del", "dev", IFA, "root")
                if current_qdisc() != "BASELINE":
                    raise RuntimeError("qdisc_not_restored")
                data["state"] = "RESTORED"
                data["recovery_probe"] = probe()
            else:
                raise RuntimeError("foreign_qdisc_preserved")
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
            data["state"] = "ESCALATED"
            data["failure"] = type(exc).__name__ + ": " + str(exc)[:220]
        data["expired_at_utc"] = now()
        save_state(data)
        return data


def cleanup() -> None:
    with exclusive():
        data = read_state()
        if data is None or data["state"] != "RESTORED":
            raise RuntimeError("cannot_cleanup_without_verified_rollback")
        management()
        verify_owned_pair(data)
        if current_qdisc() != "BASELINE":
            raise RuntimeError("qdisc_not_baseline_do_not_cleanup")
        probe()
        run("ip", "-n", NSA, "link", "del", IFA)
        run("ip", "netns", "del", NSA)
        run("ip", "netns", "del", NSB)
        remaining = names()
        if NSA in remaining or NSB in remaining or len(remaining) != 21:
            raise RuntimeError("temporary_namespace_cleanup_incomplete")
        STATE.unlink()


def status() -> None:
    with exclusive():
        data = read_state()
        if data is None:
            print("S06_040_STATE=NONE")
            return
        print("S06_040_STATE=" + data["state"])
        print("S06_040_TOKEN=" + data["token"])
        print("S06_040_EXPERIMENT=" + NSA + "/" + IFA)
        if NSA in names():
            try:
                print("S06_040_QDISC=" + current_qdisc())
            except (OSError, RuntimeError, ValueError):
                print("S06_040_QDISC=UNKNOWN_REVIEW")
        else:
            print("S06_040_QDISC=NAMESPACE_MISSING")
        if data.get("failure"):
            print("S06_040_FAILURE=" + data["failure"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("prepare", "status", "cleanup"):
        sub.add_parser(name)
    s = sub.add_parser("start")
    s.add_argument("--crash-controller", action="store_true")
    e = sub.add_parser("expire")
    e.add_argument("--token", required=True)
    args = parser.parse_args()
    os.umask(0o077)
    trusted_install()
    if args.action == "prepare":
        d = prepare()
        print("S06_040_PREPARED=" + d["token"])
    elif args.action == "start":
        d = start(args.crash_controller)
        print("S06_040_START=OK")
        print("S06_040_TOKEN=" + d["token"])
    elif args.action == "expire":
        d = expire(args.token)
        print("S06_040_EXPIRY_STATE=" + d["state"])
    elif args.action == "cleanup":
        cleanup()
        print("S06_040_CLEANUP=OK")
    elif args.action == "status":
        status()
    print("S06_040_PRODUCTION_INTERVENTION=NO")
    print("S06_040_TRAINING_LABELS=NONE")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError,
            json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print("S06_040_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
