#!/usr/bin/env python3
"""S03: cotejar manifiesto OpenTofu (terraform_data) contra SoT S02.

Solo lectura; no llama a tofu ni ejecuta Docker; no modifica estado.
Uso: python3 scripts/validacion/s03-tofu-manifest.py RUTA_MANIFEST_JSON
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
IPAM = ROOT / "inventario/ipam/topologia-s02.yaml"
SOFT = Path.home() / "netlab360-bootstrap/s03/rendered/sot-s03.json"


def validate_manifest(manifest: dict, src: dict, sha256: str) -> dict[str, int]:
    if manifest.get("scope") != "metadata_only_no_live_network_apply":
        raise ValueError("Manifiesto sin alcance seguro: no es metadata_only")
    if manifest.get("status") != "candidate_manifest":
        raise ValueError("Estado del manifiesto no es candidate_manifest")
    if manifest.get("source_sha256") != sha256:
        raise ValueError("SHA del SoT de OpenTofu no coincide con IPAM")
    mgmt = manifest["management"]
    exp_mgmt = src["management_host"]
    if mgmt != exp_mgmt or not (
            mgmt.get("locked") is True and mgmt.get("interface") == "ens33" and
            mgmt.get("host_ip") == "192.168.47.40" and
            mgmt.get("gateway") == "192.168.47.2"):
        raise ValueError("Guarda VMnet8 distinta del inventario original")
    sites = manifest["sites"]
    links = manifest["wan_links"]
    vlans = manifest["vlans"]
    if set(sites) != {"HQ", "S1", "S2"} or len(links) != 4 or len(vlans) != 9:
        raise ValueError("Cardinalidad SoT/OpenTofu inconsistente")
    for site, row in src["sites"].items():
        expected_site = dict(row, site_id=site)
        if sites[site] != expected_site:
            raise ValueError(f"Sede no coincide con SoT: {site}")
        for vlan in row["vlans"]:
            name = f"{site}-{vlan['id']}"
            expected_vlan = dict(vlan, site=site)
            if vlans.get(name) != expected_vlan:
                raise ValueError(f"VLAN no coincide con SoT: {name}")
    if set(links) != {wan["id"] for wan in src["wan_links"]}:
        raise ValueError("Nombres WAN distintos del SoT")
    for link in src["wan_links"]:
        if links.get(link["id"]) != link:
            raise ValueError(f"WAN no coincide con SoT: {link['id']}")
    return {"sites": len(sites), "links": len(links), "vlans": len(vlans),
            "records": 1+len(sites)+len(links)+len(vlans)}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    args = p.parse_args()
    source_bytes = IPAM.read_bytes()
    raw = yaml.safe_load(source_bytes)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = validate_manifest(manifest, raw, hashlib.sha256(source_bytes).hexdigest())
    print(f"S03_TOFU_SEDES={result['sites']}/3")
    print(f"S03_TOFU_WAN={result['links']}/4")
    print(f"S03_TOFU_VLAN={result['vlans']}/9")
    print(f"S03_TOFU_RECURSOS_ESTADO={result['records']}/17")
    print("S03_TOFU_MANIFESTO_CONSISTENTE=SI")
    print("S03_TOFU_ALCANCE=SOLO_METADATOS")
    print("S03_TOFU_DESPLIEGUE_FRR_LIVE=NO")
    print("S03_TOFU_VALIDACION=OK")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"S03_TOFU_VALIDACION_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
