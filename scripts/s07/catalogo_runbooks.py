"""Catálogo declarativo: no contiene ejecutores ni acepta comandos."""
from copy import deepcopy
from adaptador_frr import LINKS

SCHEMA="NETLAB360_S07_RUNBOOK_CATALOG_V1"
VERSION=1
SITES=("HQ","S1","S2")
WAN=("WAN-HQ-S1-PRIMARY","WAN-HQ-S1-BACKUP","WAN-HQ-S2-PRIMARY","WAN-HQ-S2-BACKUP")
ROUTES=tuple(f"ROUTE-{a}-{b}" for a in SITES for b in SITES if a!=b)
ICMP=("HQ_A_S1","HQ_A_S2")
VLANS=tuple(f"VLAN-{v}" for v in (110,120,130,210,220,230,310,320,330))


def entry(scope,args,refs,requirements,description,change=False):
    return {"scope":scope,"arguments":args,"references":refs,
            "requirements":requirements,"description":description,
            "risk":"CONTROLLED_CHANGE" if change else "LOW_READ_ONLY",
            "reversibility":"CAPTURE_PREVIOUS_STATE_AND_VERIFIED_ROLLBACK_REQUIRED" if change else "NO_NETWORK_MUTATION",
            "mutation":change,"approval_required":change,
            "execution_status":"BLOCKED_PENDING_POLICY_AND_EXECUTOR" if change else "DECLARATIVE_READ_ONLY",
            "execution_authorized":False}


def catalog():
    common=["FRESH_EVIDENCE","OWNERSHIP_VERIFIED","MANAGEMENT_PROTECTED"]
    entries={
        "S07_READ_WAN_V1":entry("WAN_LINK",{"link":WAN},["WAN","SCOPE","ARCH","INVENTORY"],common,"Revisar extremos administrativos y adyacencias."),
        "S07_READ_FIB_V1":entry("FIRST_HOP",{"route":ROUTES},["WAN","SCOPE","INVENTORY"],common,"Revisar selección FIB del primer salto."),
        "S07_AUDIT_OSPF_COST_V1":entry("OSPF_COST_PROFILE",{},["COST","WAN","POLICY","INVENTORY"],common+["SOT_VALIDATED"],"Comparar costos explícitos con SoT candidato S03."),
        "S07_READ_HTTP_V1":entry("HTTP_MONITOR",{},["HA","SCOPE"],common,"Revisar disponibilidad observada y backend; no cambiar selección."),
        "S07_READ_LACP_V1":entry("SITE_BOND",{"site":SITES},["LACP","WAN"],common,"Revisar miembros y estado LACP de la sede."),
        "S07_READ_SDN_V1":entry("FAUCET",{},["SDN","ARCH"],common,"Revisar controlador y reglas sin intervenir."),
        "S07_READ_ICMP_V1":entry("ICMP_INFERENCE",{"route":ICMP},["IA","SCOPE"],common+["INFERENCE_SCOPE_VERIFIED"],"Revisar calidad y procedencia de inferencia ICMP."),
        "S07_READ_TELEMETRY_V1":entry("S04_COLLECTION",{},["TELEMETRY","SCOPE"],common,"Verificar adquisición y vigencia de telemetría."),
        "S07_READ_ROUTER_V1":entry("ROUTER_EXISTENCE",{"site":SITES},["WAN","ARCH"],common,"Verificar identidad y existencia del router."),
        "S07_READ_VLAN_V1":entry("VLAN_ADMIN",{"vlan":VLANS},["WAN","ARCH"],common,"Contrastar estado administrativo de la VLAN."),
        "S07_RESTORE_OSPF_COST_V1":entry("OSPF_COST_PROFILE",{"site":SITES,"interface":("s1p","s1b","s2p","s2b"),"cost":(10,100)},["COST","POLICY","ARCH","INVENTORY"],common+["SOT_VALIDATED","RFC_APPROVED","EXCLUSIVE_LOCK","WATCHDOG_READY","ROLLBACK_VERIFIED"],"Propuesta futura de restauración del costo deseado; no ejecutable en S07-003.",True),
    }
    return {"schema":SCHEMA,"version":VERSION,"actions":deepcopy(entries),
            "network_mutations_authorized":False}


def validate_action(action_id,arguments):
    if type(action_id) is not str or type(arguments) is not dict:
        raise ValueError("ACTION_CONTRACT_INVALID")
    actions=catalog()["actions"]
    if action_id not in actions:
        raise ValueError("ACTION_NOT_ALLOWED")
    spec=actions[action_id]["arguments"]
    if set(arguments)!=set(spec):
        raise ValueError("ARGUMENT_KEYS_INVALID")
    for key,allowed in spec.items():
        value=arguments[key]
        if not any(type(value) is type(a) and value==a for a in allowed):
            raise ValueError("ARGUMENT_VALUE_INVALID")
    if action_id=="S07_RESTORE_OSPF_COST_V1":
        site,iface,cost=(arguments[k] for k in ("site","interface","cost"))
        if iface not in LINKS[site] or cost!=(10 if iface.endswith("p") else 100):
            raise ValueError("ARGUMENT_SCOPE_INVALID")
    return {"action_id":action_id,"arguments":deepcopy(arguments),
            "execution_authorized":False}
