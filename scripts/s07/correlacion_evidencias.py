"""Clasificación de evidencia y correlación temporal acotada, sin causalidad."""
from collections import Counter
from itertools import combinations

from contexto_rca import build_context
from contrato_eventos import utc
from adaptador_frr import LINKS, LOOPS, STATES
from adaptadores_noc import METHODS

SCHEMA = "NETLAB360_S07_RCA_EVIDENCE_V1"
MAX_PAIR_GAP = 10


def classification(event):
    """Devuelve etiqueta y naturaleza de una señal elegible.

    Un estado UNKNOWN puede aportar una observación administrativa.
    Los detalles incompatibles con el contrato específico no aportan evidencia.
    """
    source, subject = event["source"], event["subject"]
    d, state = event["details"], event["state"]
    scope = d.get("scope")

    def match(label, nature, expected):
        return (label, nature) if state == expected else ("INCONSISTENT", "UNUSABLE")

    if source == "PROMETHEUS_S04" and d.get("timestamp_scope") != "PROMETHEUS_SCRAPE":
        return "INCONSISTENT", "UNUSABLE"
    if subject in ("WAN", "VLAN") and scope == "ADMIN_STATE_ONLY":
        if source == "NOC_S05":
            value = {"admin-up": "UP", "admin-down": "DOWN",
                     "unknown": "UNKNOWN", "offline": "UNKNOWN"}.get(d.get("admin_state"))
        else:
            value = {-1:"UNKNOWN",0:"DOWN",1:"UP"}.get(d.get("admin_up")) if type(d.get("admin_up")) is int else None
        if value:
            return match("ADMIN_"+value, "ADMINISTRATIVE", "UNKNOWN")
    elif subject == "OSPF" and scope == "OSPF_NEIGHBOR_ONLY":
        iface = event["resource_id"].rsplit("-",1)[-1]
        neighbor = d.get("neighbor_state")
        if (d.get("interface")==iface and neighbor in STATES
                and d.get("router_id")==LOOPS[event["peer_site"]]):
            return match("OSPF_FULL" if neighbor=="Full" else "OSPF_NON_FULL",
                         "OPERATIONAL", "NORMAL" if neighbor=="Full" else "DEGRADED")
    elif subject == "FIB" and scope == "FIB_SELECTION_ONLY":
        iface = d.get("interface")
        link = LINKS[event["site"]].get(iface)
        peer = event["peer_site"] if event["site"]=="HQ" else "HQ"
        if (link and link[0]==peer and d.get("gateway")==link[2]
                and d.get("destination")==LOOPS[event["peer_site"]]
                and d.get("traffic_measured") is False):
            selection = "PRIMARY" if iface.endswith("p") else "BACKUP"
            if d.get("selection")==selection:
                return match("FIB_"+selection,"OPERATIONAL",
                             "NORMAL" if selection=="PRIMARY" else "DEGRADED")
    elif subject == "LACP" and scope == "BOND_MEMBER_STATE":
        a,b=d.get("switch_members"),d.get("client_members")
        if type(a) is int and type(b) is int and 0<=a<=2 and 0<=b<=2:
            n=min(a,b)
            return match(("LACP_DOWN","LACP_REDUCED","LACP_FULL")[n],
                         "OPERATIONAL",("FAULT","DEGRADED","NORMAL")[n])
    elif subject == "SDN" and scope == "CONTROLLER_ONLY":
        connected,flows=d.get("connected"),d.get("flow_count")
        if connected is True and type(flows) is int and 0<flows<=10**9:
            return match("SDN_CONNECTED","CONTROL_PLANE","NORMAL")
        if connected is False and flows is None:
            return match("SDN_DISCONNECTED","CONTROL_PLANE","FAULT")
    elif subject == "HTTP_HA" and scope == "HTTP_FROM_S2":
        key=(d.get("status"),d.get("active_backend"),d.get("selected_path"))
        choices={
            ("running","BACKEND_HQ","PRINCIPAL"):("HTTP_PRIMARY","NORMAL"),
            ("running","BACKEND_S1","RESPALDO"):("HTTP_BACKUP","DEGRADED"),
            ("offline",None,None):("HTTP_OFFLINE","FAULT"),
            ("running",None,None):("HTTP_UNKNOWN","UNKNOWN"),
            ("unknown",None,None):("HTTP_UNKNOWN","UNKNOWN"),
        }
        if key in choices:
            label,expected=choices[key]
            return match(label,"SERVICE",expected)
    elif subject == "ICMP_DIAGNOSIS" and scope == "HQ_CLIENT_EGRESS_NETWORK_STATE":
        votes=[d.get(k) for k in METHODS]
        if all(v in ("NORMAL","DEGRADED") for v in votes):
            consensus=votes[0] if len(set(votes))==1 else "UNKNOWN"
            if d.get("consensus")==consensus:
                return match("ICMP_"+consensus,"INFERENCE",
                             "NORMAL" if consensus=="NORMAL" else "UNKNOWN")
    elif subject == "EXPORTER":
        key,expected_scope=("up","SCRAPE_AVAILABILITY") if event["resource_id"]=="S04-EXPORTER" else ("source_up","COLLECTOR_READ")
        value=d.get(key)
        if scope==expected_scope and type(value) is int and value in (0,1):
            expected="NORMAL" if value==1 else "FAULT" if key=="up" else "UNKNOWN"
            return match(("SCRAPE_" if key=="up" else "COLLECTOR_")+("UP" if value else "DOWN"),"ACQUISITION",expected)
    elif subject == "METRIC" and scope == "CONTAINER_RUNNING_ONLY":
        value=d.get("running")
        if type(value) is int and value in (-1,0,1):
            return match({-1:"ROUTER_UNKNOWN",0:"ROUTER_STOPPED",1:"ROUTER_RUNNING"}[value],"EXISTENCE","UNKNOWN")
    elif subject == "TOPOLOGY":
        value=d.get("reported_topology")
        if source=="NOC_S05" and scope=="TOPOLOGY_OBSERVATION" and value in ("active","offline"):
            return match("TOPOLOGY_"+value.upper(),"EXISTENCE","NORMAL" if value=="active" else "UNKNOWN")
        if source=="PROMETHEUS_S04" and scope=="ROUTER_EXISTENCE_ONLY" and value in ("active","offline","partial","unknown"):
            return match("TOPOLOGY_"+value.upper(),"EXISTENCE","UNKNOWN")
    return "INCONSISTENT","UNUSABLE"


