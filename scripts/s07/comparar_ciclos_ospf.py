#!/usr/bin/env python3
"""Comparación descriptiva reproducible de dos ciclos OSPF reales conservados."""
import argparse
from copy import deepcopy
import json
import math
from pathlib import Path

TARGET="S1/s1b"
PROFILE={"HQ/s1p":10,"HQ/s1b":100,"HQ/s2p":10,"HQ/s2b":100,
         "S1/s1p":10,"S1/s1b":100,"S2/s2p":10,"S2/s2b":100}
PREFIX=["PENDING","APPROVED_EXPERIMENT","ARMED","APPLYING","DRIFT_APPLIED","DRIFT_VERIFIED"]
SUFFIX=["RESTORING","RESTORED_UNVERIFIED","VERIFIED"]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def evaluate(record,source):
    require(source in ("WATCHDOG","HUMAN_APPROVED"),"SOURCE_DENIED")
    require(record.get("ok") is True,"RECORD_NOT_OK")
    t=record["transaction"]
    require(t["schema"]=="NETLAB360_S07_OSPF_TRIAL_V1" and t["status"]=="VERIFIED"
            and t["target"]==TARGET and t["baseline_cost"]==100 and t["drift_cost"]==150,
            "TRANSACTION_INVALID")
    require(t["action_id"]=="S07_RESTORE_OSPF_COST_V1"
            and t["arguments"]=={"site":"S1","interface":"s1b","cost":100},"ACTION_INVALID")
    base=t["baseline"]
    require(base["costs"]==PROFILE and base==t["final_observation"],"BASELINE_NOT_RESTORED")
    drift=deepcopy(base)
    drift["costs"][TARGET]=150
    require(t["drift_observation"]==drift,"DRIFT_OUTSIDE_SCOPE")
    require(len(base["identity"])==3 and len(base["neighbors"])==8 and len(base["routes"])==6
            and len(set(base["icmp"]))==6 and base["http"]["status"]=="available"
            and base["http"]["backend"]=="BACKEND_HQ","POSTCONDITIONS_INCOMPLETE")
    events=t["events"]
    expected=PREFIX+(["APPROVED_RESTORE"] if source=="HUMAN_APPROVED" else [])+SUFFIX
    require([e["state"] for e in events]==expected,"SEQUENCE_INVALID")
    clocks=[e["monotonic"] for e in events]
    require(all(type(x) in (float,int) and math.isfinite(x) for x in clocks)
            and clocks==sorted(clocks),"CLOCK_INVALID")
    e={x["state"]:x for x in events}
    require(e["APPROVED_EXPERIMENT"]["approver_uid"]==0,"EXPERIMENT_NOT_APPROVED")
    require(all(e[s]["source"]==source for s in SUFFIX),"SOURCE_MISMATCH")
    require(e["DRIFT_APPLIED"]["observed"]==150 and e["RESTORING"]["observed"]==150
            and e["RESTORED_UNVERIFIED"]["observed"]==100 and e["VERIFIED"]["observed"]==100,
            "COST_EVIDENCE_INVALID")
    def dt(a,b):
        return round(e[b]["monotonic"]-e[a]["monotonic"],6)
    if source=="HUMAN_APPROVED":
        require(e["APPROVED_RESTORE"]["approver_uid"]==0,"RESTORE_NOT_APPROVED")
    return {"rfc_id":t["rfc_id"],"source":source,"status":"VERIFIED",
            "drift_verification_s":dt("DRIFT_APPLIED","DRIFT_VERIFIED"),
            "decision_and_revalidation_s":dt("DRIFT_VERIFIED","APPROVED_RESTORE") if source=="HUMAN_APPROVED" else None,
            "action_from_approval_s":dt("APPROVED_RESTORE","RESTORED_UNVERIFIED") if source=="HUMAN_APPROVED" else None,
            "restoring_to_restored_s":dt("RESTORING","RESTORED_UNVERIFIED"),
            "postverification_s":dt("RESTORED_UNVERIFIED","VERIFIED"),
            "cycle_s":dt("DRIFT_APPLIED","VERIFIED"),
            "scope":TARGET,"other_costs_unchanged":7,"icmp_samples_success":6,
            "http_sample_available":True,"baseline_restored":True}


def compare(watchdog,human):
    a=evaluate(watchdog,"WATCHDOG")
    b=evaluate(human,"HUMAN_APPROVED")
    require(a["rfc_id"]!=b["rfc_id"],"DUPLICATE_RFC")
    return {"schema":"NETLAB360_S07_OSPF_CYCLE_COMPARISON_V1",
            "mode":"HISTORICAL_DESCRIPTIVE_COMPARISON","results":[a,b],
            "statistical_generalization":False,"continuous_availability_measured":False,
            "network_mutations_authorized":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("watchdog",type=Path)
    p.add_argument("human",type=Path)
    a=p.parse_args()
    print(json.dumps(compare(json.loads(a.watchdog.read_text()),
                             json.loads(a.human.read_text())),indent=2,allow_nan=False))


if __name__=="__main__":
    main()
