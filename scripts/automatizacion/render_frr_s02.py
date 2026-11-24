#!/usr/bin/env python3
"""NETLAB360 S02 - Renderizado determinista FRR para tres sedes.

Solo lee inventario candidato y genera archivos de configuracion (sin Docker/IP).
Las interfaces se crean por un orquestador posterior: WAN s1p/s1b/s2p/s2b
y LAN trunk0.<VLAN>. No modifica S01 ni archivos de FRRouting activos.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = ROOT / "inventario/ipam/topologia-s02.yaml"
WAN_IFACES = {
    "WAN-PRIMARIA-HQ-S1": "s1p",
    "WAN-RESPALDO-HQ-S1": "s1b",
    "WAN-PRIMARIA-HQ-S2": "s2p",
    "WAN-RESPALDO-HQ-S2": "s2b",
}


def render(data: dict) -> dict[str, str]:
    if data.get("status") != "candidate" or data.get("schema_version") != "0.2":
        raise ValueError("Solo se admiten inventarios S02 candidate schema 0.2")
    sites = data["sites"]
    if set(sites) != {"HQ", "S1", "S2"} or len(data["wan_links"]) != 4:
        raise ValueError("S02 requiere HQ/S1/S2 y cuatro WAN")
    by_router = {value["router"]: value for value in sites.values()}
    if len(by_router) != 3:
        raise ValueError("Nombre de router duplicado")
    out = {}
    for router in sorted(by_router):
        site = by_router[router]
        lines = [
            "! NETLAB360 S02 - Configuracion generada por inventario; candidata",
            "frr version 10.7.1",
            "frr defaults traditional",
            f"hostname {router}",
            "log stdout",
            "service integrated-vtysh-config",
            "!",
            "interface lo",
            " ip ospf area 0",
            "!",
        ]
        for vlan in sorted(site["vlans"], key=lambda v: v["id"]):
            lines.extend([
                f"interface trunk0.{vlan['id']}",
                f" description {vlan['name']}",
                " ip ospf area 0",
                "!",
            ])
        active_wans = []
        for link in data["wan_links"]:
            if router not in (link["a"]["router"], link["b"]["router"]):
                continue
            dev = WAN_IFACES.get(link["id"])
            if not dev:
                raise ValueError(f"WAN desconocida: {link['id']}")
            active_wans.append(dev)
            lines.extend([
                f"interface {dev}",
                f" description {link['id']}",
                " ip ospf area 0",
                " ip ospf network point-to-point",
                f" ip ospf cost {link['ospf_cost']}",
                "!",
            ])
        lines.extend([
            "router ospf",
            f" ospf router-id {site['loopback'].split('/')[0]}",
            " passive-interface default",
        ])
        for dev in sorted(active_wans):
            lines.append(f" no passive-interface {dev}")
        lines.extend(["!", "line vty", "!", ""])
        out[router] = "\n".join(lines)
    if len(out) != 3:
        raise ValueError("No se generaron tres configuraciones")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=pathlib.Path, default=DEFAULT_INVENTORY)
    ap.add_argument("--output-dir", type=pathlib.Path, required=True)
    args = ap.parse_args()
    data = yaml.safe_load(args.inventory.read_text(encoding="utf-8"))
    rendered = render(data)
    dest = args.output_dir.expanduser().resolve()
    # No aceptar escritura en carpeta del inventario, scripts ni configs B2 de referencia.
    repo = ROOT.resolve()
    if dest == repo or dest == repo / "topologias" / "b2-frr" / "configs" or dest == repo / "inventario" / "ipam":
        raise ValueError("Destino prohibido para no sobrescribir S01")
    if any((dest / f"{name}.frr.conf").is_symlink() for name in rendered):
        raise ValueError("Destino contiene enlaces simbolicos no autorizados")
    dest.mkdir(parents=True, exist_ok=True)
    for router, text in rendered.items():
        p = dest / f"{router}.frr.conf"
        p.write_text(text, encoding="utf-8")
        p.chmod(0o640)
        print(f"S02_CONFIG_GENERADA={p} | bytes={p.stat().st_size}")
    print("S02_ROUTER_CONFIGS=3")
    print("RESULTADO_RENDER_S02=0")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError, yaml.YAMLError) as e:
        print(f"ERROR_RENDER_S02={e}", file=sys.stderr)
        sys.exit(1)
