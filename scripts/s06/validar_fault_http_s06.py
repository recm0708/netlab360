#!/usr/bin/env python3
"""S06: validar FAULT de backend HTTP HQ con evidencia HA independiente.

Solo lectura de JSONL S05 y bitácora de ejecución autorizada. No interviene
systemd, FRR, qdisc, Docker, LACP/SDN ni modelos. El origen no pertenece al
dataset ICMP V2 ni altera TRAIN/VALIDATION/TEST.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from datetime import datetime,timezone
from pathlib import Path
import re
import sys

ROOT=Path.home()/"netlab360-bootstrap"
BASE=ROOT/"s06"
STUDY=BASE/"estudio-uniforme-v2"
SOURCES=ROOT/"s05/evidencias/ha-noc"
OUT=STUDY/"fault-http-s06"
SCHEMA="NETLAB360_S06_FAULT_HTTP_HQ_GROUND_TRUTH_V1"
SRC_RE=re.compile(r"S05_HA_NOC_CICLO_(\d{8}T\d{6}Z)\.jsonl")
MARKERS=(
    "S05_HA_RESCATE_TIMER_ARMADO=",
    "S05_HA_RESCATE_PLAZO=120s",
    "S05_HA_NOC_BACKEND_HQ=DETENIDO_CONTROLADO",
    "S05_HA_NOC_CICLO=HQ_S1_HQ_OK",
    "S05_HA_NOC_SERVICIOS_RESTAURADOS=OK",
    "S05_HA_CICLO_INSTANCIA=HQ_S1_HQ_OK",
    "S05_HA_GESTION=INTACTA",
    "S05_LOTE_HA_INSTANCIA=OK",
)

def regular(path:Path,max_bytes:int=250000) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("source_missing_or_symlink")
    stat=path.stat()
    if stat.st_size<=0 or stat.st_size>max_bytes:
        raise ValueError("source_size_invalid")
    return path.read_bytes()

def utc(value:str)->datetime:
    if not isinstance(value,str):
        raise ValueError("timestamp_missing")
    d=datetime.fromisoformat(value.replace("Z","+00:00"))
    if d.tzinfo is None or d.utcoffset().total_seconds()!=0:
        raise ValueError("timestamp_not_utc")
    return d.astimezone(timezone.utc)

def phases(rows:list[dict])->tuple[list[str],dict]:
    if len(rows)<8:
        raise ValueError("insufficient_HA_samples")
    changes=[]
    labeled=[]
    previous_at=None
    switch_found=False
    last_state=None
    for row in rows:
        at=utc(row["observed_utc"])
        if previous_at is not None and at<=previous_at:
            raise ValueError("timestamps_not_monotonic")
        previous_at=at
        active=row.get("active")
        if (active not in ("BACKEND_HQ","BACKEND_S1")
                or row.get("ha_available") is not True
                or row.get("status")!="running"
                or row.get("fib_s1")!="s1p" or row.get("fib_s2")!="s2p"):
            raise ValueError("ha_or_wan_state_invalid")
        nodes=row.get("nodes")
        if (not isinstance(nodes,dict) or
                nodes.get("FRONTAL_HQ")!="running" or
                nodes.get(active)!="running"):
            raise ValueError("ha_service_provenance_invalid")
        if active=="BACKEND_HQ":
            if row.get("path")!="PRINCIPAL":
                raise ValueError("normal_route_inconsistent")
            label="RECOVERY_HTTP_HQ" if switch_found else "NORMAL_HTTP_HQ"
        else:
            if row.get("path")!="RESPALDO":
                raise ValueError("fault_route_inconsistent")
            # BACKEND_HQ detenido no debe seguir marcándose healthy en NOC.
            if nodes.get("BACKEND_HQ")=="running":
                raise ValueError("hq_backend_not_proven_down")
            switch_found=True
            label="FAULT_HTTP_BACKEND_HQ"
        if active!=last_state:
            changes.append(active)
            last_state=active
        labeled.append({"observed_utc":at.isoformat(),"label":label,
                        "active_backend":active})
    if changes!=["BACKEND_HQ","BACKEND_S1","BACKEND_HQ"]:
        raise ValueError("HA_fault_recovery_sequence_incomplete")
    counts={label:sum(row["label"]==label for row in labeled)
            for label in ("NORMAL_HTTP_HQ","FAULT_HTTP_BACKEND_HQ",
                          "RECOVERY_HTTP_HQ")}
    if min(counts.values())<1:
        raise ValueError("missing_ground_truth_class")
    return changes,{"counts":counts,"labeled":labeled}

def log_file(log:Path)->tuple[Path,str,bytes]:
    raw=regular(log,500000)
    text=raw.decode("utf-8")
    for marker in MARKERS:
        if marker not in text:
            raise ValueError("missing_approved_HA_marker_"+marker)
    timer=re.findall(r"^S05_HA_RESCATE_TIMER_ARMADO=(.+)$",text,re.M)
    canceled=re.findall(r"^S05_HA_RESCATE_TIMER_CANCELADO=(.+)$",text,re.M)
    if len(timer)!=1 or timer!=canceled:
        raise ValueError("rescue_timer_not_canceled_after_restoration")
    paths=re.findall(r"^S05_HA_NOC_JSONL=(.+)$",text,re.M)
    if len(paths)!=1:
        raise ValueError("ha_source_path_missing")
    source=Path(paths[0])
    if source.parent!=SOURCES or not SRC_RE.fullmatch(source.name):
        raise ValueError("ha_source_outside_scoped_evidence_dir")
    return source,timer[0],raw

def evaluate(log:Path)->dict:
    source,timer,log_raw=log_file(log)
    raw=regular(source,2500000)
    records=[json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    change,derived=phases(records)
    # Debe ser una prueba posterior al TEST cronológico V2.
    prior=STUDY/"TEST_Manifest.json"
    from auditar_gates_prospectivos import session_time
    val=json.loads(regular(prior,50000))
    ids=[val["normal_session"]]+val["degraded_sessions"]+val["recovery_sessions"]
    if utc(records[0]["observed_utc"])<=max(map(session_time,ids)):
        raise ValueError("fault_session_not_newer_than_test")
    return {
        "schema":SCHEMA,
        "created_at_utc":datetime.now(timezone.utc).isoformat(),
        "fault_type":"HTTP_HQ_BACKEND_STOP_WITH_S1_FAILOVER",
        "source_s05_jsonl":str(source),
        "source_execution_log":str(log),
        "source_sha256":hashlib.sha256(raw).hexdigest(),
        "log_sha256":hashlib.sha256(log_raw).hexdigest(),
        "recovery_watchdog":"SYSTEMD_INDEPENDENT_120_SECONDS_TIMER_CANCELED_AFTER_SUCCESS",
        "timer_unit":timer,
        "transition":change,
        "total_samples":len(records),
        "ground_truth_provenance":"AUTHORIZED_SYSTEMCTL_STOP_PLUS_NOC_HA_GRAPH",
        "observations":derived["labeled"],
        "sample_counts":derived["counts"],
        "WAN_fib_changed":False,
        "HA_frontend_failed":False,
        "network_state_mutated_by_this_auditor":False,
        "new_machine_learning_test":False,
        "legacy_models_retrained":False,
        "v2_models_retrained":False,
        "s06_v2_test_changed":False,
        "scope_limited_to_HTTP_HQ_backend":True,
        "forecast_horizon_validated":False,
        "generalization_to_fault_detection_by_ICMP_models":False,
        "gate":"FAULT_HTTP_HQ_OBSERVED_AND_RESTORED_NOT_ML_FAULT_PREDICTION",
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--save",action="store_true")
    group.add_argument("--check",action="store_true")
    parser.add_argument("--log",type=Path,required=True)
    a=parser.parse_args()
    os.umask(0o077)
    result=evaluate(a.log)
    source=Path(result["source_s05_jsonl"])
    match=SRC_RE.fullmatch(source.name)
    assert match
    destination=OUT/("S06_FAULT_HTTP_HQ_"+match.group(1)+".json")
    if a.save:
        if OUT.is_symlink():
            raise ValueError("output_symlink")
        OUT.mkdir(mode=0o700,parents=True,exist_ok=True)
        if OUT.stat().st_uid!=os.geteuid() or OUT.stat().st_mode & 0o077:
            raise ValueError("output_not_private")
        with destination.open("x",encoding="utf-8") as file:
            json.dump(result,file,ensure_ascii=False,indent=2)
            file.write("\n")
        destination.chmod(0o600)
    else:
        existing=json.loads(regular(destination,500000))
        fields=["schema","source_s05_jsonl","source_execution_log","source_sha256",
                "log_sha256","recovery_watchdog","timer_unit","transition",
                "total_samples","observations","sample_counts","gate"]
        if any(existing.get(x)!=result.get(x) for x in fields):
            raise ValueError("fault_report_or_source_changed")
    print("========== S06 FAULT HTTP HQ ==========")
    print("SECUENCIA="+">".join(result["transition"]))
    for k,v in result["sample_counts"].items():
        print("ETIQUETA="+k+" MUESTRAS="+str(v))
    print("WATCHDOG_AUTONOMO=120S_ARMADO_Y_CANCELADO")
    print("FIB_S1_S2=CONSERVADA")
    print("FRONTAL_HTTP=DISPONIBLE")
    print("FAULT_HTTP_HQ=VERIFICADO")
    print("FAULT_ICMP_IA=NO_EVALUADO")
    print("PRONOSTICO_FUTURO=NO_DEMOSTRADO")
    print("CAMBIOS_RED_POR_AUDITOR=NINGUNO")
    print("REPORTE="+str(destination))
    print("S06_FAULT_HTTP_VERIFICADO=OK")


if __name__=="__main__":
    try: main()
    except (ValueError,TypeError,RuntimeError,KeyError,OSError,
            json.JSONDecodeError) as exc:
        print("S06_FAULT_HTTP_ERROR="+type(exc).__name__+": "+str(exc),file=sys.stderr)
        sys.exit(1)
