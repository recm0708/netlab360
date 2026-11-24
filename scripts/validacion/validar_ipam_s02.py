#!/usr/bin/env python3
"""NETLAB360 S02: validacion IPAM candidate + colisiones host/Docker (SOLO LECTURA).

Sin --static-only inspecciona rutas IPv4 del host Ubuntu y redes Docker.
NO comprueba rutas existentes en Windows/VMware/VPN externas.
NO provisiona interfaces, no crea redes, no modifica el inventario S01.
"""
from __future__ import annotations

import ipaddress
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("S02_ERROR=PyYAML no instalado") from exc

ROOT = Path(__file__).resolve().parents[2]
B1 = ROOT / "inventario/ipam/topologia-b1.yaml"
S02 = ROOT / "inventario/ipam/topologia-s02.yaml"

EXPECTED_LINKS = {
    "WAN-PRIMARIA-HQ-S1": ("10.78.0.0/30", "R-HQ", "10.78.0.1/30", "R-S1", "10.78.0.2/30", 10),
    "WAN-RESPALDO-HQ-S1": ("10.78.0.4/30", "R-HQ", "10.78.0.5/30", "R-S1", "10.78.0.6/30", 100),
    "WAN-PRIMARIA-HQ-S2": ("10.78.0.8/30", "R-HQ", "10.78.0.9/30", "R-S2", "10.78.0.10/30", 10),
    "WAN-RESPALDO-HQ-S2": ("10.78.0.12/30", "R-HQ", "10.78.0.13/30", "R-S2", "10.78.0.14/30", 100),
}


def require(condition: bool, description: str) -> None:
    if not condition:
        raise ValueError(description)


def network(value: str, label: str) -> ipaddress.IPv4Network:
    net = ipaddress.ip_network(value, strict=True)
    require(isinstance(net, ipaddress.IPv4Network), f"{label}: se requiere IPv4")
    return net


def endpoint(value: str, net: ipaddress.IPv4Network, label: str) -> None:
    iface = ipaddress.ip_interface(value)
    require(iface.version == 4 and iface.network == net,
            f"{label}: interfaz {value} no pertenece con prefijo correcto a {net}")
    require(iface.ip not in (net.network_address, net.broadcast_address),
            f"{label}: extremo reservado en {net}")


def load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path.name}: YAML no es objeto")
    return data


def check_static() -> list[tuple[str, ipaddress.IPv4Network]]:
    base = load(B1)
    spec = load(S02)
    require(base.get("schema_version") == "0.1", "B1 original: esquema inesperado")
    require(spec.get("schema_version") == "0.2", "S02: esquema no es 0.2")
    require(spec.get("status") == "candidate", "S02 no esta marcado como candidate")
    require(spec.get("management_host") == base.get("management_host"),
            "S02 altera la red de gestion protegida B1")
    mg = spec["management_host"]
    require(mg.get("locked") is True and mg.get("interface") == "ens33", "Gestion no protegida")
    require(mg.get("network") == "192.168.47.0/24", "VMnet8 distinta a la de referencia")
    require(mg.get("host_ip") == "192.168.47.40" and mg.get("gateway") == "192.168.47.2",
            "IP/gateway de la gestion modificados")

    sites = spec["sites"]
    require(set(sites) == {"HQ", "S1", "S2"}, "Se requieren exactamente HQ, S1 y S2")
    require(set(base["sites"]) == set(sites), "B1: sedes no coinciden")
    used = [("GESTION_VMNET8", network(mg["network"], "gestion"))]
    vlan_ids = set()
    router_names = set()
    for name in ("HQ", "S1", "S2"):
        site = sites[name]
        old = base["sites"][name]
        require(site.get("status") == "candidate", f"{name}: solo estado candidate")
        require(all(site.get(k) == old.get(k) for k in ("router", "loopback", "vlans")),
                f"{name}: el candidato cambia direcciones/objetos del inventario B1")
        router = site["router"]
        require(router not in router_names, f"Router duplicado: {router}")
        router_names.add(router)
        lo = network(site["loopback"], f"{name} loopback")
        require(lo.prefixlen == 32, f"{name}: loopback no /32")
        used.append((f"{name}_LOOPBACK", lo))
        require(len(site["vlans"]) == 3, f"{name}: se requieren 3 VLAN")
        for vlan in site["vlans"]:
            vid = vlan["id"]
            require(isinstance(vid, int) and vid not in vlan_ids, f"VLAN ID duplicado: {vid}")
            vlan_ids.add(vid)
            sub = network(vlan["subnet"], f"{name} VLAN {vid}")
            endpoint(f"{vlan['gateway']}/{sub.prefixlen}", sub, f"{name} gateway VLAN {vid}")
            used.append((f"{name}_VLAN_{vid}", sub))
    require(len(vlan_ids) == 9, "Se esperaban nueve VLAN unicas")

    links = spec["wan_links"]
    require(len(links) == 4, "S02 requiere exactamente 4 enlaces WAN")
    seen = set()
    existing_links = {link["id"]: link for link in base["wan_links"]}
    for link in links:
        name = link["id"]
        require(name in EXPECTED_LINKS and name not in seen, f"WAN no esperada/duplicada: {name}")
        seen.add(name)
        want = EXPECTED_LINKS[name]
        require(link.get("status") == "candidate", f"{name}: estado no es candidate")
        require(
            (link["subnet"], link["a"]["router"], link["a"]["address"],
             link["b"]["router"], link["b"]["address"], link["ospf_cost"]) == want,
            f"{name}: direcciones, routers o costo distintos al diseno candidato",
        )
        if name in existing_links:
            old = existing_links[name]
            require(all(link[k] == old[k] for k in ("subnet", "ospf_cost", "a", "b")),
                    f"{name}: alteracion inesperada respecto de B1")
        sub = network(link["subnet"], name)
        require(sub.prefixlen == 30, f"{name}: WAN no /30")
        for direction in ("a", "b"):
            require(link[direction]["router"] in router_names, f"{name}: router sin sede")
            endpoint(link[direction]["address"], sub, f"{name} extremo {direction}")
        require(link["a"]["router"] != link["b"]["router"], f"{name}: enlace al mismo router")
        used.append((name, sub))
    require(seen == set(EXPECTED_LINKS), "No coinciden los cuatro enlaces esperados")

    for (a, na), (b, nb) in combinations(used, 2):
        require(not na.overlaps(nb), f"SOLAPAMIENTO_INTERNO={a}:{na} {b}:{nb}")
    print("S02_IPAM_ESTATICO=OK")
    print(f"S02_SEDES={len(sites)} VLAN={len(vlan_ids)} WAN={len(links)} REDES={len(used)}")
    print("B1_HISTORICO_NO_MODIFICADO_POR_ESTA_VALIDACION=SI")
    return used[1:]  # NO cotejar VMnet8 consigo misma en rutas de Ubuntu


