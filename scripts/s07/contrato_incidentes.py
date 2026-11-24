"""Contrato de candidatos a incidente; no confirma causas ni ejecuta acciones."""
from __future__ import annotations

from uuid import uuid5, NAMESPACE_URL

from adquisicion_integrada import assess
from almacen_eventos import checked_event
from contrato_eventos import utc

SCHEMA="NETLAB360_S07_INCIDENT_V1"


def candidate(event, as_of):
    """Un candidato refiere evidencia explícita vigente, no un incidente confirmado."""
    e=checked_event(event)
    status, _=assess(e,as_of)
    if status!="ELIGIBLE":
        return None
    if e["kind"]=="INFERENCE":
        if e["state"]!="UNKNOWN" or e["details"].get("consensus")!="DEGRADED":
            return None
        reason="UNCONFIRMED_INFERENCE"
    elif e["state"] in ("DEGRADED","FAULT"):
        reason="OBSERVED_SCOPED_DEVIATION"
    else:
        return None
    return {"schema":SCHEMA,
            "incident_id":str(uuid5(NAMESPACE_URL,SCHEMA+":"+e["event_id"])),
            "status":"CANDIDATE","confirmed":False,"reason":reason,
            "source":e["source"],"subject":e["subject"],"resource_id":e["resource_id"],
            "site":e["site"],"peer_site":e["peer_site"],
            "observed_at_utc":e["observed_at_utc"],
            "evaluated_at_utc":utc(as_of).isoformat(),
            "evidence_event_ids":[e["event_id"]],
            "root_cause":None,"ground_truth":"UNKNOWN",
            "network_mutations_authorized":False}


def candidates(acquisition):
    """Solo proyectar candidatos desde una ventana íntegra y acotada."""
    from adquisicion_integrada import evaluate_window
    batch,window=acquisition["batch"],acquisition["window"]
    computed=evaluate_window(batch,window["started_at_utc"],
                             window["ended_at_utc"],window["elapsed_seconds"])
    if computed!=window:
        raise ValueError("WINDOW_CONTRACT_MISMATCH")
    if not computed["temporal_gate"]:
        return []
    return [c for e in batch["events"]
            if (c:=candidate(e,window["ended_at_utc"])) is not None]
