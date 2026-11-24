#!/usr/bin/python3
"""S07: ensayo protegido del watchdog, sin operaciones de red.

El único backend habilitado es un archivo de estado aislado.
El plan de OSPF define el alcance futuro, pero no se ejecuta aquí.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
from uuid import uuid4

SCHEMA="NETLAB360_S07_RECOVERY_REHEARSAL_V1"
STATE=Path("/var/lib/netlab360/s07-recovery")
EXEC=Path("/usr/local/libexec/netlab360/s07-recovery.py")
TTL=15
MARGIN=4
TARGET="S1/s1b"
BASE=100
DRIFT=150
ACTION="S07_RESTORE_OSPF_COST_V1"


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)


def unit_name(rid):
    if type(rid) is not str or not re.fullmatch(r"[0-9a-f]{32}",rid):
        raise ValueError("INVALID_RUN_ID")
    return "netlab360-s07-recovery-"+rid


def secure(path,mode,kind):
    s=path.lstat()
    if s.st_uid!=0 or s.st_gid!=0 or stat.S_IMODE(s.st_mode)!=mode or not kind(s.st_mode):
        raise ValueError("UNSAFE_PATH")


def read_json(path,protected=False):
    if protected:
        secure(path,0o600,stat.S_ISREG)
    if path.stat().st_size>65536:
        raise ValueError("STATE_TOO_LARGE")
    return json.loads(path.read_text())


# Persistimos cada estado mediante archivo temporal exclusivo antes de sustituir el registro.
def save(path,data):
    tmp=path.with_name("."+path.name+"."+uuid4().hex)
    fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,"w") as f:
            f.write(canonical(data)+"\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp,path)
        fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        if tmp.exists(): tmp.unlink()


@contextmanager
def exclusive(path):
    fd=os.open(path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or stat.S_IMODE(s.st_mode)!=0o600:
            raise ValueError("UNSAFE_LOCK")
        if os.geteuid()==0 and (s.st_uid!=0 or s.st_gid!=0):
            raise ValueError("UNSAFE_LOCK")
        end=time.monotonic()+5
        while True:
            try:
                fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic()>=end: raise ValueError("RESOURCE_BUSY") from None
                time.sleep(.1)
        yield
    finally:
        os.close(fd)


def plan():
    return {"schema":"NETLAB360_S07_BOUNDED_ACTION_PLAN_V1","action_id":ACTION,
            "arguments":{"site":"S1","interface":"s1b","cost":BASE},
            "target":TARGET,"baseline":BASE,"experimental_drift":DRIFT,
            "scope":"SINGLE_BACKUP_OSPF_INTERFACE","network_executor_enabled":False,
            "requires":["FRESH_PREFLIGHT","HUMAN_RFC","OWNERSHIP","EXCLUSIVE_LOCK",
                        "ARMED_INDEPENDENT_WATCHDOG","VERIFIED_POSTCONDITIONS"],
            "no_write_memory":True,"network_mutations_authorized":False}


# La máquina de estados trabaja únicamente sobre el fixture de archivo y el identificador de este ensayo.
class Trial:
    def __init__(self,root,rid,boot_id,clock=time.monotonic,protected=False):
        unit_name(rid)
        self.root=root
        self.rid=rid
        self.boot=boot_id
        self.clock=clock
        self.protected=protected
        self.directory=root/rid
        self.journal=self.directory/"transaction.json"
        self.fixture=self.directory/"fixture.json"

    def load(self):
        if self.protected: secure(self.directory,0o700,stat.S_ISDIR)
        d=read_json(self.journal,self.protected)
        if (d.get("schema")!=SCHEMA or d.get("run_id")!=self.rid
            or d.get("boot_id")!=self.boot or d.get("mode")!="ISOLATED_FILE_REHEARSAL"
            or d.get("target")!=TARGET or d.get("baseline")!=BASE or d.get("drift")!=DRIFT
            or d.get("unit")!=unit_name(self.rid)):
            raise ValueError("TRANSACTION_BINDING_INVALID")
        return d

    def value(self):
        f=read_json(self.fixture,self.protected)
        if set(f)!={"run_id","cost"} or f["run_id"]!=self.rid or type(f["cost"]) is not int:
            raise ValueError("FIXTURE_BINDING_INVALID")
        if f["cost"] not in (BASE,DRIFT):
            raise ValueError("UNEXPECTED_STATE")
        return f["cost"]

    def event(self,d,status,**details):
        d["status"]=status
        d["events"].append({"state":status,"at_utc":now(),"monotonic":self.clock(),**details})
        save(self.journal,d)

    def prepare(self):
        self.directory.mkdir(mode=0o700)
        save(self.fixture,{"run_id":self.rid,"cost":BASE})
        d={"schema":SCHEMA,"run_id":self.rid,"boot_id":self.boot,"mode":"ISOLATED_FILE_REHEARSAL",
           "target":TARGET,"baseline":BASE,"drift":DRIFT,"unit":unit_name(self.rid),
           "deadline_monotonic":self.clock()+TTL,"ttl_seconds":TTL,"events":[],
           "network_mutations_authorized":False}
        self.event(d,"PREPARED",observed=BASE)
        return d

    def arm(self,timer_active):
        d=self.load()
        if d["status"]!="PREPARED" or not timer_active or self.clock()+MARGIN>=d["deadline_monotonic"]:
            raise ValueError("WATCHDOG_NOT_READY")
        self.event(d,"ARMED")
        return d

    def apply(self,timer_active):
        d=self.load()
        if d["status"]!="ARMED" or not timer_active or self.clock()+MARGIN>=d["deadline_monotonic"]:
            raise ValueError("WATCHDOG_NOT_READY")
        if self.value()!=BASE: raise ValueError("BASELINE_NOT_MET")
        self.event(d,"APPLYING",observed=BASE)
        save(self.fixture,{"run_id":self.rid,"cost":DRIFT})
        if self.value()!=DRIFT: raise ValueError("APPLY_VERIFICATION_FAILED")
        self.event(d,"DRIFT_APPLIED",observed=DRIFT)
        return d

    def recover(self):
        d=self.load()
        if d["status"]=="RECOVERED":
            if self.value()!=BASE: raise ValueError("RESTORATION_DIVERGED")
            return d
        if d["status"] not in ("PREPARED","ARMED","APPLYING","DRIFT_APPLIED","RECOVERING"):
            raise ValueError("RECOVERY_STATE_DENIED")
        try:
            got=self.value()
        except (ValueError,OSError):
            self.event(d,"ESCALATION_REQUIRED",reason="FIXTURE_UNSAFE")
            raise
        self.event(d,"RECOVERING",observed=got)
        if got==DRIFT:
            save(self.fixture,{"run_id":self.rid,"cost":BASE})
        if self.value()!=BASE:
            self.event(d,"ESCALATION_REQUIRED",reason="POSTCONDITION_FAILED")
            raise ValueError("POSTCONDITION_FAILED")
        self.event(d,"RECOVERED",observed=BASE,restored_by="INDEPENDENT_TIMER",
                   prior_cost=got,network_mutations=0)
        return d

    def status(self):
        d=self.load()
        return {"transaction":d,"fixture_cost":self.value(),
                "network_mutations_authorized":False}


def run(*argv):
    p=subprocess.run(argv,capture_output=True,text=True,timeout=8,
                     env={"PATH":"/usr/sbin:/usr/bin:/sbin:/bin","LC_ALL":"C"})
    if p.returncode: raise ValueError("SYSTEMD_OPERATION_FAILED")
    return p.stdout


def active(unit):
    return subprocess.run(["/usr/bin/systemctl","is-active","--quiet",unit+".timer"],
                          timeout=4,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0


def main():
    p=argparse.ArgumentParser()
    p.add_argument("op",choices=("plan","rehearse","status","recover"))
    p.add_argument("run_id",nargs="?")
    a=p.parse_args()
    if os.geteuid()!=0: p.error("root required")
    os.umask(0o077)
    try:
        secure(STATE,0o700,stat.S_ISDIR)
        secure(EXEC,0o755,stat.S_ISREG)
        boot=Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        if a.op=="plan":
            if a.run_id: p.error("unexpected run_id")
            result=plan()
        else:
            if a.op=="rehearse":
                if a.run_id: p.error("unexpected run_id")
                rid=uuid4().hex
            else:
                rid=a.run_id
            t=Trial(STATE,rid,boot,protected=True)
            with exclusive(STATE/"recovery.lock"):
                if a.op=="rehearse":
                    d=t.prepare()
                    u=d["unit"]
                    run("/usr/bin/systemd-run","--unit="+u,"--on-active="+str(TTL)+"s",
                        "--timer-property=AccuracySec=1s","--property=Type=oneshot",
                        "--property=TimeoutStartSec=30s","--property=NoNewPrivileges=yes",
                        "--property=ProtectSystem=strict","--property=ProtectHome=yes",
                        "--property=ReadWritePaths="+str(STATE),
                        "/usr/bin/python3","-I",str(EXEC),"recover",rid)
                    t.arm(active(u))
                    t.apply(active(u))
                elif a.op=="recover":
                    t.recover()
                result=t.status()
        print(json.dumps({"ok":True,**result},indent=2))
    except (ValueError,OSError,KeyError,TypeError,subprocess.TimeoutExpired) as e:
        print(json.dumps({"ok":False,"reason":str(e),"network_mutations_authorized":False}))
        sys.exit(3)


if __name__=="__main__":
    main()
