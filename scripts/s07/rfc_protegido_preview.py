#!/usr/bin/python3
"""Broker local RFC de demostración protegida. No tiene ejecutor de red."""
import argparse
import json
import os
import pwd
import socket
import sqlite3
import stat
import struct
import sys
import time
from pathlib import Path
from uuid import uuid4

SCHEMA="NETLAB360_S07_RFC_PROTECTED_PREVIEW_V1"
ACTION="S07_RESTORE_OSPF_COST_V1"
ARGS={"site":"S1","interface":"s1b","cost":100}
TTL=300
STATE=Path("/var/lib/netlab360/s07-rfc-preview")
SOCKET=Path("/run/netlab360-s07-rfc-preview/broker.sock")
USER="rc-aa-ec"
MAX=8192


def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)


class Denied(ValueError):
    pass


# El almacén protege el registro de solicitudes de demostración; las acciones no tienen un ejecutor de red.
class Store:
    def __init__(self,path,requester_uid,clock=time.time):
        if type(requester_uid) is not int or requester_uid<=0:
            raise ValueError("INVALID_REQUESTER_UID")
        self.path=path
        self.uid=requester_uid
        self.clock=clock
        with self.connect() as c:
            c.executescript("""
              CREATE TABLE IF NOT EXISTS requests(
                id TEXT PRIMARY KEY, body TEXT NOT NULL, status TEXT NOT NULL,
                approver INTEGER, approved_at INTEGER);
              CREATE TABLE IF NOT EXISTS audit(
                seq INTEGER PRIMARY KEY AUTOINCREMENT, at INTEGER NOT NULL,
                uid INTEGER NOT NULL, rfc_id TEXT, event TEXT NOT NULL, reason TEXT);
            """)

    def connect(self):
        c=sqlite3.connect(self.path,timeout=5,isolation_level=None)
        c.row_factory=sqlite3.Row
        c.execute("PRAGMA synchronous=FULL")
        return c

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
                    if set(msg)!={"op","action_id","arguments"} or msg["action_id"]!=ACTION or canonical(msg["arguments"])!=canonical(ARGS):
                        raise Denied("ACTION_OR_ARGUMENT_DENIED")
                    rid=str(uuid4())
                    body={"rfc_id":rid,"mode":"SYNTHETIC_PREVIEW_ONLY",
                          "action_id":ACTION,"arguments":dict(ARGS),"resource":"S1/s1b",
                          "expected_state":{"observed_cost":150,"desired_cost":100},
                          "requester_uid":uid,"created_at":now,"expires_at":now+TTL}
                    c.execute("INSERT INTO requests VALUES(?,?,?,NULL,NULL)",(rid,canonical(body),"PENDING"))
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
                            if msg["confirmation"]!="APROBAR PREVIEW "+rid:
                                raise Denied("CONFIRMATION_REQUIRED")
                            if row["status"]!="PENDING":
                                raise Denied("RFC_STATE_DENIED")
                            if not body["created_at"]<=now<body["expires_at"]:
                                raise Denied("RFC_EXPIRED_OR_FUTURE")
                            c.execute("UPDATE requests SET status='APPROVED_PREVIEW',approver=?,approved_at=? WHERE id=?",(uid,now,rid))
                            result={"status":"APPROVED_PREVIEW"}
                        elif op=="cancel":
                            if row["status"] not in ("PENDING","APPROVED_PREVIEW"):
                                raise Denied("RFC_STATE_DENIED")
                            c.execute("UPDATE requests SET status='CANCELLED' WHERE id=?",(rid,))
                            result={"status":"CANCELLED"}
                        else:
                            if uid!=body["requester_uid"]:
                                raise Denied("ROLE_DENIED")
                            if row["status"]!="APPROVED_PREVIEW" or row["approver"]!=0:
                                raise Denied("RFC_STATE_DENIED")
                            if not body["created_at"]<=row["approved_at"]<=now<body["expires_at"]:
                                raise Denied("RFC_EXPIRED_OR_FUTURE")
                            c.execute("UPDATE requests SET status='CONSUMED_PREVIEW' WHERE id=?",(rid,))
                            result={"status":"CONSUMED_PREVIEW","result":"PROTECTED_NOOP"}
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
        s.settimeout(8)
        s.connect(str(SOCKET))
        send_message(s,msg)
        return read_message(s)


def secure_path(p,mode,kind):
    s=p.lstat()
    if s.st_uid!=0 or stat.S_IMODE(s.st_mode)!=mode or not kind(s.st_mode):
        raise RuntimeError("UNSAFE_PATH "+str(p))


# El servidor identifica al cliente del socket Unix y reserva el proceso privilegiado al administrador.
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
                conn.settimeout(2)
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
    a=p.parse_args()
    if a.op=="serve":
        if a.rfc_id: p.error("unexpected id")
        serve()
        return
    if a.op=="request":
        if a.rfc_id: p.error("unexpected id")
        result=call({"op":"request","action_id":ACTION,"arguments":dict(ARGS)})
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
                print("Escriba APROBAR PREVIEW "+a.rfc_id+": ",file=sys.stderr,end="",flush=True)
                msg["confirmation"]=input()
            result=call(msg)
    print(json.dumps(result,indent=2))
    sys.exit(0 if result["ok"] else 3)


if __name__=="__main__":
    main()
