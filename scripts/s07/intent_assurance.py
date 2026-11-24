"""Intent Assurance: dimensiones separadas, sin cambios de infraestructura."""
from datetime import datetime
from collections import Counter
from contrato_eventos import utc
from correlacion_evidencias import correlate
from adaptador_frr import LINKS

SCHEMA="NETLAB360_S07_INTENT_V1"


def evaluate(acquisition,audit):
    corr=correlate(acquisition)
    end=utc(audit["ended_at_utc"])
    start=utc(audit["started_at_utc"])
    if (audit.get("schema")!="NETLAB360_S07_CONFIG_AUDIT_V1"
        or audit.get("reference")!="S03_CANDIDATE_SOT_MATCHED_S02_COST_PROFILE"
        or audit.get("network_mutations_authorized") is not False
        or audit.get("historical_rca_causal_link") is not False
        or not 0<=(end-start).total_seconds()<=30):
        raise ValueError("AUDIT_CONTRACT_INVALID")
    wanted={(s,i):10 if i.endswith("p") else 100 for s in LINKS for i in LINKS[s]}
    costs={}
    for r in audit["rows"]:
        key=(r["site"],r["interface"])
        if key not in wanted or key in costs or type(r["expected"]) is not int or r["expected"]!=wanted[key]:
            raise ValueError("COST_INVENTORY_INVALID")
        got=r["observed"]
        if got is not None and (type(got) is not int or not 1<=got<=65535):
            raise ValueError("COST_VALUE_INVALID")
        status="UNKNOWN" if got is None else "COMPLIANT" if got==wanted[key] else "NON_COMPLIANT"
        if status!=r["status"]:
            raise ValueError("COST_STATUS_INVALID")
        if got is not None and not start<=utc(r["observed_at_utc"])<=end:
            raise ValueError("COST_TIMESTAMP_INVALID")
        costs[key]=dict(r)
    if set(costs)!=set(wanted):
        raise ValueError("COST_INVENTORY_INCOMPLETE")
    classes={e["resource_id"]:e["classification"] for e in corr["evidence"]
             if e["source"]=="FRR_S02"}
    routes=[classes[k] for k in sorted(classes) if k.startswith("FIB-")]
    neighbors=[classes[k] for k in sorted(classes) if k.startswith("OSPF-")]
    http=next(e["classification"] for e in corr["evidence"] if e["resource_id"]=="FRONTAL_HQ")
    def aggregate(values,good,bad):
        return "NOT_MET" if any(v in bad for v in values) else "MET" if values and all(v in good for v in values) else "UNKNOWN"
    compliance=aggregate([r["status"] for r in costs.values()],{"COMPLIANT"},{"NON_COMPLIANT"})
    preference=aggregate(routes,{"FIB_PRIMARY"},{"FIB_BACKUP"})
    adjacency=aggregate(neighbors,{"OSPF_FULL"},{"OSPF_NON_FULL"})
    availability=aggregate([http],{"HTTP_PRIMARY","HTTP_BACKUP"},{"HTTP_OFFLINE"})
    # Separate timestamps, no retrospective causal claim.
    window_end=utc(corr["evaluated_at_utc"])
    synchronized=(corr["temporal_gate"] and 0<=(start-window_end).total_seconds()<=10
                  and (end-window_end).total_seconds()<=30)
    return {"schema":SCHEMA,"mode":"READ_ONLY_INTENT_EVALUATION",
            "window_ended_at_utc":window_end.isoformat(),"audit_ended_at_utc":end.isoformat(),
            "temporally_aligned":synchronized,"configuration_compliance":compliance,
            "preferred_route_intent":preference,"ospf_adjacency_intent":adjacency,
            "http_observed_availability":availability,"end_to_end_availability":"NOT_MEASURED",
            "cost_counts":dict(Counter(r["status"] for r in costs.values())),
            "cost_rows":list(costs.values()),"root_cause":None,
            "network_mutations_authorized":False}