def dependence(a,b):
    if a["source"]==b["source"]:
        return "SAME_SOURCE"
    if {a["source"],b["source"]}=={"NOC_S05","PROMETHEUS_S04"}:
        return "POTENTIALLY_SHARED_COLLECTOR"
    return "DISTINCT_SOURCES_NOT_PROVEN_INDEPENDENT"


def correlate(acquisition):
    context=build_context(acquisition)
    events={e["event_id"]:e for e in acquisition["batch"]["events"]}
    refs={r["event_id"]:r for g in context["groups"] for r in g["references"]}
    evidence={}
    for key,e in sorted(events.items()):
        ref=refs[key]
        if not ref["usable_in_window"]:
            label,nature="UNAVAILABLE","UNUSABLE"
        else:
            label,nature=classification(e)
        evidence[key]={"event_id":key,"source":e["source"],"subject":e["subject"],
                       "resource_id":e["resource_id"],"site":e["site"],"peer_site":e["peer_site"],
                       "observed_at_utc":e["observed_at_utc"],
                       "eligibility":ref["eligibility"],"classification":label,
                       "nature":nature,"usable":nature!="UNUSABLE"}
    pairs={}
    groups=[]
    for g in context["groups"]:
        keys=sorted(r["event_id"] for r in g["references"])
        linked=[]
        for a,b in combinations(keys,2):
            if not evidence[a]["usable"] or not evidence[b]["usable"]:
                continue
            gap=abs((utc(events[a]["observed_at_utc"])-utc(events[b]["observed_at_utc"])).total_seconds())
            if gap>MAX_PAIR_GAP:
                continue
            pair_id=a+":"+b
            if pair_id not in pairs:
                pairs[pair_id]={"pair_id":pair_id,"event_ids":[a,b],
                                "gap_seconds":round(gap,6),
                                "dependence":dependence(events[a],events[b])}
            linked.append(pair_id)
        groups.append({"context_id":g["context_id"],"kind":g["kind"],"event_ids":keys,
                       "pair_ids":linked})
    return {"schema":SCHEMA,"mode":"HISTORICAL_WINDOW_EVIDENCE",
            "evaluated_at_utc":context["evaluated_at_utc"],
            "temporal_gate":context["temporal_gate"],"pair_gap_limit_seconds":MAX_PAIR_GAP,
            "evidence":list(evidence.values()),"groups":groups,
            "pairs":[pairs[k] for k in sorted(pairs)],
            "by_classification":dict(Counter(e["classification"] for e in evidence.values())),
            "by_dependence":dict(Counter(p["dependence"] for p in pairs.values())),
            "root_cause":None,"network_mutations_authorized":False}
