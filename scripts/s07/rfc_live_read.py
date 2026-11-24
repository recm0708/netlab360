#!/usr/bin/python3
"""Broker RFC vinculado a evidencia privilegiada real. Solo auditoría; restauración bloqueada."""
import argparse
import json
import os
import pwd
import socket
import sqlite3
import stat
import struct
import subprocess
from datetime import datetime, timezone
import sys
import time
from pathlib import Path
from uuid import uuid4

SCHEMA="NETLAB360_S07_RFC_LIVE_READ_V1"
ACTION="S07_AUDIT_OSPF_COST_V1"
ARGS={}
RESTORE="S07_RESTORE_OSPF_COST_V1"
RESTORE_ARGS={"site":"S1","interface":"s1b","cost":100}
TTL=120
MAX_EVIDENCE_AGE=10
STATE=Path("/var/lib/netlab360/s07-rfc-live")
SOCKET=Path("/run/netlab360-s07-rfc-live/broker.sock")
PREFLIGHT=Path("/usr/local/libexec/netlab360/s07-preflight.py")
PIN=Path("/var/lib/netlab360/s07-preflight/router-pin.json")
PROFILE={"HQ":{"s1p":10,"s1b":100,"s2p":10,"s2b":100},"S1":{"s1p":10,"s1b":100},"S2":{"s2p":10,"s2b":100}}
USER="rc-aa-ec"
MAX=16384


def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)


class Denied(ValueError):
    pass


def observe_state():
    """Lectura propia del broker; no admite evidencias suministradas por el cliente."""
    secure_path(PREFLIGHT,0o755,stat.S_ISREG)
    secure_path(PIN.parent,0o700,stat.S_ISDIR)
    secure_path(PIN,0o600,stat.S_ISREG)
    p=subprocess.run(["/usr/bin/python3","-I",str(PREFLIGHT),"check"],
                     capture_output=True,text=True,timeout=35,
                     env={"PATH":"/usr/sbin:/usr/bin:/sbin:/bin","LC_ALL":"C"})
    if p.returncode or len(p.stdout)>65536:
        raise Denied("PREFLIGHT_DENIED")
    d=json.loads(p.stdout)
    if (d.get("ok") is not True or d.get("schema")!="NETLAB360_S07_PROTECTED_PREFLIGHT_V1"
        or d.get("pin_status")!="VERIFIED" or d.get("identity_verified") is not True
        or d.get("network_mutations_authorized") is not False
        or d.get("execution_authorized") is not False
        or d.get("management")!={"address":"192.168.47.40/24","gateway":"192.168.47.2","device":"ens33"}):
        raise Denied("PREFLIGHT_DENIED")
    pin=json.loads(PIN.read_text())
    ids=pin["ids"]
    if pin.get("schema")!="NETLAB360_S07_ROUTER_PIN_V1" or pin.get("profile")!=PROFILE or set(ids)!=set(PROFILE):
        raise Denied("PIN_INVALID")
    wanted={(site,iface):cost for site,interfaces in PROFILE.items() for iface,cost in interfaces.items()}
    got={}
    for row in d["costs"]:
        k=(row["site"],row["interface"])
        n=row["observed"]
        if k in got or k not in wanted or row["desired"]!=wanted[k] or type(n) is not int or not 1<=n<=65535:
            raise Denied("COST_INVENTORY_INVALID")
        got[k]=n
    if set(got)!=set(wanted) or len(d["neighbors"])!=8 or len(d["routes"])!=6:
        raise Denied("PREFLIGHT_INCOMPLETE")
    if any(x["state"]!="Full" for x in d["neighbors"]) or any(x["selection"]!="PRIMARY" for x in d["routes"]):
        raise Denied("OPERATIONAL_STATE_DENIED")
    return {"observed_at_utc":d["ended_at_utc"],
            "state":{"ids":ids,"management":d["management"],
                     "boot_id":Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                     "costs":{site+"/"+iface:n for (site,iface),n in sorted(got.items())},
                     "neighbors":d["neighbors"],"routes":d["routes"]},
            "source":"ROOT_OWNED_PREFLIGHT","end_to_end_availability":"NOT_MEASURED"}


