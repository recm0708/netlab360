#!/usr/bin/env python3
"""NETLAB360 S03 — SoT derivado estrictamente del inventario S02 candidato.

Genera dos artefactos declarativos (JSON SoT y YAML inventario Ansible local).
No despliega, NO conecta a routers, no modifica FRR ni redes.
"""
from __future__ import annotations
import argparse
from datetime import date
import ipaddress
import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "inventario/ipam/topologia-s02.yaml"
DEFAULT = Path.home() / "netlab360-bootstrap/s03/rendered"
CONTAINERS = {"HQ": "nl360-s02-r-hq", "S1": "nl360-s02-r-s1", "S2": "nl360-s02-r-s2"}
WAN_NAMES = {
    "WAN-PRIMARIA-HQ-S1": "s1p",
    "WAN-RESPALDO-HQ-S1": "s1b",
    "WAN-PRIMARIA-HQ-S2": "s2p",
    "WAN-RESPALDO-HQ-S2": "s2b",
}


def build(data: dict) -> tuple[dict, dict]:
    if data.get("schema_version") != "0.2" or set(data["sites"]) != set(CONTAINERS):
        raise ValueError("SoT requiere inventario S02 tres sedes y schema 0.2")
    if data.get("status") != "candidate" or len(data.get("wan_links", [])) != 4:
        raise ValueError("Inventario S02 en estado inesperado")
    devices = {}
    ansible_hosts = {}
    for site in sorted(CONTAINERS):
        row = data["sites"][site]
        hostname = row["router"]
        if hostname != "R-" + site:
            raise ValueError("Inconsistencia router/sede")
        if len(row["vlans"]) != 3:
            raise ValueError("Se esperaban tres VLAN por sede")
        addresses = set()
        vlans = []
        for v in sorted(row["vlans"], key=lambda x: x["id"]):
            n = ipaddress.ip_network(v["subnet"], strict=True)
            gateway = ipaddress.ip_address(v["gateway"])
            if gateway not in n or int(v["id"]) in addresses:
                raise ValueError(f"VLAN invalida {site}: {v}")
            addresses.add(int(v["id"]))
            vlans.append({
                "id": int(v["id"]), "nombre": v["name"],
                "subnet": str(n), "gateway": str(gateway),
                "interface": f"trunk0.{v['id']}",
            })
        wans = []
        for link in data["wan_links"]:
            for side in ("a", "b"):
                if link[side]["router"] != hostname:
                    continue
                prefix = ipaddress.ip_interface(link[side]["address"])
                if prefix.network != ipaddress.ip_network(link["subnet"]):
                    raise ValueError("WAN IP fuera de subred")
                wans.append({
                    "name": link["id"],
                    "interface": WAN_NAMES[link["id"]],
                    "address": str(prefix),
                    "ospf_cost": int(link["ospf_cost"]),
                })
        expected_links = 4 if site == "HQ" else 2
        if len(wans) != expected_links:
            raise ValueError(f"WAN incompletas para {site}")
        devices[hostname] = {
            "site": site,
            "container": CONTAINERS[site],
            "loopback": row["loopback"],
            "vlans": vlans, "wan": sorted(wans, key=lambda x: x["interface"]),
            "desired_status": "candidate",
        }
        ansible_hosts[hostname] = {
            "ansible_connection": "local",
            "nl360_container": CONTAINERS[site],
            "nl360_site": site,
            "nl360_loopback": row["loopback"],
            "nl360_vlans": vlans,
            "nl360_wan": devices[hostname]["wan"],
        }
    sot = {"project": "NETLAB360", "source": str(SOURCE.relative_to(ROOT)),
           "source_revision": data["revision"],
           "source_status": data["status"], "devices": devices,
           "caution": "Desired state only; NOT proof of live FRR or compliance"}
    inv = {"all": {"children": {"routers": {"hosts": ansible_hosts}}}}
    return sot, inv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT)
    args = parser.parse_args()
    sot, inv = build(yaml.safe_load(SOURCE.read_text(encoding="utf-8")))
    dest = args.output_dir.expanduser().resolve()
    if dest == ROOT or ROOT in dest.parents:
        raise ValueError("Salida S03 debe quedar fuera de repositorio para no sobrescribir fuente")
    if dest.is_symlink():
        raise ValueError("Ruta de destino simbolica no autorizada")
    dest.mkdir(parents=True, exist_ok=True)
    for fn in ("sot-s03.json", "inventory-s03.yml"):
        if (dest / fn).is_symlink():
            raise ValueError(f"Destino simbolico {fn}")
    (dest / "sot-s03.json").write_text(
        json.dumps(sot, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (dest / "inventory-s03.yml").write_text(
        yaml.safe_dump(inv, allow_unicode=True, sort_keys=True),
        encoding="utf-8")
    print(f"S03_SOT_JSON={dest / 'sot-s03.json'}")
    print(f"S03_ANSIBLE_INVENTORY={dest / 'inventory-s03.yml'}")
    print("S03_DISPOSITIVOS=3 VLAN=9 WAN_EXTREMOS=8")
    print("S03_SOLO_ESTADO_DESEADO=SI")
    print("S03_DESPLIEGUE_REAL_EJECUTADO=NO")
    print("S03_GENERACION_RESULTADO=0")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"S03_GENERACION_ERROR={type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
