#!/usr/bin/env python3
"""S03: validar que el plan OpenTofu SOLAMENTE crea 17 terraform_data.

Este script lee JSON de 'tofu show -json PLAN' y rechaza deletes, updates,
replaces, proveedores externos, recursos fuera de alcance o cardinalidad
distinta. NO aplica ni modifica state o infraestructura.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys


def verify_plan(plan: dict) -> dict:
    changes = plan.get("resource_changes", [])
    if len(changes) != 17:
        raise ValueError(f"Plan requiere 17 recursos, obtuvo {len(changes)}")
    groups = {"management_guard":set(), "site":set(), "wan":set(), "vlan":set()}
    allowed_prefixes = (
        "terraform_data.management_guard",
        'terraform_data.site["',
        'terraform_data.wan["',
        'terraform_data.vlan["',
    )
    for item in changes:
        addr = item.get("address", "")
        if item.get("type") != "terraform_data":
            raise ValueError(f"Plan contiene tipo ajeno: {addr}")
        if item.get("change", {}).get("actions") != ["create"]:
            raise ValueError(f"Plan no es creación exclusiva: {addr}")
        if item.get("provider_name") not in (None, "terraform.io/builtin/terraform"):
            raise ValueError(f"Provider no permitido: {addr}")
        if not addr.startswith(allowed_prefixes):
            raise ValueError(f"Dirección inesperada: {addr}")
        group = item.get("name")
        if group not in groups or addr in groups[group]:
            raise ValueError(f"Recurso fuera de alcance/duplicado: {addr}")
        groups[group].add(addr)
    expected = {"management_guard":1, "site":3, "wan":4, "vlan":9}
    count = {name:len(addrs) for name,addrs in groups.items()}
    if count != expected:
        raise ValueError(f"Plan no contiene 1+3+4+9: {count}")
    if groups["management_guard"]!={"terraform_data.management_guard"}:
        raise ValueError("Falta guarda VMnet8")
    return count


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("plan_json",type=Path)
    args=p.parse_args()
    counts=verify_plan(json.loads(args.plan_json.read_text(encoding="utf-8")))
    print(f"S03_PLAN_GUARDA={counts['management_guard']}")
    print(f"S03_PLAN_SEDES={counts['site']}")
    print(f"S03_PLAN_WAN={counts['wan']}")
    print(f"S03_PLAN_VLAN={counts['vlan']}")
    print("S03_PLAN_SOLO_TERRAFORM_DATA=17/17")
    print("S03_PLAN_ACCIONES_EXCLUSIVAS=CREATE")
    print("S03_PLAN_VALIDADO=OK")


if __name__=="__main__":
    try:
        main()
    except Exception as e:
        print(f"S03_PLAN_ERROR={type(e).__name__}: {e}",file=sys.stderr)
        sys.exit(1)