class Store:
    def __init__(self,path,requester_uid,clock=time.time,observer=observe_state):
        if type(requester_uid) is not int or requester_uid<=0:
            raise ValueError("INVALID_REQUESTER_UID")
        self.path=path
        self.uid=requester_uid
        self.clock=clock
        self.observer=observer
        with self.connect() as c:
            c.executescript("""
              CREATE TABLE IF NOT EXISTS requests(
                id TEXT PRIMARY KEY, body TEXT NOT NULL, status TEXT NOT NULL,
                approver INTEGER, approved_at INTEGER);
              CREATE TABLE IF NOT EXISTS audit(
                seq INTEGER PRIMARY KEY AUTOINCREMENT, at INTEGER NOT NULL,
                uid INTEGER NOT NULL, rfc_id TEXT, event TEXT NOT NULL, reason TEXT);
              CREATE TABLE IF NOT EXISTS evidence(seq INTEGER PRIMARY KEY AUTOINCREMENT, rfc_id TEXT NOT NULL, stage TEXT NOT NULL, body TEXT NOT NULL);
            """)

    def connect(self):
        c=sqlite3.connect(self.path,timeout=5,isolation_level=None)
        c.row_factory=sqlite3.Row
        c.execute("PRAGMA synchronous=FULL")
        return c

    def evidence(self,expected=None):
        try:
            e=self.observer()
            stamp=datetime.fromisoformat(e["observed_at_utc"])
            if stamp.tzinfo is None or not 0<=self.clock()-stamp.timestamp()<=MAX_EVIDENCE_AGE:
                raise Denied("EVIDENCE_NOT_FRESH")
            if e.get("source")!="ROOT_OWNED_PREFLIGHT" or type(e.get("state")) is not dict:
                raise Denied("EVIDENCE_INVALID")
            if expected is not None and canonical(e["state"])!=canonical(expected):
                raise Denied("EXPECTED_STATE_CHANGED")
            return e
        except Denied:
            raise
        except (ValueError,TypeError,KeyError,OSError,subprocess.TimeoutExpired):
            raise Denied("PREFLIGHT_UNAVAILABLE") from None

    def handle(self,uid,msg):
        c=self.connect()
        rid=None
        op="INVALID"
        try:
            c.execute("BEGIN IMMEDIATE")
            now=int(self.clock())
            try:
                if type(msg) is not dict or uid not in (self.uid,0):
                    raise Denied("PEER_DENIED")
                op=msg.get("op")
                if op=="request":
                    if uid!=self.uid:
                        raise Denied("ROLE_DENIED")
                    if set(msg)!={"op","action_id","arguments"}:
                        raise Denied("ACTION_OR_ARGUMENT_DENIED")
                    if msg["action_id"]==RESTORE and canonical(msg["arguments"])==canonical(RESTORE_ARGS):
                        e=self.evidence()
                        if e["state"]["costs"]["S1/s1b"]==100:
                            raise Denied("NO_VERIFIED_DRIFT")
                        raise Denied("MUTATION_GATE_CLOSED")
                    if msg["action_id"]!=ACTION or canonical(msg["arguments"])!=canonical(ARGS):
                        raise Denied("ACTION_OR_ARGUMENT_DENIED")
                    e=self.evidence()
                    now=int(self.clock())
                    rid=str(uuid4())
                    body={"rfc_id":rid,"mode":"LIVE_READ_ONLY",
                          "action_id":ACTION,"arguments":dict(ARGS),"resource":"OSPF_COST_PROFILE",
                          "expected_state":e["state"],"initial_observed_at_utc":e["observed_at_utc"],
                          "requester_uid":uid,"created_at":now,"expires_at":now+TTL}
                    c.execute("INSERT INTO requests VALUES(?,?,?,NULL,NULL)",(rid,canonical(body),"PENDING"))
                    c.execute("INSERT INTO evidence(rfc_id,stage,body) VALUES(?,?,?)",(rid,"REQUEST",canonical(e)))
                    result={"request":body,"status":"PENDING"}
                elif op in ("show","approve","cancel","consume"):
                    expected={"op","rfc_id"} if op=="show" else {"op","rfc_id","body"}
                    if op=="approve":
                        expected.add("confirmation")
                    if set(msg)!=expected or type(msg["rfc_id"]) is not str or len(msg["rfc_id"])!=36:
                        raise Denied("MESSAGE_INVALID")
                    rid=msg["rfc_id"]
                    row=c.execute("SELECT * FROM requests WHERE id=?",(rid,)).fetchone()
                    if row is None:
                        raise Denied("RFC_UNKNOWN")
                    body=json.loads(row["body"])
                    if op=="show":
                        result={"request":body,"status":row["status"],"approver_uid":row["approver"]}
                    else:
                        if canonical(msg["body"])!=row["body"]:
                            raise Denied("RFC_BINDING_MISMATCH")
                        if op=="approve":
                            if uid!=0 or uid==body["requester_uid"]:
                                raise Denied("ROLE_DENIED")
                            if msg["confirmation"]!="APROBAR AUDITORIA "+rid:
                                raise Denied("CONFIRMATION_REQUIRED")
                            if row["status"]!="PENDING":
                                raise Denied("RFC_STATE_DENIED")
                            if not body["created_at"]<=now<body["expires_at"]:
                                raise Denied("RFC_EXPIRED_OR_FUTURE")
                            e=self.evidence(body["expected_state"])
                            now=int(self.clock())
                            if not body["created_at"]<=now<body["expires_at"]:
                                raise Denied("RFC_EXPIRED_OR_FUTURE")
                            c.execute("INSERT INTO evidence(rfc_id,stage,body) VALUES(?,?,?)",(rid,"APPROVE",canonical(e)))
                            c.execute("UPDATE requests SET status='APPROVED_READ_ONLY',approver=?,approved_at=? WHERE id=?",(uid,now,rid))
                            result={"status":"APPROVED_READ_ONLY","evidence_observed_at_utc":e["observed_at_utc"]}
                        elif op=="cancel":
                            if row["status"] not in ("PENDING","APPROVED_READ_ONLY"):
                                raise Denied("RFC_STATE_DENIED")
                            c.execute("UPDATE requests SET status='CANCELLED' WHERE id=?",(rid,))
                            result={"status":"CANCELLED"}
                        else:
                            if uid!=body["requester_uid"]:
                                raise Denied("ROLE_DENIED")
                            if row["status"]!="APPROVED_READ_ONLY" or row["approver"]!=0:
                                raise Denied("RFC_STATE_DENIED")
                            if not body["created_at"]<=row["approved_at"]<=now<body["expires_at"]:
                                raise Denied("RFC_EXPIRED_OR_FUTURE")
                            e=self.evidence(body["expected_state"])
                            now=int(self.clock())
                            if not body["created_at"]<=row["approved_at"]<=now<body["expires_at"]:
                                raise Denied("RFC_EXPIRED_OR_FUTURE")
                            c.execute("INSERT INTO evidence(rfc_id,stage,body) VALUES(?,?,?)",(rid,"CONSUME",canonical(e)))
                            c.execute("UPDATE requests SET status='CONSUMED_READ_ONLY' WHERE id=?",(rid,))
                            result={"status":"CONSUMED_READ_ONLY","result":"LIVE_AUDIT_VERIFIED",
                                    "evidence_observed_at_utc":e["observed_at_utc"]}
                else:
                    raise Denied("OPERATION_DENIED")
                c.execute("INSERT INTO audit(at,uid,rfc_id,event,reason) VALUES(?,?,?,?,NULL)",(now,uid,rid,str(op).upper()))
                response={"ok":True,**result}
            except (Denied,TypeError,ValueError) as e:
                reason=str(e) if isinstance(e,Denied) else "MESSAGE_INVALID"
                c.execute("INSERT INTO audit(at,uid,rfc_id,event,reason) VALUES(?,?,?,?,?)",(now,uid,rid,"DENIED",reason))
                response={"ok":False,"reason":reason}
            c.commit()
            return {"schema":SCHEMA,**response,"network_mutations_authorized":False,"execution_authorized":False}
        except BaseException:
            c.rollback()
            raise
        finally:
            c.close()


