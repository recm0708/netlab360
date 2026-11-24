#!/usr/bin/env python3
"""S07: experimentos HTTP HA y LACP S1, con diagnóstico de ventanas reales.

Reutiliza los procedimientos S05, no integra el broker de cambio S07.
La aprobación local autoriza solamente estos dos estímulos y su reversión.
No importa ventanas a la base histórica, no ajusta modelos.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from uuid import uuid4

from adquisicion_integrada import collect
from contrato_eventos import utc
from diagnostico_rca import diagnose
from recomendaciones_rca import recommend

ROOT=Path(__file__).resolve().parents[2]
PREFLIGHT="/usr/local/libexec/netlab360/s07-preflight.py"
CASES={
    "HTTP":("HTTP_HA","FRONTAL_HQ","HTTP_BACKUP_SELECTED","HTTP-HA","S07_READ_HTTP_V1"),
    "LACP":("LACP","LACP-S1","LACP_MEMBER_DEVIATION","SITE-S1","S07_READ_LACP_V1"),
}


def now():
    return datetime.now(timezone.utc).isoformat()


def load_s05(name):
    path=ROOT/"scripts/laboratorio"/name
    spec=importlib.util.spec_from_file_location("s05_"+name.replace("-","_"),path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def save(directory,name,d):
    with (directory/(name+".json")).open("x",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False)
        f.write("\n")


def cmd(*argv,timeout=20):
    p=subprocess.run(argv,text=True,capture_output=True,timeout=timeout)
    if p.returncode:
        raise RuntimeError("COMMAND_FAILED: "+str(argv[:4])+" "+p.stderr[-300:])
    return p.stdout


def active(unit):
    return subprocess.run(["systemctl","is-active","--quiet",unit],timeout=5).returncode==0


def preflight():
    d=json.loads(cmd("sudo","-n","/usr/bin/python3","-I",PREFLIGHT,"check",timeout=40))
    if not d["ok"] or not d["identity_verified"] or d["configuration_status"]!="MET":
        raise RuntimeError("PREFLIGHT_DENIED")
    return {k:d[k] for k in ("costs","neighbors","routes","management")}


def assess(case,stage,a,r,rec,not_before=None):
    subject,resource,rule,ctx,action=CASES[case]
    if stage not in ("BASELINE","FAULT","RECOVERY"):
        raise ValueError("STAGE_INVALID")
    if not a["window"]["temporal_gate"] or not r["temporal_gate"]:
        return False,"WINDOW_NOT_USABLE"
    rows=[e for e in a["batch"]["events"] if e["source"]=="NOC_S05"
          and e["subject"]==subject and e["resource_id"]==resource]
    if len(rows)!=1:
        return False,"TARGET_UNKNOWN"
    e=rows[0]
    eligible={x["event_id"] for x in a["window"]["rows"] if x["eligibility"]=="ELIGIBLE"}
    if e["event_id"] not in eligible or e["quality"]!="VALID" or not e["observed_at_utc"]:
        return False,"TARGET_UNKNOWN"
    if not_before and utc(e["observed_at_utc"])<utc(not_before):
        return False,"TARGET_SAMPLE_PRECEDES_PHASE"
    fault=stage=="FAULT"
    if e["state"]!=("DEGRADED" if fault else "NORMAL"):
        return False,"TARGET_STATE_NOT_MATCHED"
    details=e["details"]
    if case=="HTTP":
        if (details.get("status"),details.get("active_backend"),details.get("selected_path"))!=(
            "running","BACKEND_S1" if fault else "BACKEND_HQ","RESPALDO" if fault else "PRINCIPAL"):
            return False,"HTTP_STATE_NOT_MATCHED"
    elif (details.get("switch_members"),details.get("client_members"))!=((1,1) if fault else (2,2)):
        return False,"LACP_STATE_NOT_MATCHED"
    hypotheses=[h for h in r["hypotheses"] if h["rule"]==rule and h["context_id"]==ctx]
    if fault:
        if len(hypotheses)!=1 or e["event_id"] not in hypotheses[0]["anchor_event_ids"]:
            return False,"TARGET_HYPOTHESIS_MISSING"
        items=[i for i in rec["recommendations"] if i["hypothesis_id"]==hypotheses[0]["hypothesis_id"]]
        if len(items)!=1 or not any(x["action_id"]==action for x in items[0]["suggested_read_only_actions"]):
            return False,"TARGET_RUNBOOK_MISSING"
    elif hypotheses:
        return False,"TARGET_FALSE_POSITIVE"
    if rec["approval_granted"] or rec["network_mutations_authorized"] or r["network_mutations_authorized"]:
        raise ValueError("ADVISORY_SCOPE_VIOLATED")
    return True,"MATCH"


def capture(directory,case,stage,not_before=None,timeout=18):
    end=time.monotonic()+timeout
    attempt=0
    while True:
        attempt+=1
        a=collect()
        r=diagnose(a)
        rec=recommend(a)
        ok,reason=assess(case,stage,a,r,rec,not_before)
        d={"case":case,"stage":stage,"attempt":attempt,"mode":"REAL_OBSERVATION",
           "matched":ok,"reason":reason,"acquisition":a,"diagnosis":r,"recommendation":rec,
           "captured_at_utc":now(),"network_mutations_authorized":False}
        save(directory,f"{case.lower()}-{stage.lower()}-{attempt:02}",d)
        if ok:
            print(f"{case}_{stage}=MATCH | RCA={r['status']} | VENTANA={a['window']['elapsed_seconds']} s",flush=True)
            for h in r["hypotheses"]:
                print("  HIPOTESIS="+h["rule"]+" CONTEXTO="+h["context_id"]+" INCERTIDUMBRE="+h["uncertainty"],flush=True)
            print("  RECOMENDACION="+rec["decision"],flush=True)
            return {"file":f"{case.lower()}-{stage.lower()}-{attempt:02}.json",
                    "captured_at_utc":d["captured_at_utc"],"hypotheses":len(r["hypotheses"]),
                    "coverage_gaps":len(r["coverage_gaps"]),"decision":rec["decision"]}
        print(f"{case}_{stage}_INTENTO_{attempt}={reason}",flush=True)
        if time.monotonic()>=end:
            raise RuntimeError(f"{case}_{stage}_OBSERVATION_NOT_VERIFIED")
        time.sleep(.75)


def http_case(directory):
    ha=load_s05("s05-ha-http-failover.py")
    ha.check()
    ha.fib_check()
    base=preflight()
    results={"baseline":capture(directory,"HTTP","BASELINE")}
    ha.expected("BACKEND_HQ","PRINCIPAL")
    unit="netlab360-s07-http-rescue-"+uuid4().hex
    cmd("sudo","-n","systemd-run","--unit="+unit,"--on-active=120s",
        "--timer-property=AccuracySec=1s","--property=Type=oneshot",
        "/usr/bin/systemctl","start",ha.ROOT)
    if not active(unit+".timer"):
        raise RuntimeError("HTTP_WATCHDOG_NOT_READY")
    changed=False
    restored=False
    try:
        ha.check()
        if not active(unit+".timer"):
            raise RuntimeError("HTTP_WATCHDOG_LOST")
        stamp=now()
        tick=time.monotonic()
        changed=True
        cmd("sudo","-n","systemctl","stop",ha.ROOT,timeout=15)
        if active(ha.ROOT):
            raise RuntimeError("HTTP_PRIMARY_NOT_STOPPED")
        ha.wait("BACKEND_S1","RESPALDO",timeout=12)
        results["fault"]=capture(directory,"HTTP","FAULT",stamp)
        ha.expected("BACKEND_S1","RESPALDO")
        if active(ha.ROOT):
            raise RuntimeError("HTTP_FAULT_ENDED_BEFORE_VERIFICATION")
        if preflight()!=base:
            raise RuntimeError("HTTP_WAN_CHANGED")
        results["fault_observed_elapsed_s"]=round(time.monotonic()-tick,6)
    finally:
        if changed:
            restore_stamp=now()
            cmd("sudo","-n","systemctl","start",ha.ROOT,timeout=20)
            ha.wait("BACKEND_HQ","PRINCIPAL",timeout=15)
            restored=True
        # Keep the independent timer on any unverified or interrupted path.
    if not restored:
        raise RuntimeError("HTTP_NOT_RESTORED")
    results["recovery"]=capture(directory,"HTTP","RECOVERY",restore_stamp)
    ha.check()
    if preflight()!=base:
        raise RuntimeError("HTTP_FINAL_WAN_CHANGED")
    if active(unit+".timer"):
        cmd("sudo","-n","systemctl","stop",unit+".timer")
    results.update(watchdog=unit,restored=True,scope="BACKEND_HQ_ONLY")
    save(directory,"http-summary",results)
    return results


def lacp_case(directory):
    fault=load_s05("s05-lacp-s1-falla-retorno.py")
    lab=fault.lab
    data=fault.precheck()
    base=preflight()
    results={"baseline":capture(directory,"LACP","BASELINE")}
    original=fault.availability
    def observed_availability():
        original()
        # Require observed NOC degradation and direct aggregators both reduced.
        results["fault"]=capture(directory,"LACP","FAULT",start_stamp)
        lab.bond_ports(lab.CLIENT,lab.CLIENT_BOND,1,attempts=1)
        lab.bond_ports(lab.SW,lab.SW_BOND,1,attempts=1)
        if preflight()!=base:
            raise RuntimeError("LACP_WAN_CHANGED")
    fault.availability=observed_availability
    start_stamp=now()
    fault.exercise()
    if "fault" not in results:
        raise RuntimeError("LACP_FAULT_NOT_OBSERVED")
    lab.status(data,ping=True)
    results["recovery"]=capture(directory,"LACP","RECOVERY",results["fault"]["captured_at_utc"])
    if preflight()!=base:
        raise RuntimeError("LACP_FINAL_WAN_CHANGED")
    results.update(restored=True,scope="S1_CLIENT_S5C1_ONLY")
    save(directory,"lacp-summary",results)
    return results


def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    args=p.parse_args()
    if os.geteuid()==0 or not sys.stdin.isatty():
        p.error("usuario normal y TTY requeridos")
    if not args.directory.is_dir() or any(args.directory.iterdir()):
        p.error("directorio nuevo y vacio requerido")
    if cmd("hostname").strip()!="netlab360-lab":
        p.error("host no autorizado")
    if cmd("git","-C",str(ROOT),"status","--porcelain").strip():
        p.error("repositorio no limpio")
    def interrupt(signum,frame):
        raise InterruptedError(f"INTERRUPTED_{signum}")
    for s in (signal.SIGHUP,signal.SIGTERM,signal.SIGINT):
        signal.signal(s,interrupt)
    print("Alcance: detener/restaurar backend HTTP HQ y reducir/restaurar s5c1 LACP S1, secuencialmente.",file=sys.stderr)
    print("Escriba APROBAR HTTP LACP S07: ",end="",flush=True,file=sys.stderr)
    if input()!="APROBAR HTTP LACP S07":
        p.error("confirmacion denegada")
    save(args.directory,"approval",{"scope":["HTTP_BACKEND_HQ","LACP_S1_S5C1"],
        "approved_at_utc":now(),"uid":os.getuid(),"mode":"LOCAL_ADMIN_EXPERIMENT",
        "broker_operational_approval":False})
    a=http_case(args.directory)
    b=lacp_case(args.directory)
    save(args.directory,"summary",{"schema":"NETLAB360_S07_SERVICE_TRIALS_V1",
        "mode":"REAL_SEQUENTIAL_CONTROLLED_EXPERIMENTS","http":a,"lacp":b,
        "synthetic":False,"simultaneous":False,"continuous_availability_measured":False,
        "automatic_remediation":False,"operational_events_imported":0})
    print("HTTP_LACP_REAL=2/2 | RCA_RUNBOOKS=2/2 | RESTAURACION=2/2",flush=True)


if __name__=="__main__":
    main()
