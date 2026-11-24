"""Recomendaciones a partir de RCA recalculado; sin acciones ni aprobaciones."""
from diagnostico_rca import diagnose
from catalogo_runbooks import validate_action,catalog
from recuperacion_documental import cite

SCHEMA="NETLAB360_S07_RECOMMENDATION_V1"


def recommendation(h):
    rule,ctx=h["rule"],h["context_id"]
    mapping={
        "WAN_ADMIN_DEVIATION":("S07_READ_WAN_V1",{"link":ctx}),
        "OSPF_ADJACENCY_DEVIATION":("S07_READ_WAN_V1",{"link":ctx}),
        "FIB_BACKUP_SELECTED":("S07_READ_FIB_V1",{"route":ctx}),
        "HTTP_BACKUP_SELECTED":("S07_READ_HTTP_V1",{}),
        "HTTP_SERVICE_OFFLINE":("S07_READ_HTTP_V1",{}),
        "LACP_MEMBER_DEVIATION":("S07_READ_LACP_V1",{"site":ctx.removeprefix("SITE-")}),
        "SDN_CONTROLLER_DEVIATION":("S07_READ_SDN_V1",{}),
        "ICMP_DEGRADATION_INDICATION":("S07_READ_ICMP_V1",{"route":ctx.removeprefix("ICMP-").replace("-","_A_")}),
        "TELEMETRY_ACQUISITION_DEVIATION":("S07_READ_TELEMETRY_V1",{}),
        "ROUTER_EXISTENCE_DEVIATION":("S07_READ_ROUTER_V1",{"site":ctx.removeprefix("SITE-")}),
        "VLAN_ADMIN_DEVIATION":("S07_READ_VLAN_V1",{"vlan":ctx.split(":")[-1]}),
    }
    action,args=mapping[rule]
    actions=[validate_action(action,args)]
    if rule in ("FIB_BACKUP_SELECTED","OSPF_ADJACENCY_DEVIATION"):
        actions.append(validate_action("S07_AUDIT_OSPF_COST_V1",{}))
    all_specs=catalog()["actions"]
    refs=sorted({"POLICY",*(r for a in actions for r in all_specs[a["action_id"]]["references"])})
    return {"hypothesis_id":h["hypothesis_id"],"rule":rule,"uncertainty":h["uncertainty"],
            "decision":"ESCALATE_NO_CHANGE" if h["uncertainty"]!="SCOPED" else "INVESTIGATE_NO_CHANGE",
            "evidence_event_ids":h["support_event_ids"],"against_event_ids":h["against_event_ids"],
            "unknown_event_ids":h["unknown_event_ids"],"suggested_read_only_actions":actions,
            "citations":[cite(r) for r in refs],"requires_fresh_evidence":True,
            "network_mutations_authorized":False}


def recommend(acquisition):
    r=diagnose(acquisition)
    items=[recommendation(h) for h in r["hypotheses"]]
    decision=("ABSTAIN_NO_CHANGE" if not r["temporal_gate"] else
              "REVIEW_HYPOTHESES_NO_CHANGE" if items else
              "COLLECT_MISSING_EVIDENCE_NO_CHANGE" if r["coverage_gaps"] else "NO_INTERVENTION")
    return {"schema":SCHEMA,"mode":"HISTORICAL_ADVISORY_ONLY","evaluated_at_utc":r["evaluated_at_utc"],
            "decision":decision,"recommendations":items,"coverage_gaps":r["coverage_gaps"],
            "citations":[cite("POLICY"),cite("SCOPE")],"requires_fresh_evidence":True,
            "approval_granted":False,"network_mutations_authorized":False}
