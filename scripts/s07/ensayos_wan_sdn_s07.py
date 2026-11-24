#!/usr/bin/env python3
"""S07 WAN y SDN: ventanas reales, alcance explícito y recuperación."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from ensayos_servicios_s07 import (collect,diagnose,recommend,now,utc,cmd,active,
                                  preflight,save,load_s05)
from catalogo_runbooks import validate_action

GUARD="/usr/local/libexec/netlab360/s07-wan-trial.py"
BACKUP={"FIB-HQ-S1","FIB-S1-HQ","FIB-S1-S2"}

def assess(case,stage,a,r,rec,after=None):
    if not a["window"]["temporal_gate"] or not r["temporal_gate"]:
        return False,"WINDOW_NOT_USABLE"
    if rec["approval_granted"] or rec["network_mutations_authorized"] or r["network_mutations_authorized"]:
        raise ValueError("ADVISORY_SCOPE_VIOLATED")
    eligible={x["event_id"] for x in a["window"]["rows"] if x["eligibility"]=="ELIGIBLE"}
    def get(source,resource):
        rows=[e for e in a["batch"]["events"] if e["source"]==source and e["resource_id"]==resource]
        if len(rows)!=1: return None
        e=rows[0]
        if e["event_id"] not in eligible or e["quality"]!="VALID" or not e["observed_at_utc"]:
            return None
        if after and utc(e["observed_at_utc"])<utc(after): return None
        return e
    fault=stage=="FAULT"
    hs=r["hypotheses"]
    if case=="WAN":
        wan=get("NOC_S05","WAN-PRIMARIA-HQ-S1")
        if not wan or wan["details"]["admin_state"]!=("admin-down" if fault else "admin-up"):
            return False,"WAN_ADMIN_NOT_MATCHED"
        for site in ("HQ","S1","S2"):
            for peer in ("HQ","S1","S2"):
                if site==peer: continue
                key=f"FIB-{site}-{peer}"
                e=get("FRR_S02",key)
                if not e or e["details"]["selection"]!=("BACKUP" if fault and key in BACKUP else "PRIMARY"):
                    return False,"FIB_NOT_MATCHED"
        for site,iface in (("HQ","s1b"),("HQ","s2p"),("HQ","s2b"),("S1","s1b"),("S2","s2p"),("S2","s2b")):
            e=get("FRR_S02",f"OSPF-{site}-{iface}")
            if not e or e["details"]["neighbor_state"]!="Full": return False,"PROTECTED_OSPF_NOT_FULL"
        targets={("WAN_ADMIN_DEVIATION","WAN-HQ-S1-PRIMARY"),
                 ("FIB_BACKUP_SELECTED","ROUTE-HQ-S1"),("FIB_BACKUP_SELECTED","ROUTE-S1-HQ")}
        found={(h["rule"],h["context_id"]):h for h in hs}
        if fault:
            if not targets.issubset(found): return False,"TARGET_HYPOTHESIS_MISSING"
            for key in targets:
                h=found[key]
                action="S07_READ_WAN_V1" if key[0]=="WAN_ADMIN_DEVIATION" else "S07_READ_FIB_V1"
                if not any(i["hypothesis_id"]==h["hypothesis_id"] and any(x["action_id"]==action for x in i["suggested_read_only_actions"]) for i in rec["recommendations"]):
                    return False,"TARGET_RUNBOOK_MISSING"
        else:
            if targets.intersection(found): return False,"TARGET_FALSE_POSITIVE"
            for site in ("HQ","S1"):
                e=get("FRR_S02",f"OSPF-{site}-s1p")
                if not e or e["details"]["neighbor_state"]!="Full": return False,"PRIMARY_OSPF_NOT_FULL"
    elif case=="SDN":
        e=get("NOC_S05","FAUCET")
        if not e or e["state"]!="NORMAL" or e["details"]["connected"] is not True:
            return False,"CONTROLLER_NOT_VERIFIED_CONNECTED"
        if any(h["rule"]=="SDN_CONTROLLER_DEVIATION" for h in hs):
            return False,"FALSE_CONTROLLER_ATTRIBUTION"
    else: raise ValueError("CASE_DENIED")
    return True,"MATCH"

def capture(directory,case,stage,after=None,timeout=45,extra=None):
    end=time.monotonic()+timeout
    attempt=0
    while True:
        attempt+=1
        a=collect(); r=diagnose(a); rec=recommend(a)
        ok,reason=assess(case,stage,a,r,rec,after)
        name=f"{case.lower()}-{stage.lower()}-{attempt:02}"
        save(directory,name,{"case":case,"stage":stage,"matched":ok,"reason":reason,
              "captured_at_utc":now(),"acquisition":a,"diagnosis":r,"recommendation":rec,
              "direct_evidence":extra,"network_mutations_authorized":False})
        if ok:
            print(f"{case}_{stage}=MATCH | RCA={r['status']} | EVENTOS={len(a['batch']['events'])}",flush=True)
            for h in r["hypotheses"]:
                print("  HIPOTESIS="+h["rule"]+" CONTEXTO="+h["context_id"]+" INCERTIDUMBRE="+h["uncertainty"],flush=True)
            return name+".json"
        print(f"{case}_{stage}_INTENTO_{attempt}={reason}",flush=True)
        if time.monotonic()>=end: raise RuntimeError(case+"_"+stage+"_NOT_VERIFIED")
        time.sleep(1)

def guard(op,rid=None,*,directory=None):
    args=["sudo","-n","/usr/bin/python3","-I",GUARD,op]
    if rid: args.append(rid)
    result=subprocess.run(args,text=True,capture_output=True,timeout=45)
    try:
        d=json.loads(result.stdout)
    except (ValueError,TypeError):
        d=None
    if result.returncode or not isinstance(d,dict) or d.get("ok") is not True:
        report={"operation":op,"rfc_id":rid,"returncode":result.returncode,
                "response":d,"stdout":result.stdout[-8192:],
                "stderr":result.stderr[-8192:],"observed_at_utc":now()}
        if directory is not None:
            from uuid import uuid4
            save(directory,"wan-guard-error-"+op+"-"+uuid4().hex,report)
        print("WAN_GUARD_ERROR="+json.dumps(report,ensure_ascii=False),file=sys.stderr,flush=True)
        reason=d.get("reason","UNKNOWN") if isinstance(d,dict) else "INVALID_RESPONSE"
        raise RuntimeError("WAN_GUARD_DENIED: "+str(reason))
    return d

def wan_case(directory):
    base=preflight()
    s02=load_s05("s02_failover_wan.py")
    ha=load_s05("s05_ha_http_failover.py")
    pids=s02.validate_ownership()
    def probes():
        if s02.validate_ownership()!=pids: raise RuntimeError("WAN_SESSION_CHANGED")
        for target in ("10.79.0.2","10.79.0.3"): s02.ping(pids["R-HQ"],target)
        ha.expected("BACKEND_HQ","PRINCIPAL")
        return {"hq_loopback_icmp":"2/2 destinos, 2 paquetes por destino","http_from_s2":"BACKEND_HQ"}
    results={"baseline":capture(directory,"WAN","BASELINE",extra=probes())}
    d=guard("start",directory=directory)
    rid=d["id"]
    try:
        save(directory,"wan-guard-start",d)
        print("WAN_GUARD="+rid+" | WATCHDOG_ARMED=SI",flush=True)
        started=time.monotonic()
        stamp=d["down_verified_at_utc"]
        # La captura exige FIB de respaldo y observación posterior al estímulo.
        results["fault"]=capture(directory,"WAN","FAULT",stamp,timeout=75)
        save(directory,"wan-fault-probes",probes())
        current=s02.ns(pids["R-HQ"],"ip","-j","link","show","dev","s1p")
        if "UP" in json.loads(current)[0]["flags"]: raise RuntimeError("WAN_STIMULUS_NO_LONGER_ACTIVE")
        results["fault_observed_s"]=round(time.monotonic()-started,6)
    finally:
        restored=guard("restore",rid,directory=directory)
        save(directory,"wan-guard-restore",restored)
    results["recovery"]=capture(directory,"WAN","RECOVERY",restored["up_verified_at_utc"],timeout=100)
    save(directory,"wan-recovery-probes",probes())
    if preflight()!=base: raise RuntimeError("WAN_BASELINE_CHANGED")
    final=guard("finish",rid,directory=directory)
    save(directory,"wan-guard-final",final)
    results.update(restored=True,scope="HQ_S1_PRIMARY_ONLY",watchdog=final["unit"])
    save(directory,"wan-summary",results)
    return results

def sdn_case(directory):
    fault=load_s05("s05_sdn_falla_retorno_puerto_a.py")
    fault.precheck()
    base=preflight()
    fault.icmp.measure("a","198.18.41.12",allowed=True)
    fault.icmp.measure("b","198.18.41.13",allowed=False)
    results={"baseline":capture(directory,"SDN","BASELINE",extra={"port":"UP","a_b":"PERMITTED","b_c":"DENIED"})}
    arm=fault.failsafe_arm
    def checked_arm():
        u=arm()
        if not active(u+".timer"): raise RuntimeError("SDN_WATCHDOG_NOT_ACTIVE")
        return u
    fault.failsafe_arm=checked_arm
    original=fault.protected_services
    def observe(data):
        original(data)
        if not fault.device_up():
            fault.icmp.measure("b","198.18.41.13",allowed=False)
            fault.controller_connected()
            results["fault"]=capture(directory,"SDN","FAULT",start,timeout=25,
                extra={"port":"DOWN","a_b":"DENIED","b_c":"DENIED","controller":"CONNECTED",
                       "coverage":"DATA_PLANE_PORT_NOT_IN_S07_EVENT_CONTRACT",
                       "manual_read_only_runbook":validate_action("S07_READ_SDN_V1",{})})
            if fault.device_up() or preflight()!=base: raise RuntimeError("SDN_STIMULUS_OR_WAN_CHANGED")
    fault.protected_services=observe
    start=now()
    fault.run_fault()
    if "fault" not in results or not fault.device_up(): raise RuntimeError("SDN_FAULT_NOT_OBSERVED")
    fault.icmp.measure("a","198.18.41.12",allowed=True)
    fault.icmp.measure("b","198.18.41.13",allowed=False)
    results["recovery"]=capture(directory,"SDN","RECOVERY",now(),extra={"port":"UP","a_b":"PERMITTED","b_c":"DENIED"})
    if preflight()!=base: raise RuntimeError("SDN_BASELINE_CHANGED")
    results.update(restored=True,scope="ISOLATED_SDN_PORT_A",controller_failure_induced=False,
                   coverage_limitation="DATA_PLANE_PORT_NOT_IN_S07_EVENT_CONTRACT")
    save(directory,"sdn-summary",results)
    return results

def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    a=p.parse_args()
    if os.geteuid()==0 or not sys.stdin.isatty(): p.error("usuario normal y TTY requeridos")
    if cmd("hostname").strip()!="netlab360-lab" or cmd("git","status","--porcelain").strip(): p.error("host o repo invalido")
    if not a.directory.is_dir() or any(a.directory.iterdir()): p.error("directorio nuevo y vacio requerido")
    def interrupted(sig,frame): raise InterruptedError(f"INTERRUPTED_{sig}")
    for sig in (signal.SIGHUP,signal.SIGINT,signal.SIGTERM): signal.signal(sig,interrupted)
    print("Solo WAN HQ/s1p y puerto aislado SDN sdna0. Retorno autorizado. Escriba APROBAR WAN SDN S07: ",end="",flush=True,file=sys.stderr)
    if input()!="APROBAR WAN SDN S07": p.error("confirmacion denegada")
    save(a.directory,"approval",{"approved_at_utc":now(),"scope":["HQ/s1p","SDN/sdna0"],"uid":os.getuid(),
         "broker_operational_approval":False})
    w=wan_case(a.directory)
    s=sdn_case(a.directory)
    save(a.directory,"summary",{"schema":"NETLAB360_S07_WAN_SDN_TRIALS_V1","wan":w,"sdn":s,
        "simultaneous":False,"automatic_remediation":False,"operational_events_imported":0})
    print("WAN_SDN_REAL=2/2 | VENTANAS=6/6 | RESTAURACIONES=2/2",flush=True)
if __name__=="__main__": main()
