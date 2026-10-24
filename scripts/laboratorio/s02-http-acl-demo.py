#!/usr/bin/env python3
"""NETLAB360 S02: HTTP real multisede y ACL firewall SOLO router HQ.

Ensayo autocontenido: servidores HTTP efimeros 8080 en HQ/S1/S2,
8081 en S1, prueba baseline 8081 activa, nft bloquea solo HQ110->S1:8081,
verifica denegacion y mantiene 8080; restaura reglas al finalizar.
Los namespaces/routers/S02 VLAN siguen intactos tras el ensayo.
"""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT = Path.home() / "proyectos/netlab360"
BASE = Path.home() / "netlab360-bootstrap/evidencias"
SPEC = importlib.util.spec_from_file_location("s02lan", ROOT/"scripts/laboratorio/s02-lan-vlan.py")
assert SPEC and SPEC.loader
lan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lan)
TABLE = "nl360_s02_acl"
SERVICES = (
    ("HQ", 120, "10.70.20.20", 8080),
    ("S1", 220, "10.71.20.20", 8080),
    ("S2", 320, "10.72.20.20", 8080),
    ("S1", 220, "10.71.20.20", 8081),
)


def cmd(*args: str, allow: bool = False, input_text: str | None = None, timeout: int = 20) -> str:
    p = subprocess.run(args, text=True, input=input_text, capture_output=True, timeout=timeout)
    if p.returncode and not allow:
        raise RuntimeError(f"exit={p.returncode}: {' '.join(args)}\n{p.stdout[-900:]} {p.stderr[-1100:]}")
    return p.stdout


def sudo(*args: str, **kw) -> str:
    return cmd("sudo", "-n", *args, **kw)


def curl(namespace: str, url: str, success: bool = True) -> str:
    p = subprocess.run(
        ["sudo", "-n", "ip", "netns", "exec", namespace, "curl",
         "--noproxy", "*", "-fsS", "--connect-timeout", "2",
         "--max-time", "5", url],
        capture_output=True, text=True, timeout=9
    )
    if success and (p.returncode != 0 or "NETLAB360_S02_HTTP_" not in p.stdout):
        raise RuntimeError(f"HTTP falla {namespace} -> {url}: exit {p.returncode} {p.stdout} {p.stderr}")
    if not success and p.returncode == 0:
        raise RuntimeError(f"ACL no bloqueo solicitud a {url}: {p.stdout}")
    return p.stdout.strip()


def main() -> None:
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal, sudo -v previamente")
    d = lan.plan()
    routers = lan.router_state()
    if not lan.STATE.is_file() or lan.STATE.is_symlink():
        raise RuntimeError("LAN S02 no desplegada")
    state = json.loads(lan.STATE.read_text(encoding="utf-8"))
    lan.owns(state, routers)
    hpid = routers["HQ"]["pid"]
    if sudo("nsenter", "-t", hpid, "-n", "nft", "list", "table",
            "inet", TABLE, allow=True).strip():
        raise RuntimeError("Tabla ACL S02 ya existe, no sobrescribir")
    if lan.host_state() != state["host"]:
        raise RuntimeError("Gestion administrativa no coincide con baseline")
    sudo("nsenter", "-t", hpid, "-n", "nft", "--version")
    BASE.mkdir(parents=True, exist_ok=True)
    servers = []
    fw_installed = False
    try:
        print("========== HTTP S02 SERVICIOS ==========", flush=True)
        for site, vlan, ipaddr, port in SERVICES:
            directory = BASE / f"s02-http-{site.lower()}-{port}"
            directory.mkdir(parents=True, exist_ok=True)
            (directory/"index.html").write_text(
                f"NETLAB360_S02_HTTP_{site}_{port}_OK\n", encoding="utf-8"
            )
            source_ns = f"nl360-s02-h-{site.lower()}-{vlan}"
            log = open(BASE/f"S02_HTTP_Server_{site}_{port}.log", "ab")
            process = subprocess.Popen(
                ["sudo", "-n", "ip", "netns", "exec", source_ns,
                 "python3", "-m", "http.server", str(port),
                 "--bind", ipaddr, "--directory", str(directory)],
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True
            )
            servers.append((process, log))
            print(f"S02_SERVIDOR_INICIADO={site}:{ipaddr}:{port}", flush=True)
        time.sleep(2)
        hq_users = "nl360-s02-h-hq-110"
        s1_users = "nl360-s02-h-s1-210"
        s2_users = "nl360-s02-h-s2-310"
        tests = (
            (hq_users, "http://10.71.20.20:8080/", "HQ_A_S1"),
            (hq_users, "http://10.72.20.20:8080/", "HQ_A_S2"),
            (s1_users, "http://10.70.20.20:8080/", "S1_A_HQ"),
            (s2_users, "http://10.71.20.20:8080/", "S2_A_S1"),
        )
        for ns, url, name in tests:
            body = curl(ns, url)
            print(f"S02_HTTP_BASELINE_{name}=OK BODY={body}")
        alive = curl(hq_users, "http://10.71.20.20:8081/")
        print(f"S02_SERVICIO_8081_PREACL=ACTIVO BODY={alive}")

        script = (
            f"table inet {TABLE} {{\n"
            " chain forward {\n"
            "  type filter hook forward priority 0; policy accept;\n"
            "  iifname \"trunk0.110\" ip saddr 10.70.10.0/24 "
            "ip daddr 10.71.20.20 tcp dport 8081 counter drop\n"
            " }\n}\n"
        )
        sudocmd = ["sudo", "-n", "nsenter", "-t", hpid, "-n", "nft", "-f", "-"]
        cmd(*sudocmd, input_text=script)
        fw_installed = True
        print("S02_ACL_ROUTER=R-HQ PUERTO_8081=DENEGADO")
        curl(hq_users, "http://10.71.20.20:8081/", success=False)
        print("S02_ACL_HTTP_8081_DENEGADO=OK")
        for ns, url, name in tests:
            body = curl(ns, url)
            print(f"S02_ACL_HTTP_8080_{name}=PERMITIDO BODY={body}")
        print("========== CONTADOR ACL ==========")
        print(sudo("nsenter", "-t", hpid, "-n", "nft", "-a", "list",
                   "chain", "inet", TABLE, "forward").strip())
        if lan.host_state() != state["host"]:
            raise RuntimeError("Gestion administrativa alterada durante ACL")
        print("S02_HTTP_MULTISEDE=VALIDADO")
        print("S02_ACL_SERVICIO_REAL=VALIDADO")
    finally:
        if fw_installed:
            try:
                sudo("nsenter", "-t", hpid, "-n", "nft", "delete", "table", "inet", TABLE)
                print("S02_ACL_TEMPORAL_RETIRADA=SI")
            except Exception as e:
                print(f"S02_ACL_LIMPIEZA_ERROR={e}", file=sys.stderr)
        for process, log in reversed(servers):
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    process.wait(timeout=6)
                except Exception:
                    process.kill()
            log.close()
        print("S02_SERVIDORES_TEMPORALES_FINALIZADOS=SI")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"S02_HTTP_ACL_ERROR={type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
