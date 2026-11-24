#!/usr/bin/env python3
"""NETLAB360 B2: observación ICMP + rutas durante failover/restauración.
Red aislada: usa exclusivamente el orquestador versionado B2; limpieza finally.
NO modifica ens33, VMnet8, NetworkManager ni rutas del anfitrión.
"""
import csv
import datetime as dt
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import threading
import time

ROOT = Path.home() / "proyectos/netlab360"
ORCH = ROOT / "scripts/laboratorio/b2-dualwan-ospf.sh"
STATE = Path.home() / "netlab360-bootstrap/estado-b2-dualwan/.nl360-owner"
EVID = Path.home() / "netlab360-bootstrap/evidencias"
HQ = "nl360-b2-r-hq"
DST = "10.71.10.1"
SRC = "10.70.10.1"
STOP = threading.Event()
LOCK = threading.Lock()
PHASE = ["normal"]
ROWS = []
ERRORS = []
EVENTS = {}

def stamp():
    return dt.datetime.now().astimezone().isoformat(timespec="milliseconds")

def log(message):
    line = f"{stamp()} | {message}"
    with LOCK:
        print(line, flush=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

def run(cmd, timeout=150):
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)

def orchestrate(action, extra=None, timeout=150):
    cmd = ["bash", str(ORCH), action]
    if extra:
        cmd.append(extra)
    log(f"ACCION_INICIO={action}")
    r = run(cmd, timeout)
    interesting = ("RESULTADO_", "OSPF_DUAL_FULL:", "CONMUTACION_WAN_B:",
                   "RESTAURACION_WAN_P:", "RUTA_RESPALDO:", "RUTA_PRINCIPAL:",
                   "WAN_PRIMARIA:", "ERROR:", "LOG_LOCAL:")
    for ln in (r.stdout + "\n" + r.stderr).splitlines():
        if any(marker in ln for marker in interesting):
            log(ln.strip())
    log(f"ACCION_FIN={action} RC={r.returncode}")
    if r.returncode:
        log("DIAGNOSTICO_FINAL_COMANDO:\n" + "\n".join((r.stdout + r.stderr).splitlines()[-25:]))
    return r.returncode

def pid_hq():
    r = run(["sudo", "-n", "docker", "inspect", "-f", "{{.State.Pid}}", HQ], 4)
    if r.returncode or not r.stdout.strip().isdigit() or int(r.stdout) < 2:
        raise RuntimeError("PID del router HQ no valido")
    return r.stdout.strip()

def check_management():
    r = run(["ip", "-4", "-br", "address", "show", "ens33"], 3)
    g = run(["ip", "-4", "route", "show", "default"], 3)
    if "192.168.47.40/24" not in r.stdout or "default via 192.168.47.2 dev ens33" not in g.stdout:
        raise RuntimeError("IP o puerta de enlace de administración diferentes")
    log("HOST_PROTEGIDO=SI")

def current_phase():
    with LOCK:
        return PHASE[0]

# Registramos el tiempo monotónico de cada transición para asociar sondeos a su fase.
def set_phase(value):
    with LOCK:
        PHASE[0] = value
    EVENTS[value] = time.monotonic()
    log(f"FASE={value}")

# El monitor recoge ICMP y selección FIB durante el ciclo; no modifica el encaminamiento.
def monitor():
    try:
        pid = pid_hq()
        probe_no = 0
        while not STOP.is_set():
            probe_no += 1
            t0 = time.monotonic()
            phase = current_phase()
            route = run(["sudo", "-n", "nsenter", "-t", pid, "-n",
                         "ip", "-4", "route", "get", DST], 4)
            route_text = route.stdout.strip().replace("\n", " ")
            mdev = re.search(r"\bdev ([\w.-]+)", route_text)
            device = mdev.group(1) if mdev else "sin-ruta"
            ping = run(["sudo", "-n", "nsenter", "-t", pid, "-n", "ping",
                        "-n", "-I", SRC, "-c", "1", "-W", "1", DST], 4)
            ok = ping.returncode == 0 and "1 received" in ping.stdout
            match = re.search(r"time=([\d.]+) ms", ping.stdout)
            rtt = match.group(1) if match else ""
            item = [stamp(), round(t0 - START, 3), probe_no, phase,
                    device, 1 if ok else 0, rtt, ping.returncode]
            with LOCK:
                ROWS.append(item)
            log(f"SONDEO={probe_no} FASE={phase} RUTA={device} ICMP={'OK' if ok else 'FALLO'} RTT_MS={rtt or '-'}")
            STOP.wait(0.35)
    except Exception as ex:
        ERRORS.append(repr(ex))
        log(f"ERROR_MONITOR={ex!r}")

