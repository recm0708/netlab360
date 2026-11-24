#!/usr/bin/env python3
"""Presentación histórica de aceptación protegida; no conecta a la API ni modifica red."""
import argparse
import json
from pathlib import Path

C="\033[1;36m";G="\033[1;32m";Y="\033[1;33m";R="\033[0m"
def color(x,c=G): return c+str(x)+R
def read(p,n): return json.loads((p/(n+".json")).read_text())
def line(): print(color("="*96,C))
def rule(): print("-"*96)
def check(ok): 
    if not ok: raise ValueError("EVIDENCE_MISMATCH")
def http(p,n,code,reason=None):
    d=read(p,n)
    check(d["http_status"]==code)
    r=d["response"]
    if reason: check(not r["ok"] and r["reason"]==reason)
    else: check(r["ok"])
    return r
def title(t):
    line();print(" NETLAB360 | S07 - "+t);line()
    print("Modalidad: PRESENTACION HISTORICA | SOLO LECTURA")
    print("Zona horaria del laboratorio: America/Panama");rule()
def end(t):
    rule();print("REGISTROS EXPERIMENTALES | SIN NUEVAS MUTACIONES")
    line();print(color(" "+t));line()
# La presentación comprueba los registros existentes; no vuelve a solicitar una autorización.
def broker(p,section):
    d=read(p,"estado-broker-final");j=read(p,"journal-protegido")["transaction"]
    check(d["status"]==j["status"]=="VERIFIED" and j["baseline"]==j["final_observation"])
    if section=="BROKER":
        title("BROKER RFC OPERACIONAL - POLITICAS")
        for name,reason in (("accion_arbitraria","ACTION_OR_ARGUMENT_DENIED"),("autoaprobacion","ROLE_DENIED"),
                            ("argumentos_alterados","RFC_BINDING_MISMATCH"),("solicitud_cancelada","RFC_STATE_DENIED"),
                            ("replay-experiment","RFC_STATE_DENIED"),("replay-restore","RFC_STATE_DENIED")):
            x=read(p,name);check(not x["ok"] and x["reason"]==reason)
            print(f"{name.upper():26} "+color(reason,Y))
        x=read(p,"cancelacion");check(x["ok"] and x["status"]=="CANCELLED")
        print("CANCELACION: "+color(x["status"]))
        rule()
        for stage,a in d["approvals"].items():
            check(a["status"]=="CONSUMED" and a["approver_uid"]==0)
            print(f"{stage:12} SOLICITANTE UID={a['binding']['requester_uid']} | APROBADOR UID={a['approver_uid']}")
        print("SEPARACION DE PRIVILEGIOS | NO DE PERSONAS")
        end("S07-004H-J | POLITICAS VALIDADAS")
    else:
        title("BROKER RFC - CICLO OSPF PROTEGIDO")
        print("RFC: "+d["rfc_id"]);rule()
        for e in j["events"]: print(color(e["state"],Y if e["state"]=="DRIFT_APPLIED" else G))
        rule();print("CICLO COSTOS: 100 -> 150 -> 100")
        for stage,a in d["approvals"].items():
            print(f"{stage:12} "+a["binding"]["approval_id"]+" | "+color(a["status"]))
        print("RESTAURACION: "+color(j["events"][-1]["source"]))
        end("S07-004H-J | CICLO VERIFICADO")

