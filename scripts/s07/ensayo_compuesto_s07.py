#!/usr/bin/env python3
"""Ensayo compuesto WAN HQ/s1p + HTTP HQ: adquisición común, rescates separados."""
import argparse
import json
import os
from pathlib import Path
import signal
import sys
import time
from uuid import uuid4
from ensayos_servicios_s07 import (collect,diagnose,recommend,now,utc,cmd,active,
                                  preflight,save,load_s05,assess as assess_service)
from ensayos_wan_sdn_s07 import guard,assess as assess_wan

def assess_joint(stage,a,r,rec,after=None):
    if stage not in ("BASELINE","FAULT","RECOVERY"):
        raise ValueError("STAGE_INVALID")
    if rec["approval_granted"] or rec["network_mutations_authorized"] or r["network_mutations_authorized"]:
        raise ValueError("ADVISORY_SCOPE_VIOLATED")
    for domain,fn in (("WAN",assess_wan),("HTTP",assess_service)):
        ok,reason=fn(domain,stage,a,r,rec,after)
        if not ok: return False,domain+":"+reason
    return True,"MATCH"

def capture(directory,stage,after=None,timeout=35,verify=None):
    end=time.monotonic()+timeout
    attempt=0
    while True:
        attempt+=1
        if verify: verify()
        a=collect(); r=diagnose(a); rec=recommend(a)
        ok,reason=assess_joint(stage,a,r,rec,after)
        if verify: verify()
        name=f"compound-{stage.lower()}-{attempt:02}"
        save(directory,name,{"mode":"REAL_SHARED_ACQUISITION_WINDOW","stage":stage,
             "matched":ok,"reason":reason,"acquisition":a,"diagnosis":r,"recommendation":rec,
             "captured_at_utc":now(),"network_mutations_authorized":False})
        if ok:
            print(f"COMPOUND_{stage}=MATCH | EVENTS={len(a['batch']['events'])} | RCA={r['status']}",flush=True)
            for h in r["hypotheses"]:
                print(f"  {h['rule']} | {h['context_id']} | {h['uncertainty']}",flush=True)
            return name+".json"
        print(f"COMPOUND_{stage}_ATTEMPT_{attempt}={reason}",flush=True)
        if time.monotonic()>=end: raise RuntimeError("COMPOUND_"+stage+"_NOT_VERIFIED")
        time.sleep(1)

def historical(directory,services,network):
    """Reproducir decisiones de 12 ventanas previamente aceptadas."""
    rows=[]
    for case,path,fn in (("HTTP",services,assess_service),("LACP",services,assess_service),
                         ("WAN",network,assess_wan),("SDN",network,assess_wan)):
        meta=json.loads((path/(case.lower()+"-summary.json")).read_text())
        if not meta["restored"]: raise ValueError("HISTORICAL_RESTORATION_NOT_VERIFIED")
        for stage in ("BASELINE","FAULT","RECOVERY"):
            name=meta[stage.lower()]
            if isinstance(name,dict): name=name["file"]
            if Path(name).name!=name: raise ValueError("HISTORICAL_PATH_INVALID")
            d=json.loads((path/name).read_text())
            a=d["acquisition"]; r=diagnose(a); rec=recommend(a)
            if (not d["matched"] or len(a["batch"]["events"])!=58
                or d["diagnosis"]!=r or d["recommendation"]!=rec):
                raise ValueError("HISTORICAL_REPRODUCTION_FAILED")
            ok,reason=fn(case,stage,a,r,rec)
            if not ok: raise ValueError("HISTORICAL_"+case+"_"+stage+":"+reason)
            rows.append({"case":case,"stage":stage,"file":str(path/name),
                         "hypotheses":[{"rule":h["rule"],"context":h["context_id"],"uncertainty":h["uncertainty"]} for h in r["hypotheses"]],
                         "decision":rec["decision"],"coverage_gaps":len(r["coverage_gaps"])})
    save(directory,"historical-review",{"mode":"REAL_HISTORICAL_REPRODUCTION","rows":rows,
         "new_stimuli":0,"statistical_generalization":False})
    print("HISTORICAL_WINDOWS_REPRODUCED=12/12",flush=True)

