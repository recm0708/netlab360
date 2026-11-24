"""Auditoría puntual de costos OSPF vs SoT S03; no modifica routers."""
from pathlib import Path
import importlib.util
import json
from datetime import datetime, timezone
import subprocess

import adaptador_frr as frr

SCHEMA="NETLAB360_S07_CONFIG_AUDIT_V1"


def now():
    return datetime.now(timezone.utc).isoformat()


def load_parser():
    path=Path(__file__).resolve().parents[1]/"validacion/s03-frr-compliance.py"
    spec=importlib.util.spec_from_file_location("s03_cost_parser",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_frr_costs


def desired(sot):
    if sot.get("source_status")!="candidate" or set(sot.get("devices",{}))!={"R-"+s for s in frr.SITES}:
        raise ValueError("SOT_IDENTITY_INVALID")
    result={}
    for s in frr.SITES:
        row=sot["devices"]["R-"+s]
        if row["container"]!=frr.NAMES[s]:
            raise ValueError("SOT_CONTAINER_INVALID")
        entries=row["wan"]
        costs={e["interface"]:e["ospf_cost"] for e in entries}
        baseline={i:10 if i.endswith("p") else 100 for i in frr.LINKS[s]}
        if len(entries)!=len(costs) or costs!=baseline or any(type(v) is not int for v in costs.values()):
            raise ValueError("SOT_COST_PROFILE_INVALID")
        result[s]=costs
    return result


def compare(site,wanted,observed,stamp):
    rows=[]
    for interface,cost in sorted(wanted.items()):
        got=observed.get(interface) if observed is not None else None
        status=("UNKNOWN" if observed is None or got is None else
                "COMPLIANT" if got==cost else "NON_COMPLIANT")
        rows.append({"site":site,"interface":interface,"expected":cost,"observed":got,
                     "observed_at_utc":stamp,"status":status,
                     "reason":"EXPLICIT_COST_ABSENT_OR_UNVERIFIED" if got is None else "EXPLICIT_COST_COMPARISON"})
    return rows


def collect():
    frr.management()
    ids=frr.ownership()
    path=Path.home()/"netlab360-bootstrap/s03/rendered/sot-s03.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size>262144:
        raise ValueError("SOT_PATH_INVALID")
    wanted=desired(json.loads(path.read_text(encoding="utf-8")))
    parser=load_parser()
    started=now()
    rows=[]
    for site in frr.SITES:
        observed=None
        stamp=None
        try:
            expected=ids["R-"+site]
            pid=frr.inspect(site,expected)
            raw=frr.run("sudo","-n","docker","exec",expected,"vtysh","-c","show running-config")
            stamp=now()
            # Persist only authorized cost fields; never export entire running-config.
            parsed=parser(raw)
            if frr.inspect(site,expected)==pid:
                observed=parsed
        except (RuntimeError,OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired):
            pass
        rows.extend(compare(site,wanted[site],observed,stamp))
    frr.management()
    return {"schema":SCHEMA,"mode":"SEPARATE_READ_ONLY_SOT_AUDIT","started_at_utc":started,
            "ended_at_utc":now(),"reference":"S03_CANDIDATE_SOT_MATCHED_S02_COST_PROFILE",
            "rows":rows,"historical_rca_causal_link":False,"network_mutations_authorized":False}


if __name__=="__main__":
    print(json.dumps(collect(),ensure_ascii=False,indent=2,allow_nan=False))
