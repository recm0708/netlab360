#!/usr/bin/python3
"""Broker local de aprobación operacional OSPF. Root del host es de confianza."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import pwd
import socket
import stat
import struct
import subprocess
import sys
import time
from uuid import uuid4

STATE=Path("/var/lib/netlab360/s07-ospf-broker")
SOCKET=Path("/run/netlab360-s07-ospf-broker/broker.sock")
EXEC=Path("/usr/local/libexec/netlab360/s07-ospf-broker.py")
TRIAL=Path("/usr/local/libexec/netlab360/s07-ospf-trial.py")
SCHEMA="NETLAB360_S07_OSPF_BROKER_V1"
MAX=32768
ACTIONS={"EXPERIMENT":("S07_EXPERIMENT_OSPF_COST_V1",{"site":"S1","interface":"s1b","initial_cost":100,"experimental_cost":150,"restore_cost":100}),
         "RESTORE":("S07_RESTORE_OSPF_COST_V1",{"site":"S1","interface":"s1b","cost":100})}


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)


def demand(ok,reason):
    if not ok: raise ValueError(reason)


class Broker:
    """Invocaciones serializadas por el servicio y el lock del preflight."""
    def __init__(self,trial_module,root,backend,desired,uid,audit,clock=time.monotonic,protected=True):
        demand(type(uid) is int and uid>0,"REQUESTER_INVALID")
        self.m=trial_module; self.root=root; self.b=backend; self.desired=desired
        self.uid=uid; self.audit=audit; self.clock=clock; self.protected=protected

    def trial(self,rid):
        return self.m.Trial(self.root,rid,self.b,self.clock,protected=self.protected)

    def binding(self,t,d,stage):
        action,args=ACTIONS[stage]
        deadline=d["request_deadline"] if stage=="EXPERIMENT" else d["watchdog_deadline"]-self.m.MARGIN
        expected=d["baseline"] if stage=="EXPERIMENT" else d["drift_observation"]
        now=self.clock()
        demand(now<deadline,"RFC_EXPIRED")
        return {"rfc_id":t.rid,"approval_id":uuid4().hex,"stage":stage,"action_id":action,
                "arguments":dict(args),"resource":"S1/s1b","expected_state":expected,
                "requester_uid":self.uid,"created_monotonic":now,"expires_monotonic":deadline,
                "boot_id":expected["boot_id"]}

    def view(self,d):
        return {"rfc_id":d["rfc_id"],"status":d["status"],"approvals":d["broker_rfc"],
                "observed_cost":d.get("drift_observation",d["baseline"])["costs"]["S1/s1b"]
                  if d["status"]!="VERIFIED" else d["final_observation"]["costs"]["S1/s1b"],
                "watchdog_armed":self.b.timer_active(d["rfc_id"])}

    def handle(self,uid,msg):
        rid=None; op="INVALID"; approval_id=None
        try:
            demand(uid in (self.uid,0),"PEER_DENIED")
            demand(type(msg) is dict,"MESSAGE_INVALID")
            op=msg.get("op")
            demand(type(op) is str,"OPERATION_DENIED")
            if op=="request":
                demand(uid==self.uid,"ROLE_DENIED")
                demand(set(msg)=={"op","action_id","arguments"},"ACTION_OR_ARGUMENT_DENIED")
                action,args=ACTIONS["EXPERIMENT"]
                demand(msg["action_id"]==action and canonical(msg["arguments"])==canonical(args),"ACTION_OR_ARGUMENT_DENIED")
                for path in self.root.glob("*/transaction.json"):
                    prev=self.trial(path.parent.name); row=prev.load()
                    if row["status"]=="PENDING" and (self.clock()>=row["request_deadline"] or row["baseline"]["boot_id"]!=self.m.boot_id()):
                        prev.event(row,"EXPIRED")
                    else:
                        demand(row["status"] in self.m.TERMINAL,"UNRESOLVED_TRANSACTION")
                t=self.trial(uuid4().hex); rid=t.rid
                d=t.request(uid,self.desired)
                d["broker_rfc"]={"EXPERIMENT":{"binding":self.binding(t,d,"EXPERIMENT"),"status":"PENDING","approver_uid":None}}
                self.m.save(t.path,d)
            else:
                demand(op in ("show","request_restore","approve","cancel"),"OPERATION_DENIED")
                keys={"op","rfc_id"}
                if op in ("approve","cancel"): keys.add("binding")
                if op=="approve": keys.add("confirmation")
                demand(set(msg)==keys,"MESSAGE_INVALID")
                t=self.trial(msg["rfc_id"]); rid=t.rid
                d=t.load()
                demand("broker_rfc" in d and d["requester_uid"]==self.uid,"BROKER_RFC_REQUIRED")
                if op=="request_restore":
                    demand(uid==self.uid,"ROLE_DENIED")
                    demand(d["status"]=="DRIFT_VERIFIED" and "RESTORE" not in d["broker_rfc"],"RFC_STATE_DENIED")
                    demand(self.b.timer_active(rid),"WATCHDOG_NOT_READY")
                    demand(self.b.snapshot()==d["drift_observation"],"EXPECTED_STATE_CHANGED")
                    d["broker_rfc"]["RESTORE"]={"binding":self.binding(t,d,"RESTORE"),"status":"PENDING","approver_uid":None}
                    self.m.save(t.path,d)
                elif op in ("approve","cancel"):
                    demand(type(msg["binding"]) is dict,"RFC_BINDING_MISMATCH")
                    stage=msg["binding"].get("stage")
                    demand(stage in d["broker_rfc"],"RFC_BINDING_MISMATCH")
                    slot=d["broker_rfc"][stage]; body=slot["binding"]; approval_id=body["approval_id"]
                    demand(canonical(msg["binding"])==canonical(body),"RFC_BINDING_MISMATCH")
                    expected_status="PENDING" if stage=="EXPERIMENT" else "DRIFT_VERIFIED"
                    demand(d["status"]==expected_status and slot["status"]=="PENDING","RFC_STATE_DENIED")
                    if op=="cancel":
                        demand(uid==self.uid,"ROLE_DENIED")
                        slot["status"]="CANCELLED"
                        slot["cancelled_at_utc"]=self.m.utc()
                        if stage=="EXPERIMENT": t.event(d,"CANCELLED",reason="REQUESTER_CANCELLED")
                        else: self.m.save(t.path,d) # El watchdog sigue autorizado.
                    else:
                        demand(uid==0 and uid!=body["requester_uid"],"ROLE_DENIED")
                        demand(msg["confirmation"]=="APROBAR RFC "+approval_id,"CONFIRMATION_REQUIRED")
                        demand(body["created_monotonic"]<=self.clock()<body["expires_monotonic"],"RFC_EXPIRED")
                        # Snapshot obtenido por el backend protegido, nunca aportado por cliente.
                        demand(self.b.snapshot()==body["expected_state"],"EXPECTED_STATE_CHANGED")
                        demand(self.clock()<body["expires_monotonic"],"RFC_EXPIRED")
                        if stage=="RESTORE": demand(self.b.timer_active(rid),"WATCHDOG_NOT_READY")
                        self.audit(uid,rid,"APPROVAL_CONSUMED",None,approval_id)
                        slot.update(status="CONSUMED",approver_uid=uid,approved_at_utc=self.m.utc())
                        self.m.save(t.path,d)
                        # Trial vuelve a comprobar el estado, plazo, identidad y watchdog.
                        d=t.start("APROBAR ENSAYO "+rid) if stage=="EXPERIMENT" else t.restore("APROBAR RESTAURACION "+rid)
            result=self.view(d)
            self.audit(uid,rid,op.upper(),None,approval_id)
            return {"schema":SCHEMA,"ok":True,**result,"automatic_remediation":False}
        except (ValueError,KeyError,TypeError,OSError,subprocess.TimeoutExpired) as e:
            reason=str(e) if isinstance(e,ValueError) else type(e).__name__
            self.audit(uid,rid,"DENIED",reason,approval_id)
            return {"schema":SCHEMA,"ok":False,"reason":reason,"automatic_remediation":False}


def load_trial():
    s=TRIAL.lstat()
    demand(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o755,"TRIAL_PATH_UNSAFE")
    spec=importlib.util.spec_from_file_location("protected_ospf_trial",TRIAL)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def record(uid,rid,event,reason,approval_id):
    path=STATE/"audit.jsonl"
    row={"at_utc":__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
         "uid":uid,"rfc_id":rid,"event":event,"reason":reason,"approval_id":approval_id}
    fd=os.open(path,os.O_WRONLY|os.O_APPEND|os.O_CREAT|os.O_NOFOLLOW,0o600)
    try:
        s=os.fstat(fd)
        demand(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600,"AUDIT_PATH_UNSAFE")
        raw=(canonical(row)+"\n").encode()
        demand(os.write(fd,raw)==len(raw),"AUDIT_WRITE_FAILED")
        os.fsync(fd)
    finally: os.close(fd)


def read_message(conn):
    with conn.makefile("rb") as f: raw=f.readline(MAX+1)
    demand(len(raw)<=MAX and raw.endswith(b"\n"),"MESSAGE_SIZE")
    return json.loads(raw)


def send(conn,msg):
    raw=(canonical(msg)+"\n").encode()
    demand(len(raw)<=MAX,"MESSAGE_SIZE")
    conn.sendall(raw)


def call(msg):
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
        conn.settimeout(75); conn.connect(str(SOCKET)); send(conn,msg)
        return read_message(conn)


def serve():
    demand(os.geteuid()==0,"ROOT_REQUIRED")
    os.umask(0o077)
    m=load_trial()
    m.secure(EXEC,0o755,stat.S_ISREG); m.secure(STATE,0o700,stat.S_ISDIR)
    m.secure(m.STATE,0o700,stat.S_ISDIR); m.secure(SOCKET.parent,0o755,stat.S_ISDIR)
    pf=m.load_preflight(); user=pwd.getpwnam(m.USER)
    desired={s+"/"+i:v for s,interfaces in pf.profile().items() for i,v in interfaces.items()}
    b=Broker(m,m.STATE,m.RealBackend(pf),desired,user.pw_uid,record)
    # No sustituir un socket de otro servidor activo.
    demand(not SOCKET.exists() and not SOCKET.is_symlink(),"SOCKET_ALREADY_EXISTS")
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
        server.bind(str(SOCKET)); os.chown(SOCKET,0,user.pw_gid); os.chmod(SOCKET,0o660)
        server.listen(8)
        while True:
            conn,_=server.accept()
            with conn:
                conn.settimeout(5)
                _,uid,_=struct.unpack("3i",conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize("3i")))
                try:
                    msg=read_message(conn)
                    with pf.exclusive(m.PREFSTATE/"preflight.lock"):
                        result=b.handle(uid,msg)
                    send(conn,result)
                except (ValueError,RuntimeError,OSError) as e:
                    record(uid,None,"DENIED",str(e),None)
                    try: send(conn,{"schema":SCHEMA,"ok":False,"reason":"BROKER_REQUEST_FAILED"})
                    except (OSError,ValueError): pass


def main():
    p=argparse.ArgumentParser()
    p.add_argument("op",choices=("serve","request","show","request_restore","approve","cancel"))
    p.add_argument("rfc_id",nargs="?")
    p.add_argument("--stage",choices=tuple(ACTIONS),default="EXPERIMENT")
    a=p.parse_args()
    if a.op=="serve":
        if a.rfc_id: p.error("unexpected id")
        serve(); return
    if a.op=="request":
        if a.rfc_id: p.error("unexpected id")
        action,args=ACTIONS["EXPERIMENT"]
        result=call({"op":"request","action_id":action,"arguments":dict(args)})
    else:
        if not a.rfc_id: p.error("rfc_id required")
        msg={"op":a.op,"rfc_id":a.rfc_id}
        if a.op in ("approve","cancel"):
            current=call({"op":"show","rfc_id":a.rfc_id})
            if not current["ok"]:
                print(json.dumps(current,indent=2));sys.exit(3)
            msg["binding"]=current["approvals"][a.stage]["binding"]
            if a.op=="approve":
                if os.geteuid()!=0 or not sys.stdin.isatty(): p.error("root TTY required")
                print(json.dumps(msg["binding"],indent=2),file=sys.stderr)
                print("APROBAR RFC "+msg["binding"]["approval_id"]+": ",end="",file=sys.stderr,flush=True)
                msg["confirmation"]=input()
        result=call(msg)
    print(json.dumps(result,indent=2))
    sys.exit(0 if result["ok"] else 3)


if __name__=="__main__": main()
