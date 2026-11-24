#!/usr/bin/env python3
"""Evaluación histórica S07; no colecta señales, ejecuta runbooks ni modifica red."""
import argparse
from copy import deepcopy
from datetime import timedelta
import json
from pathlib import Path
from adquisicion_integrada import evaluate_window
from contrato_eventos import utc
from diagnostico_rca import diagnose
from recomendaciones_rca import recommend
from catalogo_runbooks import validate_action
from comparar_ciclos_ospf import compare

STAGES=("BASELINE","FAULT","RECOVERY")
WAN={("WAN_ADMIN_DEVIATION","WAN-HQ-S1-PRIMARY"),
     *(("FIB_BACKUP_SELECTED","ROUTE-"+r) for r in ("HQ-S1","S1-HQ","S1-S2"))}
HTTP={("HTTP_BACKUP_SELECTED","HTTP-HA")}
TARGETS={"HTTP":HTTP,"LACP":{("LACP_MEMBER_DEVIATION","SITE-S1")},
         "WAN":WAN,"SDN":set(),"COMPOUND":WAN|HTTP}

def require(value,reason):
    if not value: raise ValueError(reason)

def load(path):
    return json.loads(path.read_text())

def expected_actions(rule,context):
    if rule=="HTTP_BACKUP_SELECTED": return [("S07_READ_HTTP_V1",{})]
    if rule=="LACP_MEMBER_DEVIATION": return [("S07_READ_LACP_V1",{"site":"S1"})]
    if rule=="WAN_ADMIN_DEVIATION": return [("S07_READ_WAN_V1",{"link":context})]
    if rule=="FIB_BACKUP_SELECTED":
        return [("S07_READ_FIB_V1",{"route":context}),("S07_AUDIT_OSPF_COST_V1",{})]
    raise ValueError("UNEXPECTED_RULE")

def assess(case,stage,r,rec):
    require(case in TARGETS and stage in STAGES,"INVALID_SCOPE")
    require(r["temporal_gate"] and not r["network_mutations_authorized"]
            and not rec["network_mutations_authorized"] and not rec["approval_granted"],"POLICY_OR_WINDOW")
    wanted=TARGETS[case] if stage=="FAULT" else set()
    found={(h["rule"],h["context_id"]):h for h in r["hypotheses"]}
    require(len(found)==len(r["hypotheses"]),"DUPLICATE_HYPOTHESIS")
    items={i["hypothesis_id"]:i for i in rec["recommendations"]}
    require(len(items)==len(rec["recommendations"]) and set(items)=={h["hypothesis_id"] for h in found.values()},"RECOMMENDATION_LINK")
    missing=wanted-set(found); unexpected=set(found)-wanted
    correct=0
    for key,h in found.items():
        require(not h["confirmed"] and not h["network_mutations_authorized"],"CAUSALITY_OR_AUTHORIZATION")
        item=items[h["hypothesis_id"]]
        require(not item["network_mutations_authorized"] and item["requires_fresh_evidence"],"ITEM_POLICY")
        acts=item["suggested_read_only_actions"]
        require(all(validate_action(x["action_id"],x["arguments"])==x and not x["execution_authorized"] for x in acts),"ACTION_CONTRACT")
        if key in wanted:
            actual=[(x["action_id"],x["arguments"]) for x in acts]
            require(actual==expected_actions(*key),"RUNBOOK_MISMATCH")
            require(item["decision"]==("INVESTIGATE_NO_CHANGE" if h["uncertainty"]=="SCOPED" else "ESCALATE_NO_CHANGE"),"UNCERTAINTY_POLICY")
            correct+=1
    decision="REVIEW_HYPOTHESES_NO_CHANGE" if found else "COLLECT_MISSING_EVIDENCE_NO_CHANGE" if r["coverage_gaps"] else "NO_INTERVENTION"
    require(rec["decision"]==decision,"DECISION_MISMATCH")
    return {"case":case,"stage":stage,"expected":len(wanted),"observed":len(found),
            "matched":len(wanted&set(found)),"unexpected":[list(x) for x in sorted(unexpected)],
            "missing":[list(x) for x in sorted(missing)],"correct_recommendations":correct,
            "decision":decision,"coverage_gaps":len(r["coverage_gaps"]),
            "hypotheses":[{"rule":h["rule"],"context":h["context_id"],"uncertainty":h["uncertainty"],
                           "actions":items[h["hypothesis_id"]]["suggested_read_only_actions"]} for h in r["hypotheses"]]}

