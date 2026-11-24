#!/usr/bin/python3
"""Ensayo OSPF real supervisado. Alcance fijo S1/s1b, sin write memory."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import pwd
import re
import stat
import subprocess
import sys
import time
from uuid import uuid4

SCHEMA="NETLAB360_S07_OSPF_TRIAL_V1"
STATE=Path("/var/lib/netlab360/s07-ospf-trial")
EXEC=Path("/usr/local/libexec/netlab360/s07-ospf-trial.py")
PREFLIGHT=Path("/usr/local/libexec/netlab360/s07-preflight.py")
PREFSTATE=Path("/var/lib/netlab360/s07-preflight")
TARGET="S1/s1b"
BASE=100
DRIFT=150
REQUEST_TTL=180
WATCHDOG_TTL=90
MARGIN=15
TERMINAL={"VERIFIED","EXPIRED","CANCELLED"}
USER="rc-aa-ec"


def utc():
    return datetime.now(timezone.utc).isoformat()


def secure(p,mode,kind):
    s=p.lstat()
    if s.st_uid!=0 or s.st_gid!=0 or stat.S_IMODE(s.st_mode)!=mode or not kind(s.st_mode):
        raise ValueError("UNSAFE_PATH")


def save(path,d):
    temp=path.with_name("."+path.name+"."+uuid4().hex)
    fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,"w") as f:
            json.dump(d,f,sort_keys=True,allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp,path)
        fd=os.open(path.parent,os.O_DIRECTORY|os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        if temp.exists(): temp.unlink()


def unit(rid):
    if type(rid) is not str or not re.fullmatch("[0-9a-f]{32}",rid):
        raise ValueError("INVALID_RFC_ID")
    return "netlab360-s07-ospf-"+rid


def boot_id():
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()


def expected_drift(state):
    import copy
    out=copy.deepcopy(state)
    if out["costs"].get(TARGET)!=BASE:
        raise ValueError("BASELINE_NOT_MET")
    out["costs"][TARGET]=DRIFT
    return out


def run(*args,timeout=5):
    p=subprocess.run(args,capture_output=True,text=True,timeout=timeout,
                     env={"PATH":"/usr/sbin:/usr/bin:/sbin:/bin","LC_ALL":"C"})
    if p.returncode or len(p.stdout)>262144:
        raise ValueError("COMMAND_FAILED")
    return p.stdout


class RealBackend:
    def __init__(self,pf):
        self.pf=pf
        self.ids=pf.read_pin(PREFSTATE/"router-pin.json")

    def identity(self):
        data={}
        for site in self.pf.SITES:
            r=self.pf.inspect(site)
            if r["id"]!=self.ids[site]:
                raise ValueError("PIN_MISMATCH")
            # PID plus kernel start ticks bind the live process session.
            ticks=Path("/proc",str(r["pid"]),"stat").read_text().rsplit(")",1)[1].split()[19]
            data[site]={**r,"start_ticks":ticks}
        return data

    def target_identity(self,expected):
        r=self.pf.inspect("S1")
        if r["id"]!=self.ids["S1"]:
            raise ValueError("PIN_MISMATCH")
        ticks=Path("/proc",str(r["pid"]),"stat").read_text().rsplit(")",1)[1].split()[19]
        current={**r,"start_ticks":ticks}
        if current!=expected["identity"]["S1"] or boot_id()!=expected["boot_id"]:
            raise ValueError("TARGET_SESSION_CHANGED")
        return current

    def cost(self,expected):
        r=self.target_identity(expected)
        raw=run("/usr/bin/docker","exec",r["id"],"vtysh","-c","show running-config")
        value=self.pf.parse_frr_costs(raw).get("s1b")
        if self.target_identity(expected)!=r or type(value) is not int:
            raise ValueError("TARGET_COST_UNKNOWN")
        return value

    def change(self,expected,before,after):
        if (before,after) not in ((BASE,DRIFT),(DRIFT,BASE)):
            raise ValueError("COST_PAIR_DENIED")
        if self.cost(expected)!=before:
            raise ValueError("EXPECTED_COST_CHANGED")
        r=self.target_identity(expected)
        run("/usr/bin/docker","exec",r["id"],"vtysh",
            "-c","configure terminal","-c","interface s1b",
            "-c","ip ospf cost "+str(after),"-c","end")
        if self.cost(expected)!=after:
            raise ValueError("WRITE_POSTCONDITION_FAILED")

    def snapshot(self):
        tick=time.monotonic()
        identity=self.identity()
        ns=Path("/run/netns/nl360-s02-h-s2-320")
        inode=ns.stat().st_ino
        addrs=json.loads(run("/usr/sbin/ip","netns","exec","nl360-s02-h-s2-320",
                            "/usr/sbin/ip","-j","-4","addr","show"))
        if not any(a.get("local")=="10.72.20.20" and a.get("prefixlen")==24
                   for i in addrs for a in i.get("addr_info",[])):
            raise ValueError("HTTP_SOURCE_IDENTITY")
        d=self.pf.observe(self.ids)
        probes=[]
        for site in self.pf.SITES:
            for peer in self.pf.SITES:
                if site==peer: continue
                run("/usr/bin/nsenter","-t",str(identity[site]["pid"]),"-n","/usr/bin/ping",
                    "-n","-c","1","-W","1","-I",self.pf.LOOPS[site],self.pf.LOOPS[peer],timeout=3)
                probes.append(site+"->"+peer)
        h=json.loads(run("/usr/sbin/ip","netns","exec","nl360-s02-h-s2-320",
                         "/usr/bin/curl","--noproxy","*","--fail","--silent","--show-error",
                         "--max-time","3","http://10.70.20.23:8080/api/v1/service",timeout=5))
        if any(h.get(k)!=v for k,v in {"service":"netlab360-s05-ha","id":"FRONTAL_HQ",
              "role":"frontend","status":"available","active_backend":"BACKEND_HQ",
              "selected_path":"PRINCIPAL"}.items()):
            raise ValueError("HTTP_POSTCONDITION_FAILED")
        if self.identity()!=identity or ns.stat().st_ino!=inode or self.pf.management()!=d["management"]:
            raise ValueError("OBSERVED_IDENTITY_CHANGED")
        if time.monotonic()-tick>30:
            raise ValueError("OBSERVATION_TIMEOUT")
        return {"boot_id":boot_id(),"identity":identity,"management":d["management"],
                "costs":{r["site"]+"/"+r["interface"]:r["observed"] for r in d["costs"]},
                "neighbors":d["neighbors"],"routes":d["routes"],
                "icmp":probes,"http":{"source":"S2-320","namespace_inode":inode,
                                     "frontend":"FRONTAL_HQ","backend":"BACKEND_HQ","status":"available"}}

    def timer_active(self,rid):
        return subprocess.run(["/usr/bin/systemctl","is-active","--quiet",unit(rid)+".timer"],
                              timeout=4,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0

    def arm(self,rid):
        run("/usr/bin/systemd-run","--unit="+unit(rid),
            "--on-active="+str(WATCHDOG_TTL)+"s","--timer-property=AccuracySec=1s",
            "--property=Type=oneshot","--property=TimeoutStartSec=55s",
            "--property=Restart=on-failure","--property=RestartSec=5s",
            "--property=StartLimitIntervalSec=120s","--property=StartLimitBurst=3",
            "--property=NoNewPrivileges=yes","--property=ProtectSystem=strict",
            "--property=ProtectHome=yes","--property=ReadWritePaths="+str(STATE)+" "+str(PREFSTATE),
            "/usr/bin/python3","-I",str(EXEC),"recover",rid,timeout=8)
        return self.timer_active(rid)


class Trial:
    def __init__(self,root,rid,backend,clock=time.monotonic,protected=False):
        unit(rid)
        self.rid=rid
        self.root=root
        self.path=root/rid/"transaction.json"
        self.b=backend
        self.clock=clock
        self.protected=protected

    def load(self):
        if self.protected:
            secure(self.path.parent,0o700,stat.S_ISDIR)
            secure(self.path,0o600,stat.S_ISREG)
        if self.path.stat().st_size>262144:
            raise ValueError("JOURNAL_SIZE")
        d=json.loads(self.path.read_text())
        if (d["schema"]!=SCHEMA or d["rfc_id"]!=self.rid or d["target"]!=TARGET
            or d["baseline_cost"]!=BASE or d["drift_cost"]!=DRIFT or d["unit"]!=unit(self.rid)):
            raise ValueError("RFC_BINDING_INVALID")
        return d

    def event(self,d,status,**data):
        d["status"]=status
        d["events"].append({"state":status,"at_utc":utc(),"monotonic":self.clock(),**data})
        save(self.path,d)

    def request(self,uid,desired):
        state=self.b.snapshot()
        if state["costs"]!=desired:
            raise ValueError("BASELINE_NOT_MET")
        self.path.parent.mkdir(mode=0o700)
        d={"schema":SCHEMA,"rfc_id":self.rid,"target":TARGET,"unit":unit(self.rid),
           "baseline_cost":BASE,"drift_cost":DRIFT,"requester_uid":uid,
           "request_deadline":self.clock()+REQUEST_TTL,"baseline":state,
           "action_id":"S07_RESTORE_OSPF_COST_V1","arguments":{"site":"S1","interface":"s1b","cost":BASE},
           "authorization_scope":"EXPERIMENT_AND_EMERGENCY_RESTORE_ONLY",
           "events":[]}
        self.event(d,"PENDING")
        return d

    def start(self,confirmation):
        d=self.load()
        if confirmation!="APROBAR ENSAYO "+self.rid or d["status"]!="PENDING":
            raise ValueError("APPROVAL_DENIED")
        if self.clock()>=d["request_deadline"]:
            self.event(d,"EXPIRED")
            raise ValueError("RFC_EXPIRED")
        if self.b.snapshot()!=d["baseline"]:
            raise ValueError("EXPECTED_STATE_CHANGED")
        if self.clock()>=d["request_deadline"]:
            self.event(d,"EXPIRED")
            raise ValueError("RFC_EXPIRED")
        self.event(d,"APPROVED_EXPERIMENT",approver_uid=0)
        d["watchdog_deadline"]=self.clock()+WATCHDOG_TTL
        if not self.b.arm(self.rid):
            self.event(d,"CANCELLED",reason="WATCHDOG_NOT_READY")
            raise ValueError("WATCHDOG_NOT_READY")
        self.event(d,"ARMED")
        if not self.b.timer_active(self.rid) or self.clock()+MARGIN>=d["watchdog_deadline"]:
            raise ValueError("WATCHDOG_NOT_READY")
        if self.b.cost(d["baseline"])!=BASE:
            raise ValueError("BASELINE_CHANGED")
        self.event(d,"APPLYING")
        try:
            self.b.change(d["baseline"],BASE,DRIFT)
            self.event(d,"DRIFT_APPLIED",observed=DRIFT)
            observed=self.b.snapshot()
            if observed!=expected_drift(d["baseline"]):
                raise ValueError("DRIFT_POSTCONDITION_FAILED")
            d["drift_observation"]=observed
            self.event(d,"DRIFT_VERIFIED",observed=DRIFT)
            return d
        except Exception:
            # The independently armed watchdog remains active even on failure.
            # Attempt safe immediate recovery; on failure retain journal and timer.
            self.recover("FAILSAFE")
            raise

    def restore(self,confirmation):
        d=self.load()
        if confirmation!="APROBAR RESTAURACION "+self.rid or d["status"]!="DRIFT_VERIFIED":
            raise ValueError("RESTORATION_APPROVAL_DENIED")
        if self.clock()+MARGIN>=d["watchdog_deadline"]:
            raise ValueError("WATCHDOG_DEADLINE_NEAR")
        if self.b.snapshot()!=d["drift_observation"]:
            raise ValueError("EXPECTED_DRIFT_CHANGED")
        if not self.b.timer_active(self.rid) or self.clock()+MARGIN>=d["watchdog_deadline"]:
            raise ValueError("WATCHDOG_NOT_READY")
        self.event(d,"APPROVED_RESTORE",approver_uid=0)
        return self.recover("HUMAN_APPROVED")

    def recover(self,source):
        d=self.load()
        if d["status"]=="VERIFIED":
            return d
        if d["status"] not in {"APPROVED_EXPERIMENT","ARMED","APPLYING","DRIFT_APPLIED","DRIFT_VERIFIED",
                               "APPROVED_RESTORE","RESTORING","RESTORED_UNVERIFIED","ESCALATION_REQUIRED"}:
            raise ValueError("RECOVERY_STATE_DENIED")
        if source not in {"HUMAN_APPROVED","WATCHDOG","FAILSAFE"}:
            raise ValueError("RECOVERY_SOURCE_DENIED")
        if source=="HUMAN_APPROVED" and d["status"]!="APPROVED_RESTORE":
            raise ValueError("RESTORE_NOT_APPROVED")
        try:
            old=self.b.cost(d["baseline"])
            if old not in (BASE,DRIFT):
                raise ValueError("UNEXPECTED_TARGET_COST")
            # Before APPLYING, this trial did not own any change to the router.
            if not any(e["state"]=="APPLYING" for e in d["events"]) and old!=BASE:
                raise ValueError("UNOWNED_DRIFT")
            self.event(d,"RESTORING",source=source,observed=old)
            if old==DRIFT:
                self.b.change(d["baseline"],DRIFT,BASE)
            if self.b.cost(d["baseline"])!=BASE:
                raise ValueError("RESTORE_COST_FAILED")
        except Exception as e:
            self.event(d,"ESCALATION_REQUIRED",reason=str(e),source=source)
            raise
        self.event(d,"RESTORED_UNVERIFIED",observed=BASE,source=source)
        observed=self.b.snapshot()
        if observed!=d["baseline"]:
            raise ValueError("POSTCONDITION_NOT_MET")
        d["final_observation"]=observed
        self.event(d,"VERIFIED",source=source,observed=BASE)
        return d


def load_preflight():
    secure(PREFLIGHT,0o755,stat.S_ISREG)
    secure(PREFSTATE,0o700,stat.S_ISDIR)
    spec=importlib.util.spec_from_file_location("netlab360_protected_preflight",PREFLIGHT)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def confirmation(prefix,rid,d):
    if not sys.stdin.isatty():
        raise ValueError("INTERACTIVE_TTY_REQUIRED")
    print(json.dumps({"rfc_id":rid,"target":TARGET,"status":d["status"],
                      "baseline":BASE,"drift":DRIFT,"watchdog_seconds":WATCHDOG_TTL},indent=2),file=sys.stderr)
    print(prefix+" "+rid+": ",end="",flush=True,file=sys.stderr)
    return input()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("op",choices=("request","start","restore","status","recover"))
    p.add_argument("rfc_id",nargs="?")
    a=p.parse_args()
    if os.geteuid()!=0: p.error("root required")
    os.umask(0o077)
    try:
        secure(EXEC,0o755,stat.S_ISREG)
        secure(STATE,0o700,stat.S_ISDIR)
        pf=load_preflight()
        b=RealBackend(pf)
        if a.op=="request":
            if a.rfc_id: p.error("unexpected id")
            uid=pwd.getpwnam(USER).pw_uid
            if os.environ.get("SUDO_UID")!=str(uid):
                raise ValueError("LAB_OPERATOR_REQUIRED")
            t=Trial(STATE,uuid4().hex,b,protected=True)
        else:
            t=Trial(STATE,a.rfc_id,b,protected=True)
        typed=None
        if a.op in ("start","restore"):
            old=t.load()
            typed=confirmation("APROBAR ENSAYO" if a.op=="start" else "APROBAR RESTAURACION",t.rid,old)
        with pf.exclusive(PREFSTATE/"preflight.lock"):
            if a.op=="request":
                for path in STATE.glob("*/transaction.json"):
                    prev=Trial(STATE,path.parent.name,b,protected=True)
                    row=prev.load()
                    if row["status"]=="PENDING" and prev.clock()>=row["request_deadline"]:
                        prev.event(row,"EXPIRED")
                    elif row["status"] not in TERMINAL:
                        raise ValueError("UNRESOLVED_TRANSACTION")
                desired={s+"/"+i:v for s,items in pf.profile().items() for i,v in items.items()}
                result=t.request(uid,desired)
            elif a.op=="start":
                result=t.start(typed)
            elif a.op=="restore":
                result=t.restore(typed)
            elif a.op=="recover":
                result=t.recover("WATCHDOG")
            else:
                result=t.load()
        print(json.dumps({"ok":True,"transaction":result},indent=2,allow_nan=False))
    except (ValueError,OSError,KeyError,TypeError,subprocess.TimeoutExpired) as e:
        print(json.dumps({"ok":False,"reason":str(e)},indent=2))
        sys.exit(3)


if __name__=="__main__":
    main()
