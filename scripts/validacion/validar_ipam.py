#!/usr/bin/env python3
"""Validador determinista del IPAM B1; no realiza cambios de red ni requiere root."""
from __future__ import annotations

import ipaddress
import sys
from itertools import combinations
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: falta PyYAML. Verificar python3-yaml del entorno Ansible; no instalar globalmente con pip.")

def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

# Rechazamos redes no canónicas para que las comparaciones de prefijos sean deterministas.
def network(value: str, context: str) -> ipaddress.IPv4Network:
    try:
        n = ipaddress.ip_network(value, strict=True)
    except ValueError as e:
        raise ValueError(f"{context}: subred no canónica {value}: {e}") from e
    check(isinstance(n, ipaddress.IPv4Network), f"{context}: solo se admite IPv4")
    return n

def address(value: str, context: str) -> ipaddress.IPv4Address:
    try:
        a = ipaddress.ip_address(value)
    except ValueError as e:
        raise ValueError(f"{context}: dirección no válida: {e}") from e
    check(isinstance(a, ipaddress.IPv4Address), f"{context}: solo se admite IPv4")
    return a

# Una dirección de host debe pertenecer a la red y no ser red ni broadcast.
def host_inside(value: str, n: ipaddress.IPv4Network, context: str) -> None:
    a = address(value, context)
    check(a in n, f"{context}: {a} está fuera de {n}")
    check(a not in (n.network_address, n.broadcast_address),
          f"{context}: {a} es dirección reservada de {n}")

def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 scripts/validacion/validar_ipam.py inventario/ipam/topologia-b1.yaml")

    path = Path(sys.argv[1])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    check(isinstance(data, dict), "IPAM debe ser un mapa YAML")
    check(data.get("schema_version") == "0.1", "Versión de esquema distinta de 0.1")
    check(data.get("status") == "draft", "Este validador espera propuesta en estado draft")

    mgmt = data["management_host"]
    check(mgmt.get("locked") is True, "La red de administración debe estar protegida")
    check(mgmt["interface"] == "ens33", "No alterar interfaz de administración")
    admin = network(mgmt["network"], "management_host.network")
    check(str(admin) == "192.168.47.0/24", "No alterar segmento de gestión VMware")
    host_inside(mgmt["host_ip"], admin, "management_host.host_ip")
    host_inside(mgmt["gateway"], admin, "management_host.gateway")
    check(mgmt["host_ip"] != mgmt["gateway"], "Gestión: host y gateway duplicados")

    sites = data["sites"]
    check(set(sites) >= {"HQ", "S1", "S2"}, "Faltan HQ, S1 o S2 reservada")
    check(sites["S2"]["status"] == "reserved", "S2 todavía solo debe estar reservada")

    used: list[tuple[str, ipaddress.IPv4Network]] = [("VMnet8 (protegida)", admin)]
    vlan_ids: set[int] = set()
    router_names: set[str] = set()

    for site, definition in sites.items():
        router = definition["router"]
        check(router not in router_names, f"Router duplicado: {router}")
        router_names.add(router)
        check(definition["status"] in ("proposed", "reserved"), f"Estado inválido: {site}")
        lo = network(definition["loopback"], f"{site}.loopback")
        check(lo.prefixlen == 32, f"{site}: loopback no /32")
        used.append((f"{site} loopback", lo))
        for vlan in definition["vlans"]:
            vid = vlan["id"]
            check(isinstance(vid, int) and 1 <= vid <= 4094, f"VLAN inválida: {vid}")
            check(vid not in vlan_ids, f"VLAN ID duplicado: {vid}")
            vlan_ids.add(vid)
            subnet = network(vlan["subnet"], f"{site} VLAN {vid}")
            host_inside(vlan["gateway"], subnet, f"{site} VLAN {vid} gateway")
            used.append((f"{site} VLAN {vid}", subnet))

    link_ids: set[str] = set()
    links = data["wan_links"]
    for link in links:
        label = link["id"]
        check(label not in link_ids, f"WAN ID duplicado: {label}")
        link_ids.add(label)
        n = network(link["subnet"], f"WAN {label}")
        check(n.prefixlen == 30, f"WAN {label}: se espera /30")
        check(link["status"] == "proposed", f"WAN {label}: estado inesperado")
        cost = link["ospf_cost"]
        check(isinstance(cost, int) and cost > 0, f"WAN {label}: costo OSPF inválido")
        peers = []
        for end in ("a", "b"):
            ep = link[end]
            check(ep["router"] in router_names, f"WAN {label}: router no definido")
            iface = ipaddress.ip_interface(ep["address"])
            check(iface.version == 4 and iface.network == n,
                  f"WAN {label}: dirección/prefijo incorrectos en extremo {end}")
            host_inside(str(iface.ip), n, f"WAN {label} extremo {end}")
            peers.append((ep["router"], iface.ip))
        check(peers[0][0] != peers[1][0], f"WAN {label}: mismo router a ambos lados")
        check(peers[0][1] != peers[1][1], f"WAN {label}: direcciones duplicadas")
        used.append((f"WAN {label}", n))

    check(len(links) >= 2, "Faltan WAN primaria y de respaldo")
    for (label_a, subnet_a), (label_b, subnet_b) in combinations(used, 2):
        check(not subnet_a.overlaps(subnet_b),
              f"Solapamiento: {label_a} {subnet_a} y {label_b} {subnet_b}")
    print("VALIDACIÓN B1: OK")
    print(f"Estado: {data['status']} (sin redes desplegadas)")
    print(f"Sedes: {len(sites)} | VLAN: {len(vlan_ids)} | WAN: {len(links)}")
    print(f"Redes/subredes revisadas: {len(used)} (incluye VMnet8)")
    print("Sin solapamientos internos ni con VMnet8; falta validar rutas reales del host y Docker.")

if __name__ == "__main__":
    try:
        main()
    except (KeyError, TypeError, ValueError, OSError) as exc:
        print(f"VALIDACIÓN B1: ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