def read_message(conn):
    with conn.makefile("rb") as f:
        raw=f.readline(MAX+1)
    if len(raw)>MAX or not raw.endswith(b"\n"):
        raise ValueError("MESSAGE_SIZE")
    return json.loads(raw)


def send_message(conn,msg):
    conn.sendall((canonical(msg)+"\n").encode())


def call(msg):
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
        s.settimeout(45)
        s.connect(str(SOCKET))
        send_message(s,msg)
        return read_message(s)


def secure_path(p,mode,kind):
    s=p.lstat()
    if s.st_uid!=0 or stat.S_IMODE(s.st_mode)!=mode or not kind(s.st_mode):
        raise RuntimeError("UNSAFE_PATH "+str(p))


def serve():
    if os.geteuid()!=0:
        raise RuntimeError("ROOT_REQUIRED")
    user=pwd.getpwnam(USER)
    os.umask(0o077)
    secure_path(STATE,0o700,stat.S_ISDIR)
    secure_path(SOCKET.parent,0o755,stat.S_ISDIR)
    db=STATE/"rfc.sqlite3"
    if db.exists() or db.is_symlink():
        secure_path(db,0o600,stat.S_ISREG)
    store=Store(db,user.pw_uid)
    secure_path(db,0o600,stat.S_ISREG)
    if SOCKET.exists() or SOCKET.is_symlink():
        secure_path(SOCKET,0o660,stat.S_ISSOCK)
        SOCKET.unlink()
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
        server.bind(str(SOCKET))
        os.chown(SOCKET,0,user.pw_gid)
        os.chmod(SOCKET,0o660)
        server.listen(8)
        while True:
            conn,_=server.accept()
            with conn:
                conn.settimeout(45)
                _,uid,_=struct.unpack("3i",conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize("3i")))
                try:
                    msg=read_message(conn)
                    result=store.handle(uid,msg)
                    send_message(conn,result)
                except (OSError,ValueError):
                    continue