def checked(command: list[str]) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
    return result.stdout


def check_live(candidates: list[tuple[str, ipaddress.IPv4Network]]) -> None:
    # El fallo conocido de la comprobacion anterior se debio a IPAM.Config=null.
    routes = json.loads(checked(["ip", "-j", "-4", "route", "show", "table", "all"]))
    require(isinstance(routes, list), "Salida de rutas IPv4 no es lista")
    existing: list[tuple[str, ipaddress.IPv4Network]] = []
    for route in routes:
        dest = route.get("dst")
        if not dest or dest == "default":
            continue
        try:
            subnet = ipaddress.ip_network(dest, strict=False)
        except ValueError as exc:
            raise ValueError(f"Ruta no interpretable: {dest}") from exc
        if subnet.version == 4:
            existing.append((f"HOST:{route.get('dev', 'unknown')}", subnet))
    names = checked(["sudo", "-n", "docker", "network", "ls", "--format", "{{.Name}}"]).splitlines()
    for name in names:
        inspected = json.loads(checked(["sudo", "-n", "docker", "network", "inspect", name]))
        require(isinstance(inspected, list), f"Docker network inspect {name}: no es lista")
        for obj in inspected:
            ipam = obj.get("IPAM") or {}
            # Docker host/none admiten IPAM.Config = null: tratar como lista vacia.
            for cfg in ipam.get("Config") or []:
                subnet = (cfg or {}).get("Subnet")
                if subnet:
                    existing.append((f"DOCKER:{name}", network(subnet, f"Docker {name}")))

    collisions = [
        (label, str(candidate), origin, str(active))
        for label, candidate in candidates
        for origin, active in existing
        if candidate.overlaps(active)
    ]
    print(f"S02_REDES_HOST_DOCKER_REVISADAS={len(existing)}")
    if collisions:
        for item in collisions:
            print("S02_CONFLICTO=" + " | ".join(item))
        raise ValueError(f"{len(collisions)} colisiones con rutas/redes actuales")
    print("S02_COLISIONES_HOST_DOCKER=0")
    print("S02_VALIDACION_LIVE_UBUNTU=OK")
    print("S02_RUTAS_WINDOWS_VMWARE_VPN=NO_VERIFICADAS")
    print("S02_DESPLIEGUE_EJECUTADO=NO")


def main() -> None:
    require(sys.argv[1:] in ([], ["--static-only"]),
            "Uso: python3 scripts/validacion/validar-ipam-s02.py [--static-only]")
    candidates = check_static()
    if sys.argv[1:] == ["--static-only"]:
        print("S02_SOLO_ESTATICO=SI")
        print("S02_LIVE_HOST_DOCKER=NO_EJECUTADO")
    else:
        check_live(candidates)
    print("RESULTADO_VALIDACION_S02=0")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, KeyError, OSError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"S02_VALIDACION_ERROR={exc}", file=sys.stderr)
        print("RESULTADO_VALIDACION_S02=1", file=sys.stderr)
        raise SystemExit(1)
