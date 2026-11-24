"""Contexto topológico de RCA S07: referencias a señales, no causalidad."""
from collections import Counter
from adquisicion_integrada import evaluate_window
from contrato_eventos import utc
from adaptador_frr import LINKS, SITES

SCHEMA = "NETLAB360_S07_RCA_CONTEXT_V1"


def inventory():
    """Identidades exactas y alcance esperado de las 58 señales S07."""
    rows = {}

    def add(source, subject, resource, site=None, peer=None):
        key = (source, subject, resource)
        if key in rows:
            raise ValueError("DUPLICATE_DESIGN_RESOURCE")
        rows[key] = (site, peer)
        return key

    groups = {}
    def group(name, kind, refs):
        groups[name] = {"kind":kind, "references":refs}

    def ref(source, subject, resource):
        return (source, subject, resource)

    noc, prom, frr, ia = "NOC_S05", "PROMETHEUS_S04", "FRR_S02", "IA_S06"
    topology = [add(noc,"TOPOLOGY","MULTISEDE"), add(prom,"TOPOLOGY","MULTISEDE")]
    acquisition = [add(prom,"EXPORTER","S04-EXPORTER"), add(prom,"EXPORTER","S04-COLLECTOR")]
    group("ACQUISITION","DATA_SOURCE",acquisition+topology)
    for site in SITES:
        refs=[add(noc,"LACP","LACP-"+site,site), add(prom,"METRIC","R-"+site,site)]
        prefix={"HQ":100,"S1":200,"S2":300}[site]
        for vlan in (prefix+10,prefix+20,prefix+30):
            refs.extend([add(noc,"VLAN",f"VLAN-{vlan}",site),
                         add(prom,"VLAN",f"VLAN-{vlan}",site)])
        group("SITE-"+site,"SITE",refs)
    for peer in ("S1","S2"):
        for suffix,role in (("p","PRIMARY"),("b","BACKUP")):
            iface=peer.lower()+suffix
            name=f"WAN-HQ-{peer}-{role}"
            refs=[add(noc,"WAN",f"WAN-{'PRIMARIA' if suffix=='p' else 'RESPALDO'}-HQ-{peer}","HQ",peer)]
            for site,other in (("HQ",peer),(peer,"HQ")):
                if LINKS[site][iface][0]!=other:
                    raise ValueError("DESIGN_LINK_MISMATCH")
                refs.extend([add(prom,"WAN",f"WAN-END-{site}-{iface}",site,other),
                             add(frr,"OSPF",f"OSPF-{site}-{iface}",site,other)])
            group(name,"WAN_LINK",refs)
        group("ICMP-HQ-"+peer,"ICMP_INFERENCE",
              [add(ia,"ICMP_DIAGNOSIS","HQ_A_"+peer,"HQ",peer)])
    for site in SITES:
        for peer in SITES:
            if site==peer:
                continue
            next_peer=peer if site=="HQ" else site
            group(f"ROUTE-{site}-{peer}","FIB_SELECTION",[
                add(frr,"FIB",f"FIB-{site}-{peer}",site,peer),
                *groups[f"WAN-HQ-{next_peer}-PRIMARY"]["references"],
                *groups[f"WAN-HQ-{next_peer}-BACKUP"]["references"],
            ])
    group("HTTP-HA","HTTP_SERVICE",[add(noc,"HTTP_HA","FRONTAL_HQ","HQ","S2")])
    group("SDN-FAUCET","CONTROL_PLANE",[add(noc,"SDN","FAUCET")])
    return rows,groups


def build_context(acquisition):
    """Revalidar la ventana y las identidades; no usar datos fuera de vigencia."""
    batch, window=acquisition["batch"], acquisition["window"]
    verified=evaluate_window(batch,window["started_at_utc"],
                             window["ended_at_utc"],window["elapsed_seconds"])
    if verified!=window:
        raise ValueError("WINDOW_CONTRACT_MISMATCH")
    expected, groups=inventory()
    index={}
    for e in batch["events"]:
        key=(e["source"],e["subject"],e["resource_id"])
        if key not in expected or key in index or (e["site"],e["peer_site"])!=expected[key]:
            raise ValueError("CONTEXT_RESOURCE_MISMATCH")
        index[key]=e
    if set(index)!=set(expected):
        raise ValueError("CONTEXT_INVENTORY_MISMATCH")
    validity={row["event_id"]:row["eligibility"] for row in window["rows"]}
    out=[]
    for name,group in sorted(groups.items()):
        refs=[]
        for key in group["references"]:
            e=index[key]
            eligible=validity[e["event_id"]]=="ELIGIBLE" and window["temporal_gate"]
            refs.append({"event_id":e["event_id"],"source":e["source"],
                         "subject":e["subject"],"resource_id":e["resource_id"],
                         "eligibility":validity[e["event_id"]],
                         "usable_in_window":eligible,
                         "state":e["state"] if eligible else "UNKNOWN"})
        out.append({"context_id":name,"kind":group["kind"],
                    "references":refs,"eligible":sum(r["usable_in_window"] for r in refs),
                    "total":len(refs)})
    return {"schema":SCHEMA,"mode":"HISTORICAL_WINDOW_CONTEXT",
            "evaluated_at_utc":utc(window["ended_at_utc"]).isoformat(),
            "temporal_gate":window["temporal_gate"],"unique_signals":len(index),
            "groups":out,"root_cause":None,"network_mutations_authorized":False,
            "source_dependency_notes":[
                "NOC y Prometheus pueden compartir el colector S04; no son votos independientes.",
                "Una ruta FIB acredita seleccion local, no recorrido extremo a extremo.",
                "HTTP HA y Faucet tienen alcance propio; no se atribuyen automaticamente a una WAN.",
                "La inferencia ICMP no demuestra causalidad ni disponibilidad HTTP."
            ]}