def main():
    p=argparse.ArgumentParser()
    p.add_argument("op",choices=["serve","request","show","approve","cancel","consume"])
    p.add_argument("rfc_id",nargs="?")
    p.add_argument("--restore",action="store_true")
    a=p.parse_args()
    if a.restore and a.op!="request": p.error("--restore only for request")
    if a.op=="serve":
        if a.rfc_id: p.error("unexpected id")
        serve()
        return
    if a.op=="request":
        if a.rfc_id: p.error("unexpected id")
        result=call({"op":"request","action_id":RESTORE if a.restore else ACTION,"arguments":dict(RESTORE_ARGS if a.restore else ARGS)})
    else:
        if not a.rfc_id: p.error("rfc_id required")
        msg={"op":"show","rfc_id":a.rfc_id}
        result=call(msg)
        if result["ok"] and a.op!="show":
            msg.update(op=a.op,body=result["request"])
            if a.op=="approve":
                if os.geteuid()!=0 or not sys.stdin.isatty():
                    p.error("root interactive terminal required")
                print(json.dumps(result,indent=2),file=sys.stderr)
                print("Escriba APROBAR AUDITORIA "+a.rfc_id+": ",file=sys.stderr,end="",flush=True)
                msg["confirmation"]=input()
            result=call(msg)
    print(json.dumps(result,indent=2))
    sys.exit(0 if result["ok"] else 3)


if __name__=="__main__":
    main()
