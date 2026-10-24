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


def wait_http_ready(process, namespace: str, ipaddr: str, port: int, logfile: Path) -> None:
    """No declarar servicio operativo hasta HTTP de loopback local en VLAN."""
    url = f"http://{ipaddr}:{port}/"
    for attempt in range(1, 26):
        if process.poll() is not None:
            details = logfile.read_text(errors="replace")[-1200:] if logfile.exists() else ""
            raise RuntimeError(f"Servidor {namespace}:{port} terminó prematuramente: {details}")
        try:
            body = curl(namespace, url)
            if "NETLAB360_S02_HTTP_" in body:
                print(f"S02_SERVIDOR_ESCUCHANDO={namespace}:{ipaddr}:{port} INTENTO={attempt}", flush=True)
                return
        except RuntimeError:
            time.sleep(0.2)
    details = logfile.read_text(errors="replace")[-1200:] if logfile.exists() else ""
    raise RuntimeError(f"Servidor no escuchó {namespace}:{port} después de 25 intentos: {details}")


def cleanup_http_processes(servers) -> list[str]:
    """Terminar solo procesos de esta prueba, nunca el grupo SSH de usuario."""
    errors = []
    for process, log in reversed(servers):
        try:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        except Exception as exc:
            errors.append(f"Proceso controlador HTTP: {exc}")
        finally:
            log.close()
    # Un sudo que fork+exec deja a veces el python hijo activo. Buscar
    # únicamente HTTP con directorios específicos de esta prueba en netns.
    for site, vlan, ipaddr, port in SERVICES:
        source_ns = f"nl360-s02-h-{site.lower()}-{vlan}"
        marker = str(BASE / f"s02-http-{site.lower()}-{port}").encode()
        for _ in range(3):
            pids = sudo("ip", "netns", "pids", source_ns, allow=True).split()
            targets = []
            for pid in pids:
                if not pid.isdigit():
                    continue
                # Los servidores se iniciaron con sudo y pueden ser root.
                # No depender de permisos de lectura /proc del usuario SSH.
                cmdline = sudo("ps", "-p", pid, "-o", "args=", allow=True)
                comm = sudo("ps", "-p", pid, "-o", "comm=", allow=True).strip()
                if comm.startswith("python") and "http.server" in cmdline and marker.decode() in cmdline:
                    targets.append(pid)
            if not targets:
                break
            for pid in targets:
                sudo("kill", "-TERM", pid, allow=True)
            time.sleep(0.2)
        else:
            errors.append(f"Servidores persistentes en {source_ns}:{port}")
    return errors


def main() -> None:
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal, sudo -v previamente")
    # Ejecutar SIN nueva sesión POSIX: sudo por defecto asocia la
    # credencial temporal al TTY/sesión. setsid aislaba los hijos de sudo -v.
    sudo("-v")
    print("S02_SUDO_NO_INTERACTIVO=OK")
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
    acl_attempted = False
    try:
        print("========== HTTP S02 SERVICIOS ==========", flush=True)
        for site, vlan, ipaddr, port in SERVICES:
            directory = BASE / f"s02-http-{site.lower()}-{port}"
            directory.mkdir(parents=True, exist_ok=True)
            (directory/"index.html").write_text(
                f"NETLAB360_S02_HTTP_{site}_{port}_OK\n", encoding="utf-8"
            )
            source_ns = f"nl360-s02-h-{site.lower()}-{vlan}"
            logpath = BASE / f"S02_HTTP_Server_{site}_{port}.log"
            log = open(logpath, "ab")
            process = subprocess.Popen(
                ["sudo", "-n", "ip", "netns", "exec", source_ns,
                 "python3", "-m", "http.server", str(port),
                 "--bind", ipaddr, "--directory", str(directory)],
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=False
            )
            servers.append((process, log))
            print(f"S02_SERVIDOR_PROCESO_LANZADO={site}:{ipaddr}:{port}", flush=True)
            wait_http_ready(process, source_ns, ipaddr, port, logpath)
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
        acl_attempted = True
        cmd(*sudocmd, input_text=script)
        fw_installed = True
        print("S02_ACL_ROUTER=R-HQ PUERTO_8081=DENEGADO")
        curl(hq_users, "http://10.71.20.20:8081/", success=False)
        print("S02_ACL_HTTP_8081_DENEGADO=OK")
        # El mismo servicio debe continuar aceptando conexiones desde S1:
        alive_after = curl(s1_users, "http://10.71.20.20:8081/")
        print(f"S02_SERVICIO_8081_POSTACL_DESDE_S1=ACTIVO BODY={alive_after}")
        for ns, url, name in tests:
            body = curl(ns, url)
            print(f"S02_ACL_HTTP_8080_{name}=PERMITIDO BODY={body}")
        print("========== CONTADOR ACL ==========")
        counter = sudo("nsenter", "-t", hpid, "-n", "nft", "-a", "list",
                       "chain", "inet", TABLE, "forward")
        print(counter.strip())
        count_match = re.search(r"counter packets\s+(\d+)\s+bytes", counter)
        if not count_match or int(count_match.group(1)) < 1:
            raise RuntimeError("ACL no contabilizó tráfico bloqueado")
        print(f"S02_ACL_PAQUETES_BLOQUEADOS={count_match.group(1)}")
        if lan.host_state() != state["host"]:
            raise RuntimeError("Gestion administrativa alterada durante ACL")
        print("S02_HTTP_MULTISEDE=VALIDADO")
        print("S02_ACL_SERVICIO_REAL=VALIDADO")
    finally:
        cleanup_errors = []
        if fw_installed or acl_attempted:
            try:
                # Borrar solo nuestra tabla, sin vaciar otras reglas del router.
                sudo("nsenter", "-t", hpid, "-n", "nft", "delete", "table", "inet", TABLE)
                print("S02_ACL_TEMPORAL_RETIRADA=SI")
            except Exception as e:
                cleanup_errors.append(f"ACL: {e}")
                print(f"S02_ACL_LIMPIEZA_ERROR={e}", file=sys.stderr)
        cleanup_errors.extend(cleanup_http_processes(servers))
        if cleanup_errors:
            raise RuntimeError("Limpieza HTTP/ACL requiere comprobacion: " + "; ".join(cleanup_errors))
        print("S02_SERVIDORES_TEMPORALES_FINALIZADOS=SI")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"S02_HTTP_ACL_ERROR={type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
