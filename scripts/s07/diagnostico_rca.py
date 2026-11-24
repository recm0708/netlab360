"""Hipótesis RCA explicables, históricas y estrictamente de solo lectura."""
from collections import Counter
from uuid import NAMESPACE_URL, uuid5

from correlacion_evidencias import correlate

SCHEMA = "NETLAB360_S07_RCA_V1"
UNKNOWN = {"UNAVAILABLE", "INCONSISTENT", "ADMIN_UNKNOWN", "ICMP_UNKNOWN",
           "HTTP_UNKNOWN", "ROUTER_UNKNOWN", "TOPOLOGY_UNKNOWN"}


def diagnose(acquisition):
    corr = correlate(acquisition)
    ev = {e["event_id"]: e for e in corr["evidence"]}
    groups = {g["context_id"]: g for g in corr["groups"]}
    pairs = {tuple(p["event_ids"]) for p in corr["pairs"]}
    hypotheses = []
    gaps = []

    def linked(a, b):
        return a == b or tuple(sorted((a,b))) in pairs

    def group_rows(name):
        return [ev[k] for k in groups[name]["event_ids"]]

    def select(rows, labels):
        return [r for r in rows if r["usable"] and r["classification"] in labels]

    def add(rule, context, anchors, support, opposing, unknown, explanation, limit):
        if not anchors:
            return
        # An anchor is an actual deviation or inference, never absent evidence.
        keys = sorted({r["event_id"] for r in anchors})
        # All support/opposition must relate directly in time to at least one anchor.
        # No transitive propagation of evidence or multiplication by pair count.
        def eligible(rows):
            return sorted({r["event_id"] for r in rows
                           if r["usable"] and any(linked(r["event_id"], a) for a in keys)})
        supporting = sorted(set(keys + eligible(support)))
        against = sorted(set(eligible(opposing))-set(supporting))
        missing = sorted({r["event_id"] for r in unknown})
        # Conservative ordinal rank, not a probability. Direct scoped deviations
        # rank above a single inference; contradictions/missing data weaken rank.
        inferred = all(ev[k]["nature"] == "INFERENCE" for k in keys)
        level = "AMBIGUOUS" if against else "LIMITED" if inferred or missing else "SCOPED"
        hypotheses.append({
            "hypothesis_id":str(uuid5(NAMESPACE_URL, rule+":"+context+":"+":".join(keys))),
            "rule":rule,"context_id":context,"status":"HYPOTHESIS",
            "support_event_ids":supporting,"against_event_ids":against,
            "unknown_event_ids":missing,"anchor_event_ids":keys,
            "uncertainty":level,"explanation":explanation,"limitation":limit,
            "confirmed":False,"root_cause":None,"network_mutations_authorized":False})

    def unknown(rows):
        return [r for r in rows if r["classification"] in UNKNOWN or not r["usable"]]

    if corr["temporal_gate"]:
        for name,g in sorted(groups.items()):
            rows=group_rows(name)
            missing=unknown(rows)
            if missing:
                gaps.append({"context_id":name,"event_ids":sorted(r["event_id"] for r in missing)})
            if g["kind"]=="WAN_LINK":
                down=select(rows,{"ADMIN_DOWN"})
                full=select(rows,{"OSPF_FULL"})
                nonfull=select(rows,{"OSPF_NON_FULL"})
                up=select(rows,{"ADMIN_UP"})
                # Admin DOWN and FULL can coexist during transitions. Do not resolve by majority.
                add("WAN_ADMIN_DEVIATION",name,down,nonfull,up+full,missing,
                    "Se observó una desviación administrativa respecto a la línea base UP.",
                    "No demuestra pérdida de tráfico ni identifica la causa del cambio.")
                add("OSPF_ADJACENCY_DEVIATION",name,nonfull,down,full,missing,
                    "Una adyacencia OSPF explícita no está FULL.",
                    "No distingue fallo físico, configuración, transición o problema de protocolo.")
            elif g["kind"]=="FIB_SELECTION":
                fib=select(rows,{"FIB_BACKUP"})
                # Restrict contextual OSPF/admin data to the primary first hop.
                primary=[r for r in rows if r["subject"] in ("WAN","OSPF")
                         and (r["resource_id"].endswith("p") or "WAN-PRIMARIA-" in r["resource_id"])]
                add("FIB_BACKUP_SELECTED",name,fib,
                    select(primary,{"ADMIN_DOWN","OSPF_NON_FULL"}),[],
                    unknown(primary),
                    "El primer salto local utiliza la ruta de respaldo.",
                    "La selección no prueba pérdida de tráfico ni una causa raíz. FULL no excluye cambios de costo.")
            elif g["kind"]=="SITE":
                lacp=[r for r in rows if r["subject"]=="LACP"]
                add("LACP_MEMBER_DEVIATION",name,select(lacp,{"LACP_REDUCED","LACP_DOWN"}),[],[],unknown(lacp),
                    "La cantidad de miembros LACP difiere de la línea base 2/2.",
                    "No determina capacidad efectiva ni pérdida de servicio.")
                router=[r for r in rows if r["subject"]=="METRIC"]
                add("ROUTER_EXISTENCE_DEVIATION",name,select(router,{"ROUTER_STOPPED"}),[],[],unknown(router),
                    "El colector reporta que el contenedor no está ejecutándose.",
                    "No identifica causa de detención ni estado de forwarding.")
                # Compare two observations of the same VLAN; never use other VLANs as opposition.
                for resource in sorted({r["resource_id"] for r in rows if r["subject"]=="VLAN"}):
                    v=[r for r in rows if r["subject"]=="VLAN" and r["resource_id"]==resource]
                    add("VLAN_ADMIN_DEVIATION",name+":"+resource,select(v,{"ADMIN_DOWN"}),[],
                        select(v,{"ADMIN_UP"}),unknown(v),
                        "Estado administrativo VLAN distinto del diseño UP.",
                        "No confirma drift de configuración persistente ni conectividad de usuarios.")
            elif g["kind"]=="HTTP_SERVICE":
                for label,rule in (("HTTP_BACKUP","HTTP_BACKUP_SELECTED"),("HTTP_OFFLINE","HTTP_SERVICE_OFFLINE")):
                    add(rule,name,select(rows,{label}),[],[],missing,
                        "Se observó el respaldo HTTP." if label=="HTTP_BACKUP" else "El monitor reportó HTTP offline.",
                        "Alcance del monitor S2; no atribuir a WAN ni a un backend sin evidencia adicional.")
            elif g["kind"]=="CONTROL_PLANE":
                add("SDN_CONTROLLER_DEVIATION",name,select(rows,{"SDN_DISCONNECTED"}),[],[],missing,
                    "El controlador SDN se reporta desconectado.",
                    "No implica pérdida de tráfico ni eliminación de reglas OpenFlow.")
            elif g["kind"]=="ICMP_INFERENCE":
                add("ICMP_DEGRADATION_INDICATION",name,select(rows,{"ICMP_DEGRADED"}),[],[],missing,
                    "Consenso inferencial de degradación ICMP no confirmado.",
                    "No determina causa, pérdida de paquetes ni disponibilidad HTTP.")
            elif g["kind"]=="DATA_SOURCE":
                add("TELEMETRY_ACQUISITION_DEVIATION",name,select(rows,{"SCRAPE_DOWN","COLLECTOR_DOWN"}),[],[],missing,
                    "Se detectó un problema en la adquisición de telemetría.",
                    "No equivale a una falla de la red observada.")

    rank={"SCOPED":0,"LIMITED":1,"AMBIGUOUS":2}
    hypotheses.sort(key=lambda h:(rank[h["uncertainty"]],h["rule"],h["context_id"],h["hypothesis_id"]))
    for i,h in enumerate(hypotheses,1):
        h["rank"]=i
    status=("ABSTAIN_WINDOW" if not corr["temporal_gate"] else
            "HYPOTHESES_WITH_GAPS" if hypotheses and gaps else
            "HYPOTHESES" if hypotheses else
            "NO_CANDIDATE_WITH_GAPS" if gaps else "NO_CANDIDATE")
    return {"schema":SCHEMA,"mode":"HISTORICAL_WINDOW_RCA","evaluated_at_utc":corr["evaluated_at_utc"],
            "temporal_gate":corr["temporal_gate"],"status":status,
            "hypotheses":hypotheses,"coverage_gaps":gaps,
            "unique_evidence":len(ev),"unique_pairs":len(pairs),
            "by_uncertainty":dict(Counter(h["uncertainty"] for h in hypotheses)),
            "configuration_drift":"REQUIRES_SEPARATE_SOT_AUDIT",
            "root_cause":None,"confirmed_incidents":0,"network_mutations_authorized":False}
