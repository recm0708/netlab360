#!/usr/bin/env python3
"""NETLAB360 S05: evidencia real de VLAN420 aislada sin timeout externo de 10s.

Solo lectura: NO crea, elimina, reinicia ni modifica redes/contenedores.
Captura 60 se emite SOLO si los 3 resultados se validan contra ping real.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import subprocess
import sys

LAB = Path(__file__).resolve().parents[1] / "laboratorio/s05-sdn-ovs-faucet-aislado.py"
spec = importlib.util.spec_from_file_location("s05_sdn_lab_evidencia", LAB)
assert spec and spec.loader
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

SUMMARY = re.compile(\n    r"(?m)^\s*(\d+)\s+packets transmitted,\s*(\d+)\s+received,"\n    r"(?:\s*\+\d+\s+errors,)?\s*([\d.]+)%\s+packet loss"\n)


def measure(site: str, target: str, allowed: bool) -> None:
    """Un deadline interno -w y otro de Python: 124 NO prueba denegación."""
    if site not in ("a", "b", "c"):
        raise ValueError("Namespace fuera del dominio SDN")
    if target not in ("198.18.41.11", "198.18.41.12", "198.18.41.13"):
        raise ValueError("Objetivo no pertenece al laboratorio SDN")
    args = ["sudo", "-n", "ip", "netns", "exec", lab.NS[site],
            "ping", "-n", "-c", "2", "-i", "0.3", "-W", "2", "-w", "8", target]
    print("COMANDO=" + " ".join(args), flush=True)
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Timeout de ejecución {site}->{target}; NO aceptar bloqueo") from exc
    output = result.stdout + "\n" + result.stderr
    found = SUMMARY.search(output)
    if not found:
        raise RuntimeError(f"Faltan estadísticas ICMP {site}->{target}; RC={result.returncode}: {output[-300:]}")
    sent, received = int(found[1]), int(found[2])
    loss = float(found[3])
    print(f"RESUMEN={sent} transmitidos, {received} recibidos, {loss:g}% pérdida; RC={result.returncode}",
          flush=True)
    # iputils puede volver a transmitir ARP/ICMP hasta el deadline de -w
    # si el kernel genera Destination Host Unreachable. No falsear fallo:
    # comprobar RC de ping, 0 respuestas y 100% perdida, no sent == 2.
    if sent < 2 or sent > 32:
        raise RuntimeError(f"Cantidad de intentos fuera de rango {site}->{target}: {sent}")
    if allowed:
        if result.returncode != 0 or sent != 2 or received != 2 or loss != 0:
            raise RuntimeError(f"El tráfico autorizado {site}->{target} no fue entregado")
        print(f"S05_SDN_PRUEBA_{site.upper()}_{target}=PERMITIDO_RC_0", flush=True)
    else:
        if result.returncode != 1 or received != 0 or loss != 100:
            raise RuntimeError(f"Aislamiento NO acreditado {site}->{target}; RC={result.returncode}")
        print(f"S05_SDN_PRUEBA_{site.upper()}_{target}=DENEGADO_RC_1", flush=True)


def main() -> None:
    state = lab.state_read()
    if state.get("status") != "active":
        raise RuntimeError("SDN todavía no está activo, detener")
    if not lab.owned_bridge() or not lab.owned_controller():
        raise RuntimeError("Propiedad de OVS/Faucet no válida")
    print("========== 733 POSTCHECK SDN REAL ==========", flush=True)
    lab.status()
    print("========== 734 EVIDENCIA RECUPERADA VLAN420 ==========", flush=True)
    print("========== INICIO_CAPTURA_S05_60_SDN_VLAN420_AISLADA ==========", flush=True)
    measure("a", "198.18.41.12", allowed=True)
    measure("a", "198.18.41.13", allowed=False)
    measure("c", "198.18.41.11", allowed=False)
    print("S05_SDN_VLAN_410=PERMITIDA", flush=True)
    print("S05_SDN_VLAN_420=AISLADA", flush=True)
    print("========== FIN_CAPTURA_S05_60_SDN_VLAN420_AISLADA ==========", flush=True)
    print("========== 735 POSTCHECK FINAL ==========", flush=True)
    lab.status()
    print("S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"S05_SDN_CAPTURA60_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