def review(services,network,compound,watchdog,human,denial):
    rows=[]; sample=None
    for case,directory in (("HTTP",services),("LACP",services),("WAN",network),("SDN",network),("COMPOUND",compound)):
        summary=load(directory/(case.lower()+"-summary.json"))
        require(summary["restored"] is True,"RESTORATION_NOT_VERIFIED")
        for stage in STAGES:
            name=summary[stage.lower()]
            if isinstance(name,dict): name=name["file"]
            require(Path(name).name==name,"PATH_INVALID")
            d=load(directory/name); a=d["acquisition"]
            require(d["matched"] and d["stage"]==stage and len(a["batch"]["events"])==58,"WINDOW_INVALID")
            r=diagnose(a); rec=recommend(a)
            require(r==d["diagnosis"] and rec==d["recommendation"],"REPRODUCTION_MISMATCH")
            row=assess(case,stage,r,rec)
            row.update(file=str(directory/name),window_seconds=a["window"]["elapsed_seconds"],
                       eligibility=a["window"]["by_eligibility"])
            if case=="SDN":
                ev=d["direct_evidence"]
                require(ev["port"]==("DOWN" if stage=="FAULT" else "UP")
                        and ev["a_b"]==("DENIED" if stage=="FAULT" else "PERMITTED") and ev["b_c"]=="DENIED","SDN_PROBE_INVALID")
                row["direct_evidence"]=ev
            if case=="COMPOUND" and stage=="FAULT": sample=a
            rows.append(row)
    require(sample is not None,"MISSING_COMPOUND")
    altered=deepcopy(sample); w=altered["window"]
    end=utc(w["ended_at_utc"])+timedelta(seconds=31)
    altered["window"]=evaluate_window(altered["batch"],w["started_at_utc"],end.isoformat(),w["elapsed_seconds"]+31)
    r=diagnose(altered); rec=recommend(altered)
    require(not r["temporal_gate"] and not r["hypotheses"] and rec["decision"]=="ABSTAIN_NO_CHANGE" and not rec["approval_granted"],"ABSTENTION_FAILED")
    metrics=compare(load(watchdog),load(human))
    rejected=load(denial)
    require(rejected["ok"] is False and rejected["reason"]=="RESTORATION_APPROVAL_DENIED","DENIAL_NOT_VERIFIED")
    counts={k:sum(row[k] for row in rows) for k in ("expected","observed","matched","correct_recommendations")}
    counts.update(unexpected=sum(len(row["unexpected"]) for row in rows),missing=sum(len(row["missing"]) for row in rows))
    require(counts=={"expected":11,"observed":11,"matched":11,"correct_recommendations":11,"unexpected":0,"missing":0},"ACCEPTANCE_COUNTS")
    return {"schema":"NETLAB360_S07_EVALUATION_V1","windows":15,"observations":870,
            "rows":rows,"counts":counts,"abstention":{"mode":"DERIVED_OFFLINE_COUNTERFACTUAL","decision":rec["decision"],
            "hypotheses":len(r["hypotheses"]),"window_seconds":altered["window"]["elapsed_seconds"]},
            "real_denial":rejected["reason"],"ospf":metrics,
            "sdn_port_automatic_detection":False,"statistical_generalization":False,
            "continuous_availability_measured":False,"network_mutations_authorized":False}