# La auditoría de la captura exige el ciclo verificado y la coincidencia del estado basal y final.
def api(p,section):
    s=read(p,"summary");j=read(p,"journal-protegido")["transaction"]
    check(s["status"]==j["status"]=="VERIFIED" and s["cycle"]==[100,150,100] and j["baseline"]==j["final_observation"])
    if section=="API":
        title("API VERSIONADA Y CONTROL DE ACCESO")
        for n in ("health","incidents","hypotheses","runbooks","audit"):
            http(p,n,200);print(f"GET {n.upper():20} "+color("HTTP 200"))
        rule()
        for n,c,r in (("ruta_arbitraria",404,"ROUTE_DENIED"),("schema_invalido",400,"BODY_INVALID"),
                      ("accion_arbitraria",409,"ACTION_OR_ARGUMENT_DENIED"),("sin_idempotencia",400,"IDEMPOTENCY_KEY_REQUIRED"),
                      ("autoaprobacion",403,"ROLE_DENIED")):
            http(p,n,c,r);print(f"{n.upper():22} HTTP {c} | "+color(r,Y))
        print("TRANSPORTE: HTTP UNIX | UID AJENO DENEGADO EN ACEPTACION")
        end("S07-008A-C | API CONTROLADA VALIDADA")
    elif section=="IDEMPOTENCIA":
        title("API - IDEMPOTENCIA Y CANCELACION")
        a=http(p,"solicitud_cancelable",200)["result"]
        for n in ("replay_solicitud","replay_tras_cancelacion"):
            check(http(p,n,200)["result"]==a)
            print(f"{n.upper():28} "+color("MISMA RESPUESTA"))
        http(p,"conflicto_idempotencia",409,"IDEMPOTENCY_CONFLICT")
        print("CONFLICTO DE CUERPO: "+color("HTTP 409",Y))
        for n in ("cancelacion","estado_cancelado"):
            check(http(p,n,200)["result"]["status"]=="CANCELLED")
        rule();print("RFC: "+a["rfc_id"])
        print("ESTADO CONSULTADO: "+color("CANCELLED"))
        print("REPLAY HISTORICO NO EQUIVALE A ESTADO ACTUAL")
        end("S07-008A-C | IDEMPOTENCIA VALIDADA")
    elif section=="INTENCION":
        title("API - DETECCION, INTENCION Y RECOMENDACION")
        for n in ("inicial","drift","final"):
            a=http(p,"intencion_"+n,200)["result"]
            check(a["network_mutations_authorized"] is False)
            rule()
            print(n.upper()+" | COMPLIANCE="+color(a["configuration_compliance"],Y if n=="drift" else G))
            print("DESVIACIONES="+str(len(a["deviations"])))
            for x in a["deviations"]: print(f"  {x['resource']} DESEADO={x['desired']} OBSERVADO={x['observed']}")
            print("DECISION="+a["recommendation"]["decision"])
            print(f"OSPF FULL={a['ospf_full']}/8 | FIB PRINCIPAL={a['fib_primary']}/6 | ICMP={a['icmp_samples']}/6 | HTTP={a['http']}")
        print("AUTORIZACION AUTOMATICA: NO | DISPONIBILIDAD CONTINUA: NO MEDIDA")
        end("S07-008A-C | INTENCION VERIFICADA")
    elif section=="CICLO":
        title("API - CICLO SUPERVISADO Y AUDITORIA")
        print("RFC: "+s["rfc_id"]);rule()
        a=http(p,"ejecucion_final",200)["result"]
        for e in j["events"]:print(color(e["state"],Y if e["state"]=="DRIFT_APPLIED" else G))
        rule()
        rows=[e for e in http(p,"auditoria_final",200)["result"] if e["rfc_id"]==s["rfc_id"] and e["event"]=="APPROVAL_CONSUMED"]
        check(len(rows)==2 and all(e["uid"]==0 for e in rows))
        for stage,slot in a["approvals"].items():
            check(slot["status"]=="CONSUMED")
            print(f"{stage:12} "+slot["binding"]["approval_id"]+" | "+color(slot["status"]))
        print("CICLO: 100 -> 150 -> 100 | APROBACIONES AUDITADAS: "+color("2/2"))
        print("ESTADO FINAL: "+color(j["status"]))
        end("S07-008A-C | CICLO INTEGRADO VERIFICADO")
    else: raise ValueError("SECTION_DENIED")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    p.add_argument("section",choices=("BROKER","BROKER_CICLO","API","IDEMPOTENCIA","INTENCION","CICLO"))
    a=p.parse_args()
    (broker if a.section.startswith("BROKER") else api)(a.directory,a.section)
