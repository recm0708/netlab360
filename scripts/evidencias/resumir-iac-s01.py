#!/usr/bin/env python3
"""Evidencias resumidas de IaC S01 a partir de logs reales: NO reejecuta apply.
Cada bloque tiene limites precisos INICIO/FIN CAPTURA; evita pantallazos
truncados y no muestra terraform.tfstate ni credenciales.
Uso: python3 scripts/evidencias/resumir-iac-s01.py 01|03|04|05|06
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = Path.home() / "netlab360-bootstrap/iac/s01"
NOMBRES = {
    "01": "Precheck_IPAM_Herramientas",
    "03": "Tofu_Apply_Manifest",
    "04": "Ansible_Render_Candidato_FRR",
    "05": "Compliance_FRR",
    "06": "Idempotencia",
}


def ejecutar(*args):
    p = subprocess.run(list(args), text=True, capture_output=True, cwd=ROOT)
    if p.returncode:
        raise ValueError("Comando de lectura fallido " + " ".join(args) + ": " + p.stderr.strip())
    return p.stdout.strip()


def log(filename):
    path = ART / filename
    if not path.is_file():
        raise ValueError(f"Falta log original {path}; no reconstruir artificialmente resultados")
    return path.read_text(encoding="utf-8")


def resumen01():
    print("COMANDOS SOLO LECTURA: validar-ipam.py, tofu version, ansible --version, ip, git status")
    print(ejecutar("python3", "scripts/validacion/validar-ipam.py", "inventario/ipam/topologia-b1.yaml"))
    print("TOFU:", ejecutar("tofu", "version").splitlines()[0])
    print("ANSIBLE:", ejecutar("ansible", "--version").splitlines()[0])
    direccion = ejecutar("ip", "-4", "-br", "address", "show", "ens33")
    ruta = ejecutar("ip", "-4", "route", "show", "default")
    assert "192.168.47.40/24" in direccion and "default via 192.168.47.2 dev ens33" in ruta
    print("GESTION_IP:", direccion)
    print("GESTION_RUTA:", ruta)
    print("GIT:", ejecutar("git", "status", "--short", "--branch").replace("\n", " "))
    print("IAC_PRECHECK_RESUMEN=OK")


def resumen03():
    texto = log("02-tofu-apply.log")
    marcador = "Apply complete! Resources: 5 added, 0 changed, 0 destroyed."
    assert marcador in texto, "Apply no comprobado en log"
    creados = [line for line in texto.splitlines() if ": Creation complete after " in line]
    assert len(creados) == 5, f"5 recursos esperados, log muestra {len(creados)}"
    archivo = ART / "manifest.json"
    manifest = json.loads(archivo.read_text(encoding="utf-8"))
    sot = ROOT / "inventario/ipam/topologia-b1.yaml"
    assert manifest["inventory_sha256"] == hashlib.sha256(sot.read_bytes()).hexdigest()
    assert set(manifest["sites"]) == {"HQ", "S1"}
    assert manifest["s2_reserved"] is True and len(manifest["wan_links"]) == 2
    mgmt = manifest["management_guard"]
    assert mgmt["locked"] is True and mgmt["interface"] == "ens33"
    assert mgmt["host_ip"] == "192.168.47.40" and mgmt["gateway"] == "192.168.47.2"
    print("FUENTE_HISTORICA:", ART / "02-tofu-apply.log")
    for line in creados:
        print(line)
    print(marcador)
    print("MANIFIESTO_ORIGINAL:", archivo)
    print("IPAM_SHA256_VINCULADO=SI")
    print("SITIOS_IAC=HQ,S1 | S2=RESERVADA | WAN=2")
    print("ENS33_VMNET8_GUARDA=SI")
    print("IAC_APPLY_RESUMEN=OK (lectura historica, SIN ejecutar apply nuevamente)")


def recap(texto, esperado):
    lineas = [line.strip() for line in texto.splitlines() if line.lstrip().startswith("localhost") and "changed=" in line]
    assert len(lineas) == 1, f"Se esperaba un recap de Ansible, encontrados {len(lineas)}"
    linea = lineas[0]
    assert re.search(rf"\bchanged={esperado}\b", linea), f"Ansible changed distinto de {esperado}"
    assert re.search(r"\bfailed=0\b", linea) and re.search(r"\bunreachable=0\b", linea)
    return linea


def resumen04():
    texto = log("03-ansible-primera.log")
    print("FUENTE_HISTORICA:", ART / "03-ansible-primera.log")
    for line in texto.splitlines():
        if ("PLAY [" in line or "TASK [" in line or
                "IAC_MANIFIESTO_VALIDADO=SI" in line or
                "changed: [localhost]" in line):
            print(line.strip())
    print("PLAY RECAP:", recap(texto, 2))
    for router in ("R-HQ", "R-S1"):
        archivo = ART / "rendered" / f"{router}.frr.conf"
        assert archivo.is_file() and archivo.stat().st_size > 0
        print(f"FRR_GENERADO={router} | bytes={archivo.stat().st_size}")
    print("IAC_ANSIBLE_RENDER_HISTORICO=OK (SIN reejecutar playbook)")


def resumen05():
    print("COMANDO: python3 scripts/validacion/validar-iac-frr.py " + str(ART / "rendered"))
    print(ejecutar("python3", "scripts/validacion/validar-iac-frr.py", str(ART / "rendered")))
    print("RESULTADO_COMPLIANCE_IAC=0")


def resumen06():
    ans = log("04-ansible-idempotencia.log")
    tf = log("05-tofu-idempotencia.log")
    linea = recap(ans, 0)
    assert "No changes. Your infrastructure matches the configuration." in tf
    print("FUENTE_HISTORICA_ANSIBLE:", ART / "04-ansible-idempotencia.log")
    print("SEGUNDA_EJECUCION_ANSIBLE:", linea)
    print("FUENTE_HISTORICA_TOFU:", ART / "05-tofu-idempotencia.log")
    print("OPEN_TOFU:", "No changes. Your infrastructure matches the configuration.")
    print("NOTA=logs originales sin reejecutar tofu plan/apply ni ansible")
    print("IAC_IDEMPOTENCIA_RESUMEN=OK")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in NOMBRES:
        sys.exit("Uso: python3 scripts/evidencias/resumir-iac-s01.py 01|03|04|05|06")
    n = sys.argv[1]
    marca = f"IAC_S01_{n}_{NOMBRES[n]}"
    print(f"========== INICIO CAPTURA {marca} ==========", flush=True)
    try:
        {"01": resumen01, "03": resumen03, "04": resumen04,
         "05": resumen05, "06": resumen06}[n]()
    except (AssertionError, ValueError, OSError, KeyError, json.JSONDecodeError) as e:
        print(f"EVIDENCIA_NO_VALIDADA={e}", file=sys.stderr)
        sys.exit(1)
    print(f"========== FIN CAPTURA {marca} ==========", flush=True)


if __name__ == "__main__":
    main()