def show(d,section):
    """Presentación histórica ANSI, sin modificar el informe JSON."""
    reset="\033[0m"
    colors={"cyan":"\033[1;36m","green":"\033[1;32m","yellow":"\033[1;33m"}
    def color(value,tone):
        return colors[tone]+str(value)+reset
    def rule():
        print("-"*96)
    def line():
        print(color("="*96,"cyan"))
    names={"HTTP":"ESCENARIO HTTP HA Y RCA","LACP":"ESCENARIO LACP S1 Y RCA",
           "WAN":"CONMUTACION WAN Y RCA","SDN":"SDN - PLANO DE DATOS AISLADO",
           "COMPOUND":"ESCENARIO COMPUESTO WAN + HTTP",
           "EVALUACION":"EVALUACION DE HIPOTESIS Y RECOMENDACIONES",
           "CONTROLES":"ABSTENCION, CONTROLES Y LIMITES"}
    line()
    print(" NETLAB360 | S07 - "+names[section])
    line()
    print("Modalidad: EVALUACION HISTORICA | SOLO LECTURA")
    print("Zona horaria del laboratorio: America/Panama")
    rule()
    if section in TARGETS:
        rows=[r for r in d["rows"] if r["case"]==section]
        print(f"{'ETAPA':12} {'HIPOTESIS':>10} {'BRECHAS':>10} {'VENTANA (s)':>14}  DECISION")
        for r in rows:
            tone="yellow" if r["stage"]=="FAULT" else "green"
            print(color(f"{r['stage']:12}",tone)+
                  f" {r['observed']:10} {r['coverage_gaps']:10} {r['window_seconds']:14.6f}  "+
                  ("REVISAR" if r["hypotheses"] else "RECOPILAR EVIDENCIA" if r["coverage_gaps"] else "SIN INTERVENCION"))
        rule()
        if section=="SDN":
            print(f"{'ETAPA':12} {'PUERTO':8} {'A-B':12} {'B-C':12} FAUCET")
            for r in rows:
                e=r["direct_evidence"]
                print(f"{r['stage']:12} "+color(f"{e['port']:8}","yellow" if e["port"]=="DOWN" else "green")+
                      f" {e['a_b']:12} {e['b_c']:12} "+color("CONNECTED","green"))
            print("DETECCION AUTOMATICA DEL PUERTO: NO | EVIDENCIA DIRECTA")
        else:
            print(f"{'HIPOTESIS':27} {'CONTEXTO':26} INCERTIDUMBRE")
            actions=set()
            for r in rows:
                for h in r["hypotheses"]:
                    print(f"{h['rule']:27} {h['context']:26} "+color(h["uncertainty"],"yellow" if h["uncertainty"]!="SCOPED" else "green"))
                    actions.update(x["action_id"] for x in h["actions"])
            print("RUNBOOKS RECOMENDADOS (SOLO LECTURA):")
            for a in sorted(actions):
                print("  "+a)
        print(color("RESTAURACION VERIFICADA","green"))
        status="ESCENARIO VALIDADO"
    elif section=="EVALUACION":
        print(f"{'ESCENARIO':12} {'ETAPA':12} {'ESPERADAS':>10} {'OBSERVADAS':>12} {'CORRECTAS':>12}")
        for r in d["rows"]:
            print(f"{r['case']:12} {r['stage']:12} {r['expected']:10} {r['observed']:12} "+
                  color(f"{r['correct_recommendations']:12}","green"))
        rule()
        c=d["counts"]
        print(f"VENTANAS: {d['windows']} | OBSERVACIONES: {d['observations']}")
        print("HIPOTESIS COINCIDENTES: "+color(f"{c['matched']}/{c['expected']}","green"))
        print("RECOMENDACIONES CORRECTAS: "+color(f"{c['correct_recommendations']}/{c['expected']}","green"))
        print(f"INESPERADAS: {c['unexpected']} | FALTANTES: {c['missing']}")
        status="EVALUACION HISTORICA VALIDADA"
    elif section=="CONTROLES":
        print("ABSTENCION: VENTANA ALTERADA OFFLINE (NO ES ENSAYO REAL)")
        print("DECISION: "+color(d["abstention"]["decision"],"green"))
        print("HIPOTESIS: "+str(d["abstention"]["hypotheses"]))
        print("RECHAZO REAL: "+color(d["real_denial"],"yellow"))
        rule()
        print("DETECCION AUTOMATICA PUERTO SDN: NO")
        print("GENERALIZACION ESTADISTICA: NO")
        print("DISPONIBILIDAD CONTINUA MEDIDA: NO")
        status="CONTROLES Y LIMITES VERIFICADOS"
    else: raise ValueError("SECTION_INVALID")
    rule()
    print("PRESENTACION HISTORICA | SIN NUEVAS MUTACIONES")
    print("AUTORIZACION AUTOMATICA: NO")
    line()
    print(color(" S07-007G | "+status,"green"))
    line()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--services",type=Path);p.add_argument("--network",type=Path);p.add_argument("--compound",type=Path)
    p.add_argument("--watchdog",type=Path);p.add_argument("--human",type=Path);p.add_argument("--denial",type=Path)
    p.add_argument("--report",type=Path);p.add_argument("--show",choices=[*TARGETS,"EVALUACION","CONTROLES"])
    a=p.parse_args()
    if a.show:
        show(load(a.report),a.show);return
    if not all((a.services,a.network,a.compound,a.watchdog,a.human,a.denial)): p.error("rutas requeridas")
    print(json.dumps(review(a.services,a.network,a.compound,a.watchdog,a.human,a.denial),indent=2,ensure_ascii=False))
if __name__=="__main__": main()