def summary():
    with CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fecha_local", "segundos_desde_inicio", "sondeo",
                         "fase", "interfaz_fib", "icmp_ok", "rtt_ms", "codigo_ping"])
        writer.writerows(ROWS)
    log(f"CSV_LOCAL={CSV}")
    all_ok = True
    for phase, expected in (("normal", "wan-p"), ("respaldo", "wan-b"), ("restaurada", "wan-p")):
        vals = [row for row in ROWS if row[3] == phase]
        ok = sum(int(row[5]) for row in vals)
        onroute = sum(1 for row in vals if row[4] == expected)
        loss = round(100 * (len(vals) - ok) / len(vals), 1) if vals else None
        log(f"RESUMEN_{phase}: muestras={len(vals)} recibidas={ok} perdidas={len(vals)-ok} porcentaje_perdida={loss}% ruta_esperada={onroute}/{len(vals)}")
        if len(vals) < 3 or not ok or not onroute:
            all_ok = False
    for phase in ("cambio_respaldo", "cambio_principal"):
        vals = [row for row in ROWS if row[3] == phase]
        ok = sum(int(row[5]) for row in vals)
        log(f"TRANSICION_{phase}: muestras={len(vals)} exitosas={ok} fallidas={len(vals)-ok}")
        expected = "wan-b" if phase == "cambio_respaldo" else "wan-p"
        matching = [row for row in vals if row[4] == expected]
        if matching:
            elapsed = round(matching[0][1] - (EVENTS[phase] - START), 3)
            log(f"PRIMER_SONDEO_FIB_{phase}: {elapsed}s desde inicio de accion; resolucion limitada por intervalo y ejecucion de comandos")
        else:
            log(f"PRIMER_SONDEO_FIB_{phase}: NO OBSERVADO en transicion")
    log(f"MUESTRAS_TOTALES={len(ROWS)} ERRORES_MONITOR={len(ERRORS)}")
    return all_ok and not ERRORS

def main():
    if len(sys.argv) != 2 or sys.argv[1] != "--snapshot-confirmado":
        print(f"Uso: python3 {sys.argv[0]} --snapshot-confirmado")
        return 2
    if os.geteuid() == 0 or socket.gethostname() != "netlab360-lab":
        print("ERROR: ejecutar desde usuario habitual de netlab360-lab")
        return 2
    now = dt.datetime.now().astimezone()
    if now.date() == dt.date(2026, 10, 13) and (now.hour, now.minute) >= (11, 53):
        print("ERROR: no iniciar una prueba nueva después de 11:53; cierre desde las 12:00.")
        return 2
    EVID.mkdir(parents=True, exist_ok=True)
    LOG.touch(exist_ok=False)
    log("========== B2 MEDICION CONTINUA / TRAFICO ICMP ==========")
    log("NOTA: se observan muestras discretas; retardo de primer sondeo no es tiempo exacto de convergencia OSPF.")
    check_management()
    if run(["sudo", "-v"], 20).returncode:
        log("ERROR: sudo no disponible")
        return 2
    if orchestrate("precheck") != 0:
        log("RESULTADO_MEDICION=3 PRECHECK_FALLIDO")
        return 3
    started = False
    thread = None
    outcome = 4
    try:
        if orchestrate("up", "--snapshot-confirmado") != 0:
            log("RESULTADO_MEDICION=4 DESPLIEGUE_FALLIDO")
            return 4
        started = True
        STARTER = time.monotonic()
        set_phase("normal")
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        time.sleep(5)
        set_phase("cambio_respaldo")
        if orchestrate("fail") != 0:
            log("ERROR: fail no superado; se intentará restauración y cleanup")
            orchestrate("restore")
            return 5
        set_phase("respaldo")
        time.sleep(6)
        set_phase("cambio_principal")
        if orchestrate("restore") != 0:
            log("ERROR: restore no superado; cleanup obligatorio")
            return 6
        set_phase("restaurada")
        time.sleep(6)
        STOP.set()
        thread.join(timeout=6)
        if thread.is_alive():
            log("ERROR: monitor no terminó")
            outcome = 7
        else:
            outcome = 0 if summary() else 7
        return outcome
    finally:
        STOP.set()
        if thread is not None and thread.is_alive():
            thread.join(timeout=6)
        if STATE.is_file() and STATE.read_text().strip() == "netlab360-b2-dualwan":
            rc = orchestrate("down")
            log(f"LIMPIEZA_FINAL={'OK' if rc == 0 else 'ERROR'}")
            if rc != 0:
                raise RuntimeError('Se requiere revisar la limpieza B2 antes del apagado')
        elif STATE.exists():
            raise RuntimeError("Estado B2 no reconocido; inspeccionar sin borrar recursos")
        else:
            log("LIMPIEZA_FINAL: orquestador sin marcador activo")
        check_management()
        residual = run(["sudo", "-n", "docker", "ps", "-a",
                        "--filter", "name=nl360-b2-", "--format", "{{.Names}}"], 5)
        if residual.returncode != 0 or residual.stdout.strip():
            raise RuntimeError("No se pudo verificar limpieza de contenedores B2")
        log("CONTENEDORES_B2_RESIDUALES=0")
        log("========== FIN ENSAYO ==========")

if __name__ == "__main__":
    def stop_signal(signum, frame):
        raise KeyboardInterrupt(f"Senal {signum}")
    signal.signal(signal.SIGTERM, stop_signal)
    EVID.mkdir(parents=True, exist_ok=True)
    LABEL = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    LOG = EVID / f"17-b2-convergencia-{LABEL}.log"
    CSV = EVID / f"17-b2-convergencia-{LABEL}.csv"
    START = time.monotonic()
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        STOP.set()
        log("INTERRUMPIDO_POR_USUARIO: comprobar limpieza via 'down' si quedaron recursos")
        sys.exit(130)
    except Exception as ex:
        STOP.set()
        log(f"ERROR_FATAL={ex!r}; ejecutar inspeccion y down si hay marcador activo")
        sys.exit(8)