def experiment(directory):
    base=preflight()
    ha=load_s05("s05_ha_http_failover.py")
    s02=load_s05("s02_failover_wan.py")
    ha.check(); ha.fib_check()
    pids=s02.validate_ownership()
    def direct(backend,path):
        if s02.validate_ownership()!=pids: raise RuntimeError("ROUTER_SESSION_CHANGED")
        for ip in ("10.79.0.2","10.79.0.3"): s02.ping(pids["R-HQ"],ip)
        return {"http":ha.expected(backend,path),"icmp_destinations":2,"samples_not_continuous":True}
    save(directory,"compound-baseline-probes",direct("BACKEND_HQ","PRINCIPAL"))
    result={"baseline":capture(directory,"BASELINE")}
    w=guard("start",directory=directory)
    rid=w["id"]
    http_timer="netlab360-s07-http-rescue-"+uuid4().hex
    http_changed=False
    try:
        save(directory,"compound-wan-start",w)
        s02.wait_fib(pids["R-HQ"],"10.79.0.2","s1b",limit=45)
        ha.check()
        cmd("sudo","-n","systemd-run","--unit="+http_timer,"--on-active=120s",
            "--timer-property=AccuracySec=1s","--property=Type=oneshot",
            "/usr/bin/systemctl","start",ha.ROOT)
        if not active(http_timer+".timer") or not active(w["unit"]+".timer"):
            raise RuntimeError("WATCHDOG_NOT_READY")
        def overlap():
            if not active(w["unit"]+".timer") or not active(http_timer+".timer"):
                raise RuntimeError("WATCHDOG_LOST")
            if s02.validate_ownership()!=pids: raise RuntimeError("ROUTER_SESSION_CHANGED")
            link=json.loads(s02.ns(pids["R-HQ"],"ip","-j","link","show","dev","s1p"))
            if len(link)!=1 or "UP" in link[0]["flags"] or active(ha.ROOT):
                raise RuntimeError("STIMULI_NOT_SIMULTANEOUS")
            if not active(ha.BACKUP) or not active(ha.FRONTEND):
                raise RuntimeError("PROTECTED_HTTP_UNAVAILABLE")
        stamp=now()
        tick=time.monotonic()
        http_changed=True
        cmd("sudo","-n","systemctl","stop",ha.ROOT,timeout=15)
        ha.wait("BACKEND_S1","RESPALDO",timeout=15)
        overlap()
        save(directory,"compound-fault-probes",direct("BACKEND_S1","RESPALDO"))
        result["fault"]=capture(directory,"FAULT",stamp,timeout=35,verify=overlap)
        overlap()
        result["elapsed_from_http_stop_request_s"]=round(time.monotonic()-tick,6)
        print("SIMULTANEOUS_WAN_HTTP=VERIFIED",flush=True)
    finally:
        try:
            if http_changed:
                cmd("sudo","-n","systemctl","start",ha.ROOT,timeout=20)
        finally:
            recovered=guard("restore",rid,directory=directory)
            save(directory,"compound-wan-restore",recovered)
    ha.wait("BACKEND_HQ","PRINCIPAL",timeout=20)
    result["recovery"]=capture(directory,"RECOVERY",recovered["up_verified_at_utc"],timeout=100)
    save(directory,"compound-recovery-probes",direct("BACKEND_HQ","PRINCIPAL"))
    ha.check()
    if preflight()!=base: raise RuntimeError("BASELINE_NOT_RESTORED")
    final=guard("finish",rid,directory=directory)
    save(directory,"compound-wan-final",final)
    if active(http_timer+".timer"):
        try: cmd("sudo","-n","systemctl","stop",http_timer+".timer")
        except RuntimeError:
            if active(http_timer+".timer"): raise
    if active(http_timer+".timer") or active(w["unit"]+".timer"):
        raise RuntimeError("WATCHDOG_STILL_ACTIVE")
    result.update(schema="NETLAB360_S07_COMPOUND_TRIAL_V1",simultaneous=True,
        restored=True,automatic_remediation=False,broker_operational_approval=False,
        continuous_availability_measured=False,operational_events_imported=0)
    save(directory,"compound-summary",result)
    print("COMPOUND_REAL=VERIFIED | SHARED_WINDOWS=3/3 | RESTORATION=2/2",flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    p.add_argument("--services",required=True,type=Path)
    p.add_argument("--network",required=True,type=Path)
    a=p.parse_args()
    if os.geteuid()==0 or not sys.stdin.isatty(): p.error("usuario normal y TTY requeridos")
    if cmd("hostname").strip()!="netlab360-lab" or cmd("git","status","--porcelain").strip():
        p.error("host o repo invalido")
    if not a.directory.is_dir() or any(a.directory.iterdir()): p.error("directorio nuevo requerido")
    historical(a.directory,a.services,a.network)
    def interrupted(sig,frame): raise InterruptedError(f"INTERRUPTED_{sig}")
    for sig in (signal.SIGHUP,signal.SIGINT,signal.SIGTERM): signal.signal(sig,interrupted)
    print("Solo HQ/s1p y backend HTTP HQ, simultaneos, con retorno autorizado.\nEscriba APROBAR COMPUESTO S07: ",
          end="",flush=True,file=sys.stderr)
    if input()!="APROBAR COMPUESTO S07": p.error("confirmacion denegada")
    save(a.directory,"approval",{"scope":["HQ/s1p","HTTP_BACKEND_HQ"],"approved_at_utc":now(),
         "uid":os.getuid(),"broker_operational_approval":False})
    experiment(a.directory)
if __name__=="__main__": main()
