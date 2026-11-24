#!/usr/bin/python3
"""Guarda privilegiada de ensayo WAN: solo R-HQ/s1p, recuperación restore-only."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4

STATE=Path("/var/lib/netlab360/s07-wan-trial")
PREF=Path("/usr/local/libexec/netlab360/s07-preflight.py")
PSTATE=Path("/var/lib/netlab360/s07-preflight")
EXE=Path("/usr/local/libexec/netlab360/s07-wan-trial.py")
IFACE="s1p"
TTL=180

def now(): return datetime.now(timezone.utc).isoformat()

def load_pf():
    for p,mode,kind in ((EXE,0o755,stat.S_ISREG),(PREF,0o755,stat.S_ISREG),
                         (STATE,0o700,stat.S_ISDIR),(PSTATE,0o700,stat.S_ISDIR)):
        s=p.lstat()
        if s.st_uid!=0 or s.st_gid!=0 or stat.S_IMODE(s.st_mode)!=mode or not kind(s.st_mode):
            raise ValueError("UNSAFE_PATH")
    spec=importlib.util.spec_from_file_location("protected_pf",PREF)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def run(*args):
    p=subprocess.run(args,capture_output=True,text=True,timeout=12,
                     env={"PATH":"/usr/sbin:/usr/bin:/sbin:/bin","LC_ALL":"C"})
    if p.returncode: raise ValueError("COMMAND_FAILED")
    return p.stdout

def unit(rid):
    if not isinstance(rid,str) or not re.fullmatch("[0-9a-f]{32}",rid):
        raise ValueError("BAD_ID")
    return "netlab360-s07-wan-rescue-"+rid

def active(name):
    return subprocess.run(["/usr/bin/systemctl","is-active","--quiet",name],
                          timeout=5).returncode==0

def save(p,d):
    tmp=p.with_name("."+p.name+"."+uuid4().hex)
    with tmp.open("x") as f:
        json.dump(d,f,indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp,p)
    fd=os.open(p.parent,os.O_DIRECTORY|os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)

def read(p,pf):
    pf.secure(p,0o600,stat.S_ISREG)
    d=json.loads(p.read_text())
    if d["target"]!="HQ/s1p" or d["unit"]!=unit(d["id"]) or p.stem!=d["id"]:
        raise ValueError("JOURNAL_INVALID")
    return d

def parse_interface(addr,link):
    """ip -4 addr omite la MAC; unir exclusivamente la misma interfaz."""
    if not isinstance(addr,list) or not isinstance(link,list) or len(addr)!=1 or len(link)!=1:
        raise ValueError("WAN_IDENTITY")
    a,l=addr[0],link[0]
    if (not isinstance(a,dict) or not isinstance(l,dict)
        or a.get("ifname")!=IFACE or l.get("ifname")!=IFACE
        or type(a.get("ifindex")) is not int or a["ifindex"]<=0
        or a["ifindex"]!=l.get("ifindex")
        or type(l.get("ifindex")) is not int):
        raise ValueError("WAN_INTERFACE_MISMATCH")
    addresses=a.get("addr_info",[])
    if not any(x.get("family")=="inet" and x.get("local")=="10.78.0.1" and x.get("prefixlen")==30
               for x in addresses):
        raise ValueError("WAN_IDENTITY")
    mac=l.get("address")
    if not isinstance(mac,str) or not re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}",mac):
        raise ValueError("WAN_MAC_INVALID")
    if mac.lower()=="00:00:00:00:00:00" or int(mac[:2],16)&1:
        raise ValueError("WAN_MAC_INVALID")
    if not isinstance(a.get("flags"),list) or not isinstance(l.get("flags"),list):
        raise ValueError("WAN_FLAGS_INVALID")
    up="UP" in a["flags"]
    if up!=("UP" in l["flags"]):
        raise ValueError("WAN_ADMIN_STATE_CHANGED")
    return {"ifindex":a["ifindex"],"mac":mac.lower()},up

def process_identity(pid):
    return {"netns":Path("/proc",pid,"ns/net").stat().st_ino,
            "boot":Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
            "start_ticks":Path("/proc",pid,"stat").read_text().rsplit(")",1)[1].split()[19]}

def identity(pf,ids):
    r=pf.inspect("HQ")
    if r["id"]!=ids["HQ"]: raise ValueError("PIN_MISMATCH")
    pid=str(r["pid"])
    session=process_identity(pid)
    if session["netns"]==Path("/proc/self/ns/net").stat().st_ino:
        raise ValueError("HOST_NAMESPACE_DENIED")
    prefix=("/usr/bin/nsenter","-t",pid,"-n","/usr/sbin/ip")
    addr=json.loads(run(*prefix,"-j","-4","addr","show","dev",IFACE))
    link=json.loads(run(*prefix,"-j","link","show","dev",IFACE))
    interface,up=parse_interface(addr,link)
    if pf.inspect("HQ")!=r or process_identity(pid)!=session:
        raise ValueError("SESSION_CHANGED")
    return {**r,**session,**interface},up

def set_link(pf,ids,expected,up):
    current,state=identity(pf,ids)
    if current!=expected: raise ValueError("TARGET_SESSION_CHANGED")
    if state!=up:
        run("/usr/bin/nsenter","-t",str(current["pid"]),"-n","/usr/sbin/ip","link","set","dev",IFACE,"up" if up else "down")
    if identity(pf,ids)!=(expected,up):
        raise ValueError("LINK_POSTCONDITION_FAILED")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("op",choices=["check","start","restore","finish"])
    p.add_argument("id",nargs="?")
    a=p.parse_args()
    if os.geteuid()!=0: p.error("root required")
    os.umask(0o077)
    try:
        pf=load_pf()
        ids=pf.read_pin(PSTATE/"router-pin.json")
        with pf.exclusive(PSTATE/"preflight.lock"):
            if a.op=="check":
                if a.id: raise ValueError("UNEXPECTED_ID")
                target,up=identity(pf,ids)
                print(json.dumps({"ok":True,"mode":"READ_ONLY","target":"HQ/s1p",
                                  "identity":target,"admin_up":up},indent=2))
                return
            if a.op=="start":
                if a.id: raise ValueError("UNEXPECTED_ID")
                for prev in STATE.glob("*.json"):
                    if read(prev,pf)["status"]!="VERIFIED": raise ValueError("UNRESOLVED_TRIAL")
                base=pf.observe(ids)
                if base["configuration_status"]!="MET": raise ValueError("PREFLIGHT_DENIED")
                target,up=identity(pf,ids)
                if not up: raise ValueError("BASELINE_NOT_UP")
                rid=uuid4().hex
                name=unit(rid)
                path=STATE/(rid+".json")
                d={"id":rid,"target":"HQ/s1p","identity":target,"unit":name,"status":"PREPARED",
                   "created_at_utc":now(),"baseline":{k:base[k] for k in ("costs","neighbors","routes","management")}}
                save(path,d)
                run("/usr/bin/systemd-run","--unit="+name,"--on-active="+str(TTL)+"s",
                    "--timer-property=AccuracySec=1s","--property=Type=oneshot",
                    "--property=TimeoutStartSec=30s","--property=Restart=on-failure",
                    "--property=RestartSec=5s","/usr/bin/python3","-I",str(EXE),"restore",rid)
                if not active(name+".timer"): raise ValueError("WATCHDOG_NOT_READY")
                d.update(status="ARMED",armed_at_utc=now())
                save(path,d)
                if not active(name+".timer") or identity(pf,ids)!=(target,True): raise ValueError("PRECONDITION_CHANGED")
                d.update(status="APPLYING",stimulus_started_at_utc=now())
                save(path,d)
                set_link(pf,ids,target,False)
                d.update(status="DOWN",down_verified_at_utc=now())
                save(path,d)
            else:
                name=unit(a.id)
                path=STATE/(a.id+".json")
                d=read(path,pf)
                if a.op=="restore":
                    if d["status"]=="VERIFIED":
                        pass
                    elif d["status"] in ("APPLYING","DOWN","RESTORING","UP"):
                        d.update(status="RESTORING")
                        save(path,d)
                        set_link(pf,ids,d["identity"],True)
                        d.update(status="UP",up_verified_at_utc=now())
                        save(path,d)
                    elif d["status"] in ("PREPARED","ARMED"):
                        if identity(pf,ids)!=(d["identity"],True): raise ValueError("UNOWNED_CHANGE")
                        d.update(status="UP",up_verified_at_utc=now())
                        save(path,d)
                    else: raise ValueError("STATE_DENIED")
                else:
                    if d["status"] not in ("UP","VERIFIED") or identity(pf,ids)!=(d["identity"],True):
                        raise ValueError("RESTORATION_UNVERIFIED")
                    final=pf.observe(ids)
                    if {k:final[k] for k in d["baseline"]}!=d["baseline"]:
                        raise ValueError("BASELINE_NOT_RESTORED")
                    d.update(status="VERIFIED",verified_at_utc=now())
                    save(path,d)
                    if active(name+".timer"):
                        try: run("/usr/bin/systemctl","stop",name+".timer")
                        except ValueError:
                            if active(name+".timer"): raise
            print(json.dumps({"ok":True,**d},indent=2))
    except (ValueError,OSError,KeyError,TypeError,subprocess.TimeoutExpired) as e:
        print(json.dumps({"ok":False,"reason":str(e)}))
        sys.exit(3)
if __name__=="__main__": main()
