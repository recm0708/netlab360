#!/usr/bin/env python3
"""Aceptación local S07 API; solo operador, dos confirmaciones root por TTY."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from uuid import uuid4
from api_s07 import call
from rfc_ospf_operacional import ACTIONS

PREFIX="/api/v1"
EXEC="/usr/local/libexec/netlab360/s07-api.py"
TRIAL="/usr/local/libexec/netlab360/s07-ospf-trial.py"

def key(): return uuid4().hex

def write(path,d):
    path.write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+"\n")

def accept(directory):
    assert os.geteuid()!=0 and directory.is_dir()
    def req(name,method,route,body=None,k=None,code=200,reason=None):
        status,d=call(method,PREFIX+route,body,k)
        write(directory/(name+".json"),{"http_status":status,"response":d})
        if status!=code or (reason is not None and d.get("reason")!=reason):
            raise RuntimeError(name+": "+str(status)+" "+str(d.get("reason","UNEXPECTED_RESPONSE")))
        print(name.upper()+"="+str(status)+(f" | {reason}" if reason else ""),flush=True)
        return d
    print("========== API READS Y CONTROLES ==========",flush=True)
    for endpoint in ("health","incidents","hypotheses","runbooks","audit"):
        d=req(endpoint,"GET","/"+endpoint)
        assert d["ok"]
        if endpoint in ("incidents","hypotheses","runbooks"):
            assert d["result"]["authorization_evidence"] is False
    req("ruta_arbitraria","POST","/shell",{},key(),404,"ROUTE_DENIED")
    req("schema_invalido","POST","/rfcs",{"shell":"id"},key(),400,"BODY_INVALID")
    req("accion_arbitraria","POST","/rfcs",{"action_id":"shell","arguments":{}},key(),409,"ACTION_OR_ARGUMENT_DENIED")
    action,args=ACTIONS["EXPERIMENT"]
    body={"action_id":action,"arguments":args}
    req("sin_idempotencia","POST","/rfcs",body,None,400,"IDEMPOTENCY_KEY_REQUIRED")
    k=key()
    a=req("solicitud_cancelable","POST","/rfcs",body,k)["result"]
    assert a["status"]=="PENDING"
    rid=a["rfc_id"];route="/rfcs/"+rid
    approval=a["approvals"]["EXPERIMENT"]["binding"]
    assert req("replay_solicitud","POST","/rfcs",body,k)["result"]==a
    req("conflicto_idempotencia","POST","/rfcs",{"action_id":"shell","arguments":{}},k,409,"IDEMPOTENCY_CONFLICT")
    req("autoaprobacion","POST",route+"/approve-execute",{"binding":approval,"confirmation":"APROBAR RFC "+approval["approval_id"]},key(),403,"ROLE_DENIED")
    c=req("cancelacion","POST",route+"/cancel",{"binding":approval},key())["result"]
    assert c["status"]=="CANCELLED"
    assert req("estado_cancelado","GET",route)["result"]["status"]=="CANCELLED"
    # A repeat returns historical response, without creating a second RFC.
    assert req("replay_tras_cancelacion","POST","/rfcs",body,k)["result"]==a
    print("IDEMPOTENCIA_REAL=VALIDADA | MUTACIONES_CONTROLES=0",flush=True)
    print("========== CICLO INTEGRADO API ==========",flush=True)
    a=req("solicitud_real","POST","/rfcs",body,key())["result"]
    rid=a["rfc_id"]; route="/rfcs/"+rid
    print("RFC="+rid,flush=True)
    baseline=req("intencion_inicial","GET",route+"/intent")["result"]
    assert baseline["configuration_compliance"]=="MET" and baseline["deviations"]==[]
    def approve(stage,name):
        with (directory/(name+".json")).open("w") as out, open("/dev/tty") as tty:
            result=subprocess.run(["sudo","-n","/usr/bin/python3","-I",EXEC,"approve",rid,
                                   "--stage",stage,"--key",key()],stdin=tty,stdout=out,check=False)
        if result.returncode: raise RuntimeError(name+": APROBACION_NO_COMPLETADA")
        d=json.loads((directory/(name+".json")).read_text())
        assert d["ok"]
        return d["result"]
    print("PRIMERA CONFIRMACION ADMINISTRATIVA: ESTIMULO",flush=True)
    drift=approve("EXPERIMENT","estimulo")
    assert drift["status"]=="DRIFT_VERIFIED" and drift["observed_cost"]==150 and drift["watchdog_armed"]
    observed=req("intencion_drift","GET",route+"/intent")["result"]
    assert observed["configuration_compliance"]=="NOT_MET"
    assert observed["deviations"]==[{"resource":"S1/s1b","desired":100,"observed":150}]
    assert observed["recommendation"]["decision"]=="REQUEST_HUMAN_RESTORE"
    assert observed["network_mutations_authorized"] is False
    print("DRIFT=150 | EXPLICACION=DESVIACION_DE_COSTO | RECOMENDACION=RESTAURAR_100",flush=True)
    restored_req=req("solicitud_restauracion","POST",route+"/restore-request",{},key())["result"]
    assert restored_req["status"]=="DRIFT_VERIFIED"
    print("SEGUNDA CONFIRMACION ADMINISTRATIVA: RESTAURACION",flush=True)
    final=approve("RESTORE","restauracion")
    assert final["status"]=="VERIFIED" and final["observed_cost"]==100
    state=req("ejecucion_final","GET",route+"/execution")["result"]
    assert state["status"]=="VERIFIED"
    after=req("intencion_final","GET",route+"/intent")["result"]
    assert after["configuration_compliance"]=="MET" and after["deviations"]==[]
    assert after["recommendation"]["decision"]=="NO_CHANGE"
    assert after["ospf_full"]==8 and after["fib_primary"]==6 and after["icmp_samples"]==6 and after["http"]=="available"
    for stage in ("EXPERIMENT","RESTORE"):
        a=state["approvals"][stage]
        assert a["status"]=="CONSUMED" and a["approver_uid"]==0 and a["binding"]["requester_uid"]==os.getuid()
    audit=req("auditoria_final","GET","/audit")["result"]
    rows=[e for e in audit if e["rfc_id"]==rid and e["event"]=="APPROVAL_CONSUMED"]
    assert len(rows)==2 and all(e["uid"]==0 for e in rows)
    # Protected journal is the source of final postconditions.
    with (directory/"journal-protegido.json").open("w") as out:
        subprocess.run(["sudo","-n","/usr/bin/python3","-I",TRIAL,"status",rid],stdout=out,check=True)
    journal=json.loads((directory/"journal-protegido.json").read_text())["transaction"]
    assert journal["status"]=="VERIFIED" and journal["baseline"]==journal["final_observation"]
    assert journal["events"][-1]["source"]=="HUMAN_APPROVED"
    write(directory/"summary.json",{"rfc_id":rid,"status":"VERIFIED","source":"REAL_API",
          "cycle":[100,150,100],"controls":"PASS","approvals":2,"postconditions":True,
          "continuous_availability_measured":False,"automatic_remediation":False})
    print("CICLO_API=100_150_100 | APROBACIONES=2/2 | ESTADO=VERIFIED",flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("directory",type=Path)
    accept(p.parse_args().directory)
