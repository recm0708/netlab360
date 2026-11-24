#!/usr/bin/python3
"""API S07 versionada: HTTP local sobre Unix, identidad del kernel, broker fijo."""
import argparse
from contextlib import closing
import http.client
from http.server import BaseHTTPRequestHandler
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import socketserver
import sqlite3
import stat
import struct
import sys
from uuid import uuid4

STATE=Path("/var/lib/netlab360/s07-api")
SOCKET=Path("/run/netlab360-s07-api/api.sock")
EXEC=Path("/usr/local/libexec/netlab360/s07-api.py")
BROKER=Path("/usr/local/libexec/netlab360/s07-ospf-broker.py")
SCHEMA="NETLAB360_S07_API_V1"
MAX=65536
RID=re.compile(r"[0-9a-f]{32}")
KEY=re.compile(r"[A-Za-z0-9_-]{16,80}")

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def response(code,**body):
    return code,{"schema":SCHEMA,**body}

def deny(code,reason):
    return response(code,ok=False,reason=reason)

class Replay:
    """Reserva persistente antes de ejecutar; fallo ambiguo nunca se reintenta."""
    def __init__(self,path):
        self.path=path
        with closing(self.connect()) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS requests(
                uid INTEGER, route TEXT, key TEXT, body TEXT,
                code INTEGER, result TEXT, PRIMARY KEY(uid,route,key))""")
    def connect(self):
        c=sqlite3.connect(self.path,timeout=5,isolation_level=None)
        c.execute("PRAGMA synchronous=FULL")
        return c
    def apply(self,uid,route,key,body,fn):
        if not isinstance(key,str) or not KEY.fullmatch(key):
            return deny(400,"IDEMPOTENCY_KEY_REQUIRED")
        raw=canon(body)
        with closing(self.connect()) as c:
            c.execute("BEGIN IMMEDIATE")
            row=c.execute("SELECT body,code,result FROM requests WHERE uid=? AND route=? AND key=?",
                          (uid,route,key)).fetchone()
            if row:
                c.commit()
                if row[0]!=raw: return deny(409,"IDEMPOTENCY_CONFLICT")
                if row[1] is None: return deny(409,"OUTCOME_UNCERTAIN_RECONCILE")
                return row[1],json.loads(row[2])
            if c.execute("SELECT count(*) FROM requests").fetchone()[0]>=2048:
                c.rollback();return deny(503,"IDEMPOTENCY_CAPACITY")
            c.execute("INSERT INTO requests VALUES(?,?,?,?,NULL,NULL)",(uid,route,key,raw))
            c.commit()
            code,out=fn()
            c.execute("UPDATE requests SET code=?,result=? WHERE uid=? AND route=? AND key=?",
                      (code,canon(out),uid,route,key))
            return code,out

class API:
    def __init__(self,broker,replay,advisory,audit,lock):
        self.b=broker;self.replay=replay;self.advisory=advisory
        self.audit=audit;self.lock=lock
    def invoke(self,uid,msg):
        d=self.b.handle(uid,msg)
        if d["ok"]: return response(200,ok=True,result=d)
        reason=d.get("reason","BROKER_DENIED")
        status=403 if reason in ("ROLE_DENIED","PEER_DENIED","CONFIRMATION_REQUIRED") else 409
        return deny(status,reason)
    def intent(self,rid):
        t=self.b.trial(rid);d=t.load()
        if "broker_rfc" not in d or d["requester_uid"]!=self.b.uid:
            return deny(404,"RFC_NOT_FOUND")
        current=self.b.b.snapshot()
        base=d["baseline"]
        wanted=self.b.desired
        deviations=[{"resource":k,"desired":v,"observed":current["costs"].get(k)}
                    for k,v in sorted(wanted.items()) if current["costs"].get(k)!=v]
        drift=d["status"]=="DRIFT_VERIFIED" and current==d.get("drift_observation") and self.b.b.timer_active(rid)
        exact=deviations==[{"resource":"S1/s1b","desired":100,"observed":150}]
        recommendation={"decision":"REQUEST_HUMAN_RESTORE","action_id":"S07_RESTORE_OSPF_COST_V1",
                        "arguments":{"site":"S1","interface":"s1b","cost":100}} if drift and exact else {
                            "decision":"NO_CHANGE" if not deviations and current==base else "ABSTAIN_NO_CHANGE"}
        return response(200,ok=True,result={"source":"ROOT_OWNED_OSPF_BACKEND",
            "observed_at_utc":self.b.m.utc(),"rfc_id":rid,"configuration_compliance":"NOT_MET" if deviations else "MET",
            "deviations":deviations,"ospf_full":sum(x["state"]=="Full" for x in current["neighbors"]),
            "fib_primary":sum(x["selection"]=="PRIMARY" for x in current["routes"]),
            "icmp_samples":len(current["icmp"]),"http":current["http"]["status"],
            "recommendation":recommendation,"confirmed_root_cause":None,
            "network_mutations_authorized":False,"continuous_availability_measured":False})
    def dispatch(self,uid,method,path,body=None,key=None):
        if uid not in (0,self.b.uid): return deny(403,"PEER_DENIED")
        if method=="GET":
            if body is not None: return deny(400,"BODY_DENIED")
            if path=="/api/v1/health":
                return response(200,ok=True,result={"transport":"HTTP_UNIX","authorization":"SO_PEERCRED","automatic_remediation":False})
            if path in ("/api/v1/incidents","/api/v1/hypotheses","/api/v1/runbooks"):
                section=path.rsplit("/",1)[1]
                return response(200,ok=True,result={"source":"OPERATOR_ADVISORY_SNAPSHOT",
                    "observed_at_utc":self.advisory["observed_at_utc"],"data":self.advisory[section],
                    "historical":True,"authorization_evidence":False})
            if path=="/api/v1/audit":
                return response(200,ok=True,result=self.audit())
            match=re.fullmatch(r"/api/v1/rfcs/([0-9a-f]{32})(?:/(intent|execution))?",path)
            if not match: return deny(404,"ROUTE_DENIED")
            rid,part=match.groups()
            with self.lock():
                if part=="intent":
                    try: return self.intent(rid)
                    except (ValueError,KeyError,OSError,TypeError): return deny(409,"INTENT_UNAVAILABLE")
                return self.invoke(uid,{"op":"show","rfc_id":rid})
        if method!="POST": return deny(405,"METHOD_DENIED")
        if type(body) is not dict: return deny(400,"BODY_INVALID")
        if path=="/api/v1/rfcs":
            if uid!=self.b.uid: return deny(403,"ROLE_DENIED")
            if set(body)!={"action_id","arguments"}: return deny(400,"BODY_INVALID")
            msg={"op":"request",**body}
        else:
            match=re.fullmatch(r"/api/v1/rfcs/([0-9a-f]{32})/(restore-request|approve-execute|cancel)",path)
            if not match: return deny(404,"ROUTE_DENIED")
            rid,op=match.groups()
            required={"restore-request":set(),"approve-execute":{"binding","confirmation"},"cancel":{"binding"}}[op]
            if set(body)!=required: return deny(400,"BODY_INVALID")
            if uid!=(0 if op=="approve-execute" else self.b.uid): return deny(403,"ROLE_DENIED")
            msg={"op":{"restore-request":"request_restore","approve-execute":"approve","cancel":"cancel"}[op],"rfc_id":rid,**body}
        def perform():
            with self.lock():
                return self.invoke(uid,msg)
        return self.replay.apply(uid,path,key,body,perform)

class Handler(BaseHTTPRequestHandler):
    protocol_version="HTTP/1.0"
    def setup(self):
        self.request.settimeout(5)
        super().setup()
    def do_GET(self): self.process("GET")
    def do_POST(self): self.process("POST")
    def do_PUT(self): self.process("PUT")
    def do_DELETE(self): self.process("DELETE")
    def process(self,method):
        _,uid,_=struct.unpack("3i",self.request.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize("3i")))
        try:
            if self.headers.get("Transfer-Encoding") or len(self.headers.get_all("Content-Length",[]))>1:
                code,out=deny(400,"FRAMING_DENIED")
            elif method=="POST":
                length=int(self.headers.get("Content-Length","-1"))
                if not 0<length<=MAX or self.headers.get_content_type()!="application/json":
                    code,out=deny(400,"BODY_INVALID")
                else:
                    raw=self.rfile.read(length)
                    if len(raw)!=length: raise ValueError("INCOMPLETE_BODY")
                    body=json.loads(raw)
                    code,out=self.server.api.dispatch(uid,method,self.path,body,self.headers.get("Idempotency-Key"))
            elif self.headers.get("Content-Length","0")!="0":
                code,out=deny(400,"BODY_DENIED")
            else:
                code,out=self.server.api.dispatch(uid,method,self.path)
        except (ValueError,TypeError,KeyError):
            code,out=deny(400,"REQUEST_INVALID")
        except (OSError,RuntimeError,sqlite3.Error):
            code,out=deny(503,"BACKEND_UNAVAILABLE_RECONCILE")
        raw=canon(out).encode()
        self.send_response(code);self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(raw)));self.send_header("Cache-Control","no-store")
        self.end_headers();self.wfile.write(raw)
    def log_message(self,*args): pass

class Server(socketserver.UnixStreamServer):
    request_queue_size=8

def load_module(path,name):
    s=path.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_uid!=0 or s.st_gid!=0 or stat.S_IMODE(s.st_mode)!=0o755:
        raise RuntimeError("UNSAFE_MODULE")
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def serve():
    if os.geteuid()!=0: raise RuntimeError("ROOT_REQUIRED")
    os.umask(0o077)
    br=load_module(BROKER,"protected_broker");m=br.load_trial()
    m.secure(EXEC,0o755,stat.S_ISREG);m.secure(STATE,0o700,stat.S_ISDIR)
    m.secure(SOCKET.parent,0o755,stat.S_ISDIR);m.secure(br.STATE,0o700,stat.S_ISDIR)
    m.secure(m.STATE,0o700,stat.S_ISDIR)
    advisory_path=STATE/"advisory.json"
    m.secure(advisory_path,0o600,stat.S_ISREG)
    if advisory_path.stat().st_size>2_000_000: raise RuntimeError("ADVISORY_TOO_LARGE")
    advisory=json.loads(advisory_path.read_text())
    if set(advisory)!={"observed_at_utc","incidents","hypotheses","runbooks"}: raise RuntimeError("ADVISORY_INVALID")
    db=STATE/"idempotency.sqlite3"
    if db.exists() or db.is_symlink(): m.secure(db,0o600,stat.S_ISREG)
    replay=Replay(db);m.secure(db,0o600,stat.S_ISREG)
    import pwd
    user=pwd.getpwnam(m.USER);pf=m.load_preflight()
    desired={s+"/"+i:v for s,interfaces in pf.profile().items() for i,v in interfaces.items()}
    b=br.Broker(m,m.STATE,m.RealBackend(pf),desired,user.pw_uid,br.record)
    def audit():
        p=br.STATE/"audit.jsonl"
        if not p.exists(): return []
        m.secure(p,0o600,stat.S_ISREG)
        if p.stat().st_size>8_000_000: raise RuntimeError("AUDIT_TOO_LARGE")
        return [json.loads(x) for x in p.read_text().splitlines()[-100:]]
    if SOCKET.exists() or SOCKET.is_symlink(): raise RuntimeError("SOCKET_EXISTS")
    with Server(str(SOCKET),Handler) as srv:
        srv.api=API(b,replay,advisory,audit,lambda:pf.exclusive(m.PREFSTATE/"preflight.lock"))
        os.chown(SOCKET,0,user.pw_gid);os.chmod(SOCKET,0o660)
        srv.serve_forever()

class UnixHTTP(http.client.HTTPConnection):
    def connect(self):
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout);self.sock.connect(str(SOCKET))

def call(method,path,body=None,key=None):
    c=UnixHTTP("localhost",timeout=75)
    headers={}
    if body is not None: headers["Content-Type"]="application/json"
    if key: headers["Idempotency-Key"]=key
    try:
        c.request(method,path,None if body is None else canon(body),headers)
        r=c.getresponse();raw=r.read(2_000_001)
        if len(raw)>2_000_000: raise ValueError("RESPONSE_TOO_LARGE")
        return r.status,json.loads(raw)
    finally: c.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("op",choices=("serve","approve"))
    p.add_argument("rid",nargs="?")
    p.add_argument("--stage",choices=("EXPERIMENT","RESTORE"))
    p.add_argument("--key")
    a=p.parse_args()
    if a.op=="serve": serve();return
    if os.geteuid()!=0 or not sys.stdin.isatty() or not a.rid or not RID.fullmatch(a.rid) or not a.stage or not a.key:
        p.error("root TTY, RFC, stage y key requeridos")
    path="/api/v1/rfcs/"+a.rid
    status,d=call("GET",path)
    if status!=200: print(json.dumps(d));sys.exit(3)
    binding=d["result"]["approvals"][a.stage]["binding"]
    print(json.dumps({k:binding[k] for k in ("action_id","arguments","resource","approval_id","requester_uid","expires_monotonic")},indent=2),file=sys.stderr)
    print("APROBAR RFC "+binding["approval_id"]+": ",end="",file=sys.stderr,flush=True)
    confirmation=input()
    status,d=call("POST",path+"/approve-execute",{"binding":binding,"confirmation":confirmation},a.key)
    print(json.dumps(d,indent=2));sys.exit(0 if status==200 else 3)

if __name__=="__main__": main()
