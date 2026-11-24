#!/usr/bin/env python3
"""NETLAB360 S03: experimento controlado FRR OSPF BACKUP R-S1/s1b.

Acciones:
  inspect: readonly, estado actual y ownership
  inject --snapshot-confirmado: requiere baseline COMPLIANT, escribe costo s1b
     100 -> 150 solo en R-S1, deja registro de propiedad y rollback automático
     si cualquier validación posterior falla.
  reconcile: recupera únicamente s1b costo 100 desde SoT con idempotencia;
     ejecutado por Ansible; no escribe si ya es 100.

Ejecutar exclusivamente bajo Ansible become sudo.ws; HOME original preservado.
No toca interfaces, IPs, rutas del host, ens33, OSPF primarios ni archivos FRR.
NO ejecuta "write memory", pues el drift es transitorio del running-config.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HOME = Path.home()
ROOT = HOME / "proyectos/netlab360"
STATE = HOME / "netlab360-bootstrap/s03/drift-s1b-state.json"
SOT = HOME / "netlab360-bootstrap/s03/rendered/sot-s03.json"
WAN_STATE = HOME / "netlab360-bootstrap/s02/wan-links-state.json"
LAN_STATE = HOME / "netlab360-bootstrap/s02/lan-vlan-state.json"
MODULE = ROOT / "scripts/validacion/s03_frr_compliance.py"
MARKER = "NETLAB360_S03_DRIFT_R-S1_S1B_V1"
ROUTERS = {"R-HQ":"nl360-s02-r-hq", "R-S1":"nl360-s02-r-s1",
           "R-S2":"nl360-s02-r-s2"}
EXPECTED_FULL = {"R-HQ":4,"R-S1":2,"R-S2":2}
TARGET_ROUTER = "R-S1"
TARGET_INTERFACE = "s1b"
INJECTED_COST = 150


def run(*cmd: str, fail_ok=False) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    if p.returncode and not fail_ok:
        raise RuntimeError(
            f"cmd exit={p.returncode}: {' '.join(cmd)}\n"
            f"STDOUT={p.stdout[-1200:]}\nSTDERR={p.stderr[-1200:]}"
        )
    return p.stdout


def parse_functions():
    spec = importlib.util.spec_from_file_location("s03_compliance", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Validador S03 no importable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def host() -> dict:
    addr = run("ip","-4","-o","addr","show","dev","ens33")
    gateway = run("ip","-4","route","show","default")
    if "192.168.47.40/24" not in addr or "default via 192.168.47.2 dev ens33" not in gateway:
        raise RuntimeError("Proteccion VMnet8: gestion inesperada")
    return {"address":addr, "routes":run("ip","-4","route","show","table","main")}


def read_sources() -> tuple[dict, dict, dict]:
    if any(p.is_symlink() or not p.is_file() for p in (SOT,WAN_STATE,LAN_STATE)):
        raise RuntimeError("Faltan SoT, WAN state o LAN state de la red activa")
    sot=json.loads(SOT.read_text(encoding="utf-8"))
    wan=json.loads(WAN_STATE.read_text(encoding="utf-8"))
    lan=json.loads(LAN_STATE.read_text(encoding="utf-8"))
    if (sot.get("source_status") != "candidate"
            or set(sot.get("devices",{})) != set(ROUTERS)
            or wan.get("owner") != "NETLAB360_S02_WAN_LINKS_V1"
            or set(wan.get("ids",{})) != set(ROUTERS)
            or lan.get("owner") != "NETLAB360_S02_LAN_8021Q_V1"):
        raise RuntimeError("Propiedad declarativa WAN/LAN no coincide con S02")
    expected_by_device={name:sot["devices"][name]["container"] for name in ROUTERS}
    if expected_by_device != ROUTERS:
        raise RuntimeError("SoT contiene contenedores ajenos")
    mod=parse_functions()
    costs = {router:mod.expected(sot,router) for router in ROUTERS}
    if costs[TARGET_ROUTER].get(TARGET_INTERFACE) != 100:
        raise RuntimeError("El costo SoT de respaldo S1/s1b no es 100")
    return wan,lan,costs


def routers(wan: dict, lan: dict) -> dict:
    current={}
    for router,name in ROUTERS.items():
        data=json.loads(run("docker","inspect",name))[0]
        if (not data["State"]["Running"] or
                data["HostConfig"]["NetworkMode"] != "none" or
                data["Id"] != wan["ids"][router] or
                (data["Config"].get("Labels") or {}).get("com.docker.compose.project") != "netlab360-s02-wan"):
            raise RuntimeError(f"Router fuera de propiedad S02: {router}")
        site=router[2:]
        if lan.get("router_ids",{}).get(site) != data["Id"]:
            raise RuntimeError(f"Router WAN/LAN IDs inconsistentes: {router}")
        current[router]={"id":data["Id"],"pid":str(data["State"]["Pid"]),"name":name}
    return current


def observed_costs(current: dict) -> dict[str,dict[str,int]]:
    mod=parse_functions()
    return {
        r:mod.parse_frr_costs(
            run("docker","exec",d["name"],"vtysh","-c","show running-config"))
        for r,d in current.items()
    }


def full_neighbors(current:dict) -> None:
    for r,d in current.items():
        data=run("docker","exec",d["name"],"vtysh","-c","show ip ospf neighbor")
        got=sum("Full" in row for row in data.splitlines())
        if got!=EXPECTED_FULL[r]:
            raise RuntimeError(f"OSPF Full distinto a esperado: {r}={got}")
    print("S03_OSPF_FULL_INTACTO=4+2+2")


def primary_routes(current:dict) -> None:
    tests=(("R-HQ","10.79.0.2","s1p"),
           ("R-S1","10.79.0.1","s1p"),
           ("R-HQ","10.79.0.3","s2p"))
    for r,target,dev in tests:
        result=run("nsenter","-t",current[r]["pid"],"-n",
                   "ip","-4","route","get",target)
        if f"dev {dev}" not in result:
            raise RuntimeError(f"Ruta primaria alterada {r} -> {target}: {result}")
    print("S03_RUTAS_PRIMARIAS_INTACTAS=3/3")


def validate_costs(desired:dict, actual:dict, expected_target:int) -> None:
    count=0
    for router,rows in desired.items():
        for dev,cost in rows.items():
            expected=expected_target if (router,dev)==(TARGET_ROUTER,TARGET_INTERFACE) else cost
            if actual[router].get(dev) != expected:
                raise RuntimeError(f"Costo no esperado {router}/{dev}: "
                                   f"{actual[router].get(dev)} != {expected}")
            count+=1
    if count!=8:
        raise RuntimeError("Conteo WAN 8 diferente")
    print(f"S03_WAN_COSTOS_VERIFICADOS={count}/8 TARGET={expected_target}")


def vtysh_set_cost(current:dict,new_cost:int) -> None:
    if new_cost not in (100,150):
        raise RuntimeError("Costo fuera del escenario permitido")
    output=run("docker","exec",current[TARGET_ROUTER]["name"],"vtysh",
               "-c","configure terminal",
               "-c",f"interface {TARGET_INTERFACE}",
               "-c",f"ip ospf cost {new_cost}",
               "-c","end")
    if any(word in output.lower() for word in
           ("invalid input","unknown command","error","can't open","processing failure")):
        raise RuntimeError(f"FRR rechazo configuración: {output}")
    print(f"S03_CONFIG_APLICADA={TARGET_ROUTER}/{TARGET_INTERFACE} COSTO={new_cost}")


def check_state(current:dict) -> dict:
    if STATE.is_symlink() or not STATE.is_file():
        raise RuntimeError("Drift state propio ausente o simbolico")
    info=json.loads(STATE.read_text(encoding="utf-8"))
    if (info.get("owner")!=MARKER or info.get("target")!="R-S1/s1b" or
            info.get("original_cost")!=100 or info.get("injected_cost")!=150 or
            info.get("router_ids")!={k:v["id"] for k,v in current.items()}):
        raise RuntimeError("State drift no pertenece a routers actuales")
    return info


def verify(current:dict,desired:dict,target:int,before:dict) -> None:
    validate_costs(desired,observed_costs(current),target)
    full_neighbors(current)
    primary_routes(current)
    if host()!=before:
        raise RuntimeError("Rutas/IP de gestion del host cambiaron")
    print("S03_HOST_GESTION_INTACTO=SI")


def perform(action:str,snapshot:bool)->None:
    if os.geteuid()!=0:
        raise RuntimeError("Se requiere become sudo.ws solo dentro de Ansible")
    if HOME == Path("/root"):
        raise RuntimeError("Ansible debe preservar HOME del usuario del laboratorio")
    wan,lan,desired=read_sources()
    current=routers(wan,lan)
    before=host()
    cost=observed_costs(current)[TARGET_ROUTER].get(TARGET_INTERFACE)
    if cost not in (100, INJECTED_COST):
        raise RuntimeError(f"Costo de respaldo desconocido; no actuar: {cost}")
    print(f"S03_TARGET={TARGET_ROUTER}/{TARGET_INTERFACE}")
    print(f"S03_COSTO_SOT={desired[TARGET_ROUTER][TARGET_INTERFACE]}")
    print(f"S03_COSTO_OBSERVADO={cost}")
    if action=="inspect":
        if STATE.exists() or STATE.is_symlink():
            check_state(current)
            validate_costs(desired,observed_costs(current),cost)
            print("S03_DRIFT_STATE=PRESENTE")
        else:
            validate_costs(desired,observed_costs(current),100)
            print("S03_DRIFT_STATE=AUSENTE")
        full_neighbors(current)
        primary_routes(current)
        if host()!=before:
            raise RuntimeError("Host cambiado")
        print("S03_OPERACION_INSPECT=OK")
        return

    if action=="inject":
        if not snapshot:
            raise RuntimeError("Falta --snapshot-confirmado")
        if STATE.exists() or STATE.is_symlink():
            raise RuntimeError("State drift ya existe: nunca sobrescribir")
        verify(current,desired,100,before)
        STATE.parent.mkdir(parents=True,exist_ok=True)
        record={
            "owner":MARKER,"target":"R-S1/s1b",
            "original_cost":100,"injected_cost":150,
            "router_ids":{k:v["id"] for k,v in current.items()},
            "host":before,"created":datetime.now().isoformat(),
            "phase":"prepared",
        }
        with STATE.open("x",encoding="utf-8") as fh:
            json.dump(record,fh,indent=2)
        os.chmod(STATE,0o644)
        try:
            vtysh_set_cost(current,INJECTED_COST)
            verify(current,desired,150,before)
            record["phase"]="injected"
            STATE.write_text(json.dumps(record,indent=2))
            print("S03_DRIFT_INYECTADO=R-S1/s1b 100->150")
            print("S03_CONFIG_CHANGED=1")
            print("S03_DRIFT_INJECT_RESULTADO=OK")
        except BaseException:
            print("S03_DRIFT_INJECT_ERROR: intentando revertir 150->100",file=sys.stderr)
            try:
                vtysh_set_cost(current,100)
                verify(current,desired,100,before)
                STATE.unlink()
                print("S03_AUTO_ROLLBACK_COMPLETO=SI",file=sys.stderr)
            except Exception as exc:
                print(f"S03_AUTO_ROLLBACK_ERROR={exc}; STATE CONSERVADO",file=sys.stderr)
            raise
        return

    if snapshot:
        raise RuntimeError("--snapshot-confirmado solo pertenece a inject")
    info=None
    if STATE.exists() or STATE.is_symlink():
        info=check_state(current)
        if info["host"]!=before:
            raise RuntimeError("Estado base host cambió desde inyección; no modificar")
    if cost==100:
        verify(current,desired,100,before)
        if info is not None:
            STATE.unlink()
            print("S03_DRIFT_STATE_LIMPIADO=SI")
        print("S03_CONFIG_CHANGED=0")
        print("S03_RECONCILIACION=COMPLIANT")
        return
    if cost!=150 or info is None:
        raise RuntimeError(f"Solo se reconcilia drift autorizado 150 con state: observado={cost}")
    validate_costs(desired,observed_costs(current),150)
    full_neighbors(current)
    primary_routes(current)
    vtysh_set_cost(current,100)
    verify(current,desired,100,before)
    STATE.unlink()
    print("S03_DRIFT_RECONCILIADO=R-S1/s1b 150->100")
    print("S03_CONFIG_CHANGED=1")
    print("S03_RECONCILIACION=COMPLIANT")


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=("inspect","inject","reconcile"))
    ap.add_argument("--snapshot-confirmado",action="store_true")
    a=ap.parse_args()
    if a.action!="inject" and a.snapshot_confirmado:
        raise RuntimeError("Snapshot flag solo permitido con inject")
    perform(a.action,a.snapshot_confirmado)


if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print(f"S03_DRIFT_CONTROL_ERROR={type(exc).__name__}: {exc}",file=sys.stderr)
        sys.exit(1)
