#!/usr/bin/env python3
"""NETLAB360 S05: LACP real HQ VLAN120; propiedad exclusiva y reversión selectiva.

Solo añade un cliente S05 al switch S02 existente. NO toca FRR, WAN,
tr-sw, ha-hq21, ha-hq23, ens33 ni el bridge br0 existente fuera de
agregar/retirar UN puerto lógico de S05.
Acciones: plan, precheck, up, status, down. Up/down exigen confirmación.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts/validacion/s05-lacp-integracion-precheck.py"
BASE = Path.home() / "netlab360-bootstrap/s05/lacp-multisede"
STATE = BASE / "state-hq.json"
OWNER = "NETLAB360_S05_LACP_HQ_V1"
SITE = "HQ"
SW = "nl360-s02-sw-hq"
CLIENT = "nl360-s05-lacp-hq"
GW = "10.70.20.1"
IP = "10.70.20.40/24"
VID = 120
SW_BOND = "s5bond0"
CLIENT_BOND = "bond0"
SW_SLAVES = ("s5p1", "s5p2")
CLIENT_SLAVES = ("s5c1", "s5c2")
PROTECTED = ("br0", "tr-sw", "a110", "a120", "a130", "ha-hq21", "ha-hq23")
UNITS = (
    "netlab360-s04-exporter", "netlab360-s05-noc",
    "netlab360-s05-ha-backend-hq", "netlab360-s05-ha-backend-s1",
    "netlab360-s05-ha-frontal-hq", "netlab360-s05-ha-monitor-s2",
)


def cmd(*parts: str, root: bool = False, check: bool = True, timeout: int = 20) -> str:
    full = (["sudo", "-n"] if root else []) + list(parts)
    result = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(
            f"Fallo {result.returncode}: {' '.join(parts)}: "
            + (result.stderr or result.stdout)[-700:]
        )
    return result.stdout


def ip_ns(ns: str, *parts: str, check: bool = True) -> str:
    return cmd("ip", "-n", ns, *parts, root=True, check=check)


def ns_exec(ns: str, *parts: str, check: bool = True, timeout: int = 20) -> str:
    return cmd("ip", "netns", "exec", ns, *parts, root=True, check=check, timeout=timeout)


def netns() -> set[str]:
    return {line.split()[0] for line in cmd("ip", "netns", "list", root=True).splitlines()
            if line.strip()}


def management() -> dict[str, str]:
    a = cmd("ip", "-4", "-o", "address", "show", "dev", "ens33")
    r = cmd("ip", "-4", "route", "show", "table", "main")
    if "192.168.47.40/24" not in a or "default via 192.168.47.2 dev ens33" not in r:
        raise RuntimeError("IP/ruta de gestión distinta de baseline")
    return {"ens33": a, "routes": r}


def links(ns: str) -> dict[str, dict]:
    items = json.loads(ns_exec(ns, "ip", "-j", "-d", "link", "show"))
    return {item["ifname"]: item for item in items}


def protected_snapshot() -> dict:
    devices = links(SW)
    if not set(PROTECTED).issubset(devices):
        raise RuntimeError("Puerto de S02/HA protegido ausente")
    vlans = ns_exec(SW, "bridge", "vlan", "show")
    # Capturar pertenencia de VLAN para cada puerto, sin depender de líneas de
    # salida del puerto nuevo S05 que se añadirán después.
    rows = {}
    current = None
    for raw in vlans.splitlines():
        if raw.startswith("port "):
            continue
        values = raw.split()
        if not values:
            continue
        if values[0].isdigit() and current:
            rows.setdefault(current, []).append(" ".join(values))
        elif len(values) >= 2 and values[1].isdigit():
            current = values[0]
            rows.setdefault(current, []).append(" ".join(values[1:]))
    if not set(PROTECTED).issubset(rows):
        raise RuntimeError("Inventario VLAN incompleto en HQ")
    return {
        "ports": {name: {
            "ifindex": devices[name]["ifindex"],
            "mac": devices[name].get("address"),
            "master": devices[name].get("master"),
        } for name in PROTECTED},
        "vlans": {name: rows[name] for name in PROTECTED},
    }


def assert_protected(before: dict, *, before_cleanup: bool = False) -> None:
    current = protected_snapshot()
    if before_cleanup:
        # El MAC automático de br0 puede elegirse de un puerto nuevo; permitir
        # retirar SOLO dispositivos S05 sin relajar IFINDEX/VLAN ni otros MAC.
        # Tras la limpieza se exige nuevamente el MAC original del bridge.
        current = {
            **current,
            "ports": {
                **current["ports"],
                "br0": {
                    **current["ports"]["br0"],
                    "mac": before["ports"]["br0"]["mac"],
                },
            },
        }
    if current != before:
        raise RuntimeError("Cambio en puertos protegidos o sus VLAN")


def assert_services() -> None:
    for unit in UNITS:
        if cmd("systemctl", "is-active", unit, check=False).strip() != "active":
            raise RuntimeError(f"Servicio no activo: {unit}")
    # La API del NOC puede entregar transitoriamente una vista sin rutas.
    # Nunca registrar OK por un JSON parcial: comprobar hasta tres vistas.
    last_error = None
    for attempt in range(1, 4):
        try:
            with urlopen("http://127.0.0.1:9130/api/v1/graph", timeout=8) as resp:
                graph = json.load(resp)
            ha = graph.get("ha_service") if isinstance(graph, dict) else None
            routing = graph.get("routing") if isinstance(graph, dict) else None
            routes = routing.get("routes") if isinstance(routing, dict) else None
            ha = ha if isinstance(ha, dict) else {}
            routes = routes if isinstance(routes, dict) else {}
            s1 = routes.get("S1") if isinstance(routes.get("S1"), dict) else {}
            s2 = routes.get("S2") if isinstance(routes.get("S2"), dict) else {}
            if (ha.get("available") is True
                    and ha.get("active_backend") == "BACKEND_HQ"
                    and s1.get("dev") == "s1p"
                    and s2.get("dev") == "s2p"):
                print("S05_LACP_HQ_SERVICIOS_HA_FIB=OK")
                return
            last_error = "observación NOC sin HA principal y rutas S1/S2 completas"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        print(f"S05_LACP_HQ_NOC_FIB_NO_VALIDADO_INTENTO_{attempt}=SI",
              flush=True)
        if attempt < 3:
            time.sleep(1)
    raise RuntimeError(f"NOC no confirmó HA/FIB tras 3 observaciones: {last_error}")


def identity() -> None:
    if os.geteuid() == 0 or cmd("hostname").strip() != "netlab360-lab":
        raise RuntimeError("Host o usuario no autorizado")
    if cmd("git", "-C", str(ROOT), "status", "--porcelain").strip():
        raise RuntimeError("Git con cambios locales")
    management()


def plan() -> None:
    print(f"S05_LACP_HQ_PLAN=SW:{SW} VLAN:{VID} CLIENTE:{CLIENT}")
    print(f"S05_LACP_HQ_BONDS=SW:{SW_BOND} CLIENTE:{CLIENT_BOND}")
    print(f"S05_LACP_HQ_DOS_VETH={','.join(SW_SLAVES)} <-> {','.join(CLIENT_SLAVES)}")
    print(f"S05_LACP_HQ_IP={IP} GW={GW}")
    print("S05_LACP_HQ_NO_MODIFICAR=WAN_FRR_TR_SW_ENS33_HTTP_HA")
    print("S05_LACP_HQ_PLAN=OK_SIN_CAMBIOS")


def precheck() -> dict:
    identity()
    if STATE.exists() or STATE.is_symlink():
        raise RuntimeError("Estado S05 LACP HQ ya existe: usar status o down")
    print("========== PRECHECK INTEGRAL S05 ==========")
    result = cmd(sys.executable, str(VALIDATOR), "precheck", timeout=100)
    if "S05_LACP_PRECHECK=OK_SIN_CAMBIOS_DE_CONFIGURACION" not in result:
        raise RuntimeError("Validador LACP no completó")
    print(result, end="")
    names = netns()
    if CLIENT in names or SW not in names:
        raise RuntimeError("Namespace cliente ya ocupado o switch ausente")
    devs = set(links(SW))
    if {SW_BOND, *SW_SLAVES, *CLIENT_SLAVES} & devs:
        raise RuntimeError("Nombre de interfaz LACP HQ ya utilizado")
    before = {"mgmt": management(), "switch": protected_snapshot()}
    assert_services()
    print("S05_LACP_HQ_RECURSOS_NUEVOS=LIBRES")
    print("S05_LACP_HQ_PRECHECK=OK_SIN_CAMBIOS")
    return before


def write_state(data: dict) -> None:
    BASE.mkdir(parents=True, exist_ok=True, mode=0o700)
    f = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=BASE, delete=False,
                                         encoding="utf-8") as out:
            f = Path(out.name)
            json.dump(data, out, indent=2, ensure_ascii=False)
            out.write("\n")
        os.chmod(f, 0o600)
        os.replace(f, STATE)
    finally:
        if f and f.exists():
            f.unlink()


def read_state() -> dict:
    if not STATE.is_file() or STATE.is_symlink():
        raise RuntimeError("Estado S05 LACP HQ ausente o symlink")
    data = json.loads(STATE.read_text(encoding="utf-8"))
    if (data.get("owner") != OWNER or data.get("site") != SITE
            or data.get("sw") != SW or data.get("client") != CLIENT
            or not re.fullmatch(r"S05_HQ_[0-9a-f]{16}", data.get("alias", ""))):
        raise RuntimeError("Estado de propiedad inválido")
    return data


def alias_of(ns: str, dev: str) -> str | None:
    item = links(ns).get(dev)
    return item.get("ifalias", "") if item else None


def assert_owned(dev: str, ns: str, data: dict) -> None:
    value = alias_of(ns, dev)
    if value is not None and value != data["alias"]:
        raise RuntimeError(f"ABORTAR: identidad de recurso desconocida {ns}/{dev} ({value})")


def set_alias(ns: str, dev: str, data: dict) -> None:
    ip_ns(ns, "link", "set", "dev", dev, "alias", data["alias"])


def bond_ports(ns: str, dev: str, expected: int, attempts: int = 22) -> None:
    output = ""
    for i in range(attempts):
        output = ns_exec(ns, "cat", f"/proc/net/bonding/{dev}", check=False)
        if "IEEE 802.3ad" in output and re.search(
            rf"^\s*Number of ports:\s*{expected}\s*$", output, re.M
        ):
            print(f"S05_LACP_HQ_{ns}_PUERTOS_ACTIVOS={expected}")
            return
        time.sleep(1)
    raise RuntimeError(f"Agregador {ns}/{dev} no alcanzó {expected}: " + output[-400:])


def ping_verified(ns: str, target: str, *,
                  prefix: str = "S05_LACP_HQ_PING",
                  attempts: int = 3) -> None:
    """Comprueba conectividad estabilizada: reintentos acotados, sin falsear OK.

    Timeout del proceso (VM) y error de ICMP son distintos y ambos se
    registran. Nunca declaramos conectividad si todas las pruebas fallaron.
    """
    if attempts < 1 or attempts > 3:
        raise ValueError("Número de intentos fuera del contrato 1..3")
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            ns_exec(ns, "ping", "-n", "-c", "2", "-W", "2",
                    target, timeout=15)
            print(f"{prefix}_{target}=OK",
                  f"INTENTO={attempt}", flush=True)
            return
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            last = exc
            reason = ("TIMEOUT_PROCESO" if isinstance(
                exc, subprocess.TimeoutExpired) else "ICMP_O_COMANDO_ERROR")
            print(f"{prefix}_{target}_INTENTO_{attempt}={reason}",
                  flush=True)
            if attempt < attempts:
                time.sleep(1)
    raise RuntimeError(
        f"{prefix}_{target}=NO_VALIDADO tras {attempts} intentos; "
        f"último error: {last}"
    ) from last


def status(data: dict, ping: bool = True) -> None:
    if data.get("status") != "active":
        raise RuntimeError("Estado S05 no está activo")
    if CLIENT not in netns():
        raise RuntimeError("Cliente LACP S05 HQ no existe")
    for ns, names in ((SW, (SW_BOND, *SW_SLAVES)),
                      (CLIENT, (CLIENT_BOND, *CLIENT_SLAVES))):
        for name in names:
            if alias_of(ns, name) != data["alias"]:
                raise RuntimeError(f"Alias de propiedad alterado: {ns}/{name}")
    vlans = ns_exec(SW, "bridge", "vlan", "show", "dev", SW_BOND)
    if not re.search(rf"(?<!\d){VID}(?!\d).*PVID.*Untagged", vlans, re.I):
        raise RuntimeError("VLAN 120 sin PVID untagged en bond")
    addr = ip_ns(CLIENT, "-4", "-br", "address", "show", "dev", CLIENT_BOND)
    if IP not in addr:
        raise RuntimeError("Dirección IP de bond cliente inesperada")
    route = ip_ns(CLIENT, "-4", "route", "show", "default")
    if f"default via {GW} dev {CLIENT_BOND}" not in route:
        raise RuntimeError("Gateway del cliente no corresponde")
    bond_ports(SW, SW_BOND, 2, attempts=12)
    bond_ports(CLIENT, CLIENT_BOND, 2, attempts=12)
    if ping:
        for target in (GW, "10.70.20.23", "10.71.20.21", "10.72.20.20"):
            ping_verified(CLIENT, target)
    if management() != data["before"]["mgmt"]:
        raise RuntimeError("Red de gestión cambió respecto del precheck")
    assert_protected(data["before"]["switch"])
    assert_services()
    print("S05_LACP_HQ_S02_PUERTOS_VLAN=CONSERVADOS")
    print("S05_LACP_HQ_STATUS=OK")


def cleanup(data: dict) -> None:
    if data.get("status") not in ("creating", "active", "cleanup_pending"):
        raise RuntimeError("Estado de LACP HQ no autoriza limpieza")
    if management() != data["before"]["mgmt"]:
        raise RuntimeError("Gestión cambió: bloquear limpieza")
    assert_protected(data["before"]["switch"], before_cleanup=True)
    names = netns()
    if CLIENT in names:
        pids = cmd("ip", "netns", "pids", CLIENT, root=True).split()
        if pids:
            raise RuntimeError(f"Cliente S05 contiene procesos no terminados: {pids}")
    # Validar TODAS las identidades antes de borrar cualquier recurso.
    for ns, devs in ((SW, (SW_BOND, *SW_SLAVES, *CLIENT_SLAVES)),
                     (CLIENT, (CLIENT_BOND, *CLIENT_SLAVES))):
        if ns not in names:
            continue
        for dev in devs:
            assert_owned(dev, ns, data)
    for dev in (*SW_SLAVES, *CLIENT_SLAVES):
        if dev in links(SW):
            ip_ns(SW, "link", "delete", "dev", dev)
    if SW_BOND in links(SW):
        ip_ns(SW, "link", "delete", "dev", SW_BOND)
    if CLIENT in names:
        cmd("ip", "netns", "delete", CLIENT, root=True)
    if any(dev in links(SW) for dev in (SW_BOND, *SW_SLAVES, *CLIENT_SLAVES)):
        raise RuntimeError("Hay interfaces S05 HQ residuales")
    if CLIENT in netns():
        raise RuntimeError("Namespace cliente S05 HQ residual")
    assert_protected(data["before"]["switch"])
    if management() != data["before"]["mgmt"]:
        raise RuntimeError("Host perdió baseline de gestión")
    STATE.unlink()
    print("S05_LACP_HQ_LIMPIEZA=OK")
    print("S05_LACP_HQ_S02_CONSERVADO=SI")


def up() -> None:
    before = precheck()
    data = {
        "owner": OWNER, "site": SITE, "sw": SW, "client": CLIENT,
        "status": "creating", "alias": "S05_HQ_" + secrets.token_hex(8),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "before": before,
    }
    write_state(data)
    try:
        cmd("ip", "netns", "add", CLIENT, root=True)
        ip_ns(CLIENT, "link", "set", "lo", "up")
        for ns, bond, mac in (
                (SW, SW_BOND, "fe:10:05:70:01:20"),
                (CLIENT, CLIENT_BOND, "fe:20:05:70:01:20")):
            ip_ns(ns, "link", "add", bond, "type", "bond",
                  "mode", "802.3ad", "miimon", "100", "lacp_rate", "fast")
            set_alias(ns, bond, data)
            # MAC locales y altas: no competir con MAC autoseleccionada de br0.
            ip_ns(ns, "link", "set", "dev", bond, "address", mac)
            ip_ns(ns, "link", "set", bond, "type", "bond",
                  "xmit_hash_policy", "layer3+4")
        for sw_dev, client_dev in zip(SW_SLAVES, CLIENT_SLAVES):
            ip_ns(SW, "link", "add", sw_dev, "type", "veth",
                  "peer", "name", client_dev)
            set_alias(SW, sw_dev, data)
            set_alias(SW, client_dev, data)
            ip_ns(SW, "link", "set", client_dev, "netns", CLIENT)
            set_alias(CLIENT, client_dev, data)
            ip_ns(SW, "link", "set", sw_dev, "master", SW_BOND)
            ip_ns(CLIENT, "link", "set", client_dev, "master", CLIENT_BOND)
        # Ningún esclavo entra directamente a br0: puerto L2 ÚNICO = bond.
        ip_ns(SW, "link", "set", SW_BOND, "master", "br0")
        ns_exec(SW, "bridge", "vlan", "del", "dev", SW_BOND, "vid", "1",
                check=False)
        ns_exec(SW, "bridge", "vlan", "add", "dev", SW_BOND, "vid",
                str(VID), "pvid", "untagged")
        ip_ns(CLIENT, "address", "add", IP, "dev", CLIENT_BOND)
        ip_ns(CLIENT, "link", "set", CLIENT_BOND, "up")
        ip_ns(SW, "link", "set", SW_BOND, "up")
        for sw_dev, client_dev in zip(SW_SLAVES, CLIENT_SLAVES):
            ip_ns(SW, "link", "set", sw_dev, "up")
            ip_ns(CLIENT, "link", "set", client_dev, "up")
        ip_ns(CLIENT, "route", "add", "default", "via", GW, "dev", CLIENT_BOND)
        # Marcar activo provisionalmente para ejecutar contrato completo de
        # status. Si falla, se hace rollback de estos recursos S05.
        data["status"] = "active"
        write_state(data)
        status(data)
        print("S05_LACP_HQ_DESPLIEGUE=OK")
    except BaseException:
        print("S05_LACP_HQ_DESPLIEGUE=ERROR_ROLLBACK_SELECTIVO",
              file=sys.stderr)
        try:
            cleanup(read_state())
        except Exception as err:
            data["status"] = "cleanup_pending"
            write_state(data)
            print(f"S05_LACP_HQ_CLEANUP_PENDIENTE={err}", file=sys.stderr)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "precheck", "up", "status", "down"))
    parser.add_argument("--confirm-isolated", action="store_true")
    args = parser.parse_args()
    if args.action in ("up", "down") and not args.confirm_isolated:
        parser.error("up/down requieren --confirm-isolated")
    if args.action not in ("up", "down") and args.confirm_isolated:
        parser.error("--confirm-isolated solo para up/down")
    if args.action == "plan":
        plan()
        return
    identity()
    BASE.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (BASE / "lock-hq").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        if args.action == "precheck":
            precheck()
        elif args.action == "up":
            up()
        elif args.action == "status":
            status(read_state())
        elif args.action == "down":
            cleanup(read_state())


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print(f"S05_LACP_HQ_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
