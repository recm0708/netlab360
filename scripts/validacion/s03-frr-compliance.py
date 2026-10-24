#!/usr/bin/env python3
"""NETLAB360 S03: compliance READ-ONLY de costos WAN OSPF FRR vs SoT.

Verifica propiedad (IDs) de 3 contenedores del despliegue S02 y que las
interfaces WAN tengan los costos OSPF declarados. No configura FRR, no reinicia
servicios ni modifica rutas. Puede ejecutarse en Ansible por router.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

HOME = Path.home()
SOT = HOME / "netlab360-bootstrap/s03/rendered/sot-s03.json"
WAN_STATE = HOME / "netlab360-bootstrap/s02/wan-links-state.json"
OWNER = "NETLAB360_S02_WAN_LINKS_V1"
FULL = {"R-HQ": 4, "R-S1": 2, "R-S2": 2}


def parse_frr_costs(raw: str) -> dict[str, int]:
    """Extraer costos SOLO de stanza interface, no falsos positivos globales."""
    costs: dict[str, int] = {}
    current = None
    for raw_line in raw.splitlines():
        line = raw_line.rstrip()
        if line.startswith("interface "):
            current = line[len("interface "):].strip()
            continue
        if current and line.startswith((" ", "\t")):
            match = re.fullmatch(r"\s+ip ospf cost\s+(\d+)\s*", line)
            if match:
                if current in costs:
                    raise ValueError(f"Costo OSPF duplicado en {current}")
                costs[current] = int(match.group(1))
            continue
        if line and not line.startswith((" ", "\t")):
            current = None
    return costs


def command(*args: str) -> str:
    p = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if p.returncode:
        raise RuntimeError(f"Comando fallo: {' '.join(args)}; rc={p.returncode}\n{p.stderr[-1600:]}")
    return p.stdout


def expected(sot: dict, router: str) -> dict[str, int]:
    device = sot["devices"][router]
    result = {}
    for wan in device["wan"]:
        name = wan["interface"]
        if name in result:
            raise ValueError(f"WAN duplicada {router}/{name}")
        cost = int(wan["ospf_cost"])
        if cost not in (10, 100):
            raise ValueError(f"Costo fuera de perfil S02: {name}={cost}")
        result[name] = cost
    if len(result) != (4 if router == "R-HQ" else 2):
        raise ValueError(f"WAN esperadas no coinciden {router}")
    return result


def compare_costs(reference: dict[str, int], observed: dict[str, int]) -> list[str]:
    return [f"{name} esperado={cost} observado={observed.get(name, 'AUSENTE')}"
            for name, cost in sorted(reference.items())
            if observed.get(name) != cost]


def audit(routers: list[str]) -> int:
    if not SOT.is_file() or not WAN_STATE.is_file():
        raise RuntimeError("Faltan SoT o state WAN existentes; no ejecutar contra red desconocida")
    sot = json.loads(SOT.read_text(encoding="utf-8"))
    state = json.loads(WAN_STATE.read_text(encoding="utf-8"))
    if (sot.get("source_status") != "candidate" or
            set(sot.get("devices", {})) != set(FULL) or
            state.get("owner") != OWNER or
            set(state.get("ids", {})) != set(FULL)):
        raise RuntimeError("Propiedad WAN/SoT no validada")
    host_ip = command("ip", "-4", "-o", "addr", "show", "dev", "ens33")
    gateway = command("ip", "-4", "route", "show", "default")
    if ("192.168.47.40/24" not in host_ip or
            "default via 192.168.47.2 dev ens33" not in gateway):
        raise RuntimeError("Red de gestion inesperada")
    totals = 0
    drifts = []
    for router in routers:
        cname = sot["devices"][router]["container"]
        data = json.loads(command("sudo", "-n", "docker", "inspect", cname))[0]
        if (data["Id"] != state["ids"][router] or
                not data["State"]["Running"] or
                data["HostConfig"]["NetworkMode"] != "none" or
                (data["Config"].get("Labels") or {}).get("com.docker.compose.project") != "netlab360-s02-wan"):
            raise RuntimeError(f"Contenedor FRR no pertenece al S02 activo: {router}")
        running = command("sudo", "-n", "docker", "exec", cname,
                          "vtysh", "-c", "show running-config")
        got = parse_frr_costs(running)
        wanted = expected(sot, router)
        discrepancies = compare_costs(wanted, got)
        for interface in sorted(wanted):
            actual = got.get(interface)
            if actual == wanted[interface]:
                print(f"S03_COSTO_{router}_{interface}=COMPLIANT ESPERADO={wanted[interface]} OBSERVADO={actual}")
            else:
                print(f"S03_COSTO_{router}_{interface}=NON_COMPLIANT ESPERADO={wanted[interface]} OBSERVADO={actual if actual is not None else 'AUSENTE'}")
        neighbor_output = command("sudo", "-n", "docker", "exec", cname,
                                  "vtysh", "-c", "show ip ospf neighbor")
        full = sum("Full" in row for row in neighbor_output.splitlines())
        if full != FULL[router]:
            discrepancies.append(f"Vecinos Full esperados={FULL[router]} observados={full}")
        totals += len(wanted)
        print(f"S03_ROUTER_{router}_COSTOS_REVISADOS={len(wanted)} OSPF_FULL={full}")
        drifts += [f"{router}/{item}" for item in discrepancies]
    if drifts:
        for item in drifts:
            print(f"S03_DRIFT_DETECTADO={item}")
        print(f"S03_COMPLIANCE_RESULTADO=NON_COMPLIANT TOTAL_DRIFT={len(drifts)}")
        return 2
    print(f"S03_COSTOS_WAN_COMPLIANT={totals}/{totals}")
    print("S03_COMPLIANCE_RESULTADO=COMPLIANT")
    print("S03_COMPLIANCE_READONLY=SI")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--router", choices=sorted(FULL),
                        help="Sin indicar se comprueban los tres routers")
    args = parser.parse_args()
    selected = [args.router] if args.router else sorted(FULL)
    return audit(selected)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"S03_COMPLIANCE_ERROR={type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
