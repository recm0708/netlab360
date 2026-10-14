#!/usr/bin/env python3
"""Gate SOLO LECTURA para usar configuraciones OpenTofu+Ansible en B2 FRR.
No crea redes, no ejecuta apply y no revela terraform.tfstate.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ART=Path.home()/"netlab360-bootstrap/iac/s01"
RENDER=ART/"rendered"
MANIFEST=ART/"manifest.json"
SOT=ROOT/"inventario/ipam/topologia-b1.yaml"
COMPARE=ROOT/"scripts/validacion/validar-iac-frr.py"

def run(*cmd):
    result=subprocess.run(list(cmd), cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise ValueError("Comando no aprobado: "+" ".join(map(str,cmd))+"\n"+result.stderr)
    return result.stdout.strip()

def main():
    assert sys.argv[1:]==[], "Uso sin argumentos"
    assert MANIFEST.is_file() and not MANIFEST.is_symlink()
    assert RENDER.is_dir() and not RENDER.is_symlink()
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["inventory_sha256"]==hashlib.sha256(SOT.read_bytes()).hexdigest()
    assert manifest["topology_status"]=="candidate_only" and manifest["s2_reserved"] is True
    assert set(manifest["sites"])=={"HQ","S1"}
    assert manifest["sites"]["HQ"]["router"]=="R-HQ"
    assert manifest["sites"]["S1"]["router"]=="R-S1"
    links={link["id"]:link for link in manifest["wan_links"]}
    assert set(links)=={"WAN-PRIMARIA-HQ-S1","WAN-RESPALDO-HQ-S1"}
    assert links["WAN-PRIMARIA-HQ-S1"]["ospf_cost"]==10
    assert links["WAN-RESPALDO-HQ-S1"]["ospf_cost"]==100
    mgmt=manifest["management_guard"]
    assert mgmt["locked"] is True and mgmt["interface"]=="ens33"
    assert mgmt["network"]=="192.168.47.0/24"
    assert mgmt["host_ip"]=="192.168.47.40" and mgmt["gateway"]=="192.168.47.2"
    addr=run("ip","-4","-br","address","show","ens33")
    gw=run("ip","-4","route","show","default")
    assert "192.168.47.40/24" in addr and "default via 192.168.47.2 dev ens33" in gw
    assert "VALIDACIÓN B1: OK" in run("python3","scripts/validacion/validar-ipam.py",str(SOT))
    assert {p.name for p in RENDER.iterdir()}=={"R-HQ.frr.conf","R-S1.frr.conf"}
    for router in ("R-HQ","R-S1"):
        assert not (RENDER/f"{router}.frr.conf").is_symlink()
    checked=run("python3",str(COMPARE),str(RENDER))
    assert "IAC_CONFIG_FIEL_A_B2=SI" in checked
    print("IAC_B2_CONFIGDIR="+str(RENDER))
    print("IAC_B2_SOT_SHA256=OK")
    print("IAC_B2_MGMT_ENS33_VMNET8=PROTEGIDA")
    print("IAC_B2_SITIOS=HQ,S1 | S2=RESERVADA | WAN=2")
    print("IAC_B2_COSTOS_OSPF=10,100")
    print("IAC_B2_CONFIGS_COMPLIANT=SI")
    print("IAC_B2_PRECHECK=0")

if __name__=="__main__":
    try: main()
    except (AssertionError, ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("IAC_B2_PRECHECK=1: "+str(exc),file=sys.stderr)
        sys.exit(1)
