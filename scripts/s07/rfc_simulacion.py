"""Simulador RFC: roles de prueba, registro auditable y consumo único.
No es autenticación, persistencia protegida ni autorización operacional.
"""
from copy import deepcopy
from uuid import uuid4
from datetime import timedelta
from contrato_eventos import utc
from catalogo_runbooks import validate_action

SCHEMA="NETLAB360_S07_RFC_SIMULATION_V1"
ROLES={"TEST_REQUESTER":"REQUESTER","TEST_APPROVER":"APPROVER"}
ACTION="S07_RESTORE_OSPF_COST_V1"
TTL=60
MAX_EVIDENCE_AGE=30


# Los roles y registros de este ledger son datos simulados, no identidades autenticadas.
class Ledger:
    def __init__(self):
        self._records={}
        self._audit=[]

    def _log(self,rid,actor,event,now):
        self._audit.append({"rfc_id":rid,"actor":actor,"event":event,"at_utc":utc(now).isoformat()})

    def snapshot(self):
        return deepcopy({"schema":SCHEMA,"mode":"SIMULATION_ONLY","records":list(self._records.values()),
                         "audit":self._audit,"operational_authorization":False})

    def _role(self,actor,role):
        if ROLES.get(actor)!=role:
            raise ValueError("ROLE_DENIED")

    def _fresh(self,stamp,now):
        age=(utc(now)-utc(stamp)).total_seconds()
        if not 0<=age<=MAX_EVIDENCE_AGE:
            raise ValueError("EVIDENCE_NOT_FRESH")

    def _policy(self,args,intent,now):
        validate_action(ACTION,args)
        if (intent.get("schema")!="NETLAB360_S07_INTENT_V1"
            or intent.get("network_mutations_authorized") is not False
            or intent.get("temporally_aligned") is not True
            or intent.get("configuration_compliance")!="NOT_MET"
            or intent.get("preferred_route_intent")!="MET"
            or intent.get("ospf_adjacency_intent")!="MET"
            or intent.get("http_observed_availability")!="MET"):
            raise ValueError("POLICY_DENIED")
        self._fresh(intent["window_ended_at_utc"],now)
        self._fresh(intent["audit_ended_at_utc"],now)
        matches=[r for r in intent["cost_rows"] if (r["site"],r["interface"])==(args["site"],args["interface"])]
        if len(matches)!=1:
            raise ValueError("TARGET_NOT_UNIQUE")
        r=matches[0]
        observed=r["observed"]
        if (r["status"]!="NON_COMPLIANT" or r["expected"]!=args["cost"]
            or type(observed) is not int or not 1<=observed<=65535 or observed==args["cost"]):
            raise ValueError("TARGET_NOT_VERIFIED_DRIFT")
        self._fresh(r["observed_at_utc"],now)
        return {"observed_cost":observed,"desired_cost":args["cost"]}

    def request(self,actor,action,args,intent,now):
        self._role(actor,"REQUESTER")
        if action!=ACTION:
            raise ValueError("ACTION_DENIED")
        state=self._policy(args,intent,now)
        rid=str(uuid4())
        body={"rfc_id":rid,"action_id":action,"arguments":deepcopy(args),
              "resource":args["site"]+"/"+args["interface"],"expected_state":state,
              "evidence_window":intent["window_ended_at_utc"],"evidence_audit":intent["audit_ended_at_utc"],
              "requester":actor,"created_at_utc":utc(now).isoformat(),
              "expires_at_utc":(utc(now)+timedelta(seconds=TTL)).isoformat()}
        self._records[rid]={"request":deepcopy(body),"status":"PENDING","approver":None,"approval":None}
        self._log(rid,actor,"REQUESTED",now)
        return deepcopy(body)

    # Se verifica el cuerpo original y el estado esperado antes de aprobar o consumir una solicitud.
    def _check(self,body,now,status):
        record=self._records.get(body.get("rfc_id"))
        if record is None or body!=record["request"]:
            raise ValueError("RFC_ALTERED_OR_UNKNOWN")
        if record["status"]!=status:
            raise ValueError("RFC_STATE_DENIED")
        if not utc(body["created_at_utc"])<=utc(now)<utc(body["expires_at_utc"]):
            raise ValueError("RFC_EXPIRED_OR_FUTURE")
        return record

    def approve(self,actor,body,now):
        self._role(actor,"APPROVER")
        r=self._check(body,now,"PENDING")
        if actor==body["requester"]:
            raise ValueError("SELF_APPROVAL")
        self._fresh(body["evidence_window"],now)
        self._fresh(body["evidence_audit"],now)
        r["status"]="APPROVED_SIMULATION"
        r["approver"]=actor
        r["approval"]={"request":deepcopy(body),"approved_at_utc":utc(now).isoformat(),"approver":actor}
        self._log(body["rfc_id"],actor,"APPROVED_SIMULATION",now)

    def cancel(self,actor,body,now):
        if actor not in ROLES:
            raise ValueError("ROLE_DENIED")
        r=self._records.get(body.get("rfc_id"))
        if r is None or body!=r["request"] or r["status"] not in ("PENDING","APPROVED_SIMULATION"):
            raise ValueError("CANCEL_DENIED")
        r["status"]="CANCELLED"
        self._log(body["rfc_id"],actor,"CANCELLED",now)

    def consume_preview(self,actor,body,current_intent,now):
        self._role(actor,"REQUESTER")
        r=self._check(body,now,"APPROVED_SIMULATION")
        if actor!=body["requester"] or r["approval"]["request"]!=body:
            raise ValueError("APPROVAL_BINDING_INVALID")
        if utc(now)<utc(r["approval"]["approved_at_utc"]):
            raise ValueError("APPROVAL_TIME_INVALID")
        self._fresh(body["evidence_window"],now)
        self._fresh(body["evidence_audit"],now)
        if self._policy(body["arguments"],current_intent,now)!=body["expected_state"]:
            raise ValueError("EXPECTED_STATE_CHANGED")
        r["status"]="CONSUMED_SIMULATION"
        self._log(body["rfc_id"],actor,"CONSUMED_SIMULATION",now)
        return {"status":"SIMULATED_NOOP","rfc_id":body["rfc_id"],
                "execution_authorized":False,"network_mutations_authorized":False}
