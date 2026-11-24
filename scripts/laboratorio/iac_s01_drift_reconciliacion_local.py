#!/usr/bin/env python3
"""Demostracion controlada de drift y reconciliacion Ansible sobre COPIAS FRR.

NO toca contenedores, interfaces, OpenTofu state ni configuraciones versionadas.
El directorio de trabajo es exclusivo bajo ~/netlab360-bootstrap/iac/s01/.
Una ejecucion por directorio; ante error NO borrar manualmente sin diagnostico.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = Path.home() / "netlab360-bootstrap/iac/s01"
ORIGINAL = ART / "rendered"
DEST = ART / "drift-demo-2026-10-13"
VALIDADOR = ROOT / "scripts/validacion/validar-iac-frr.py"
PLAY = ROOT / "ansible/s01/render-frr.yml"
MANIFEST = ART / "manifest.json"


def run(args, check=True):
    proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError("Fallo comando " + " ".join(map(str,args)) +
                           "\nSTDOUT:\n" + proc.stdout + "\nSTDERR:\n" + proc.stderr)
    return proc


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resumen_ansible(texto, esperado):
    recaps = [ln.strip() for ln in texto.splitlines() if
              ln.strip().startswith("localhost") and "changed=" in ln]
    assert len(recaps) == 1, "Recap no encontrado"
    recap = recaps[0]
    assert re.search(rf"\bchanged={esperado}\b", recap) and re.search(r"\bfailed=0\b", recap)
    return recap


def admin():
    addr = run(["ip", "-4", "-br", "address", "show", "ens33"]).stdout
    route = run(["ip", "-4", "route", "show", "default"]).stdout
    assert "192.168.47.40/24" in addr
    assert "default via 192.168.47.2 dev ens33" in route
    return addr, route


def main():
    assert sys.argv[1:] == [], "Uso: python3 scripts/laboratorio/iac-s01-drift-reconciliacion-local.py"
    before = admin()
    assert ORIGINAL.is_dir() and MANIFEST.is_file()
    assert not DEST.exists(), f"Directorio ya existe: {DEST}. No repetir sin revisar."
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["topology_status"] == "candidate_only"
    assert set(data["sites"]) == {"HQ","S1"} and data["s2_reserved"] is True
    for router in ("R-HQ","R-S1"):
        assert (ORIGINAL / f"{router}.frr.conf").is_file()
    ok = run(["python3",str(VALIDADOR),str(ORIGINAL)])
    assert "IAC_CONFIG_FIEL_A_B2=SI" in ok.stdout
    DEST.mkdir(mode=0o700)
    for router in ("R-HQ","R-S1"):
        shutil.copy2(ORIGINAL / f"{router}.frr.conf", DEST / f"{router}.frr.conf")

    print("========== INICIO CAPTURA IAC_S01_08_Drift_Detectado ==========", flush=True)
    print("FUENTE=Copias de dos configuraciones FRR generadas por Ansible")
    print("RUTA_EXCLUSIVA=" + str(DEST))
    print("BASELINE_COMPLIANCE=OK (ambos routers)")
    hq = DEST / "R-HQ.frr.conf"
    before_text = hq.read_text(encoding="utf-8")
    antiguo = "\n ip ospf cost 10\n"
    assert before_text.count(antiguo) == 1, "No se puede identificar costo unico"
    hq.write_text(before_text.replace(antiguo, "\n ip ospf cost 50\n", 1), encoding="utf-8")
    hq.chmod(0o600)
    print("DRIFT_CONTROLADO=R-HQ WAN-P OSPF cost 10 -> 50 (SOLO COPIA)")
    check = run(["python3",str(VALIDADOR),str(DEST)], check=False)
    assert check.returncode == 1, "El verificador NO detecto drift"
    assert "NON_COMPLIANT" in check.stderr, "Falta etiqueta NON_COMPLIANT"
    print("DETECTOR_RESULTADO=NON_COMPLIANT | EXIT=1 (esperado)")
    print("S1_NO_MODIFICADA=SI")
    print("========== FIN CAPTURA IAC_S01_08_Drift_Detectado ==========", flush=True)

    print("========== INICIO CAPTURA IAC_S01_09_Reconciliacion ==========", flush=True)
    opts = ["ansible-playbook", "-i", "localhost,", "-c", "local",
            str(PLAY), "-e", json.dumps({
                "manifest_path":str(MANIFEST), "output_dir":str(DEST)
            })]
    first = run(opts)
    print("ANSIBLE_RECONCILIACION:", resumen_ansible(first.stdout, 1))
    post = run(["python3",str(VALIDADOR),str(DEST)])
    print(post.stdout.strip())
    for router in ("R-HQ","R-S1"):
        name = f"{router}.frr.conf"
        assert sha(DEST/name) == sha(ORIGINAL/name), f"Contenido distinto tras reconciliar: {name}"
    second = run(opts)
    print("ANSIBLE_IDEMPOTENCIA:", resumen_ansible(second.stdout, 0))
    assert admin() == before, "Se altero gestion VMnet8 durante la prueba"
    print("HASHES_IGUALES_A_CONFIG_ORIGINAL=SI")
    print("RED_GESTION_INTACTA=SI")
    print("CONTENEDORES_INTERFACES_NO_MODIFICADOS=SI (solo archivos)")
    print("RECONCILIACION_CANDIDATA=OK")
    print("NOTA=Esta es reconciliacion de ARCHIVOS CANDIDATOS, NO de router vivo")
    print("========== FIN CAPTURA IAC_S01_09_Reconciliacion ==========", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, AssertionError, ValueError, OSError, KeyError, IndexError) as exc:
        print("RESULTADO_DRIFT_LOCAL=ERROR: " + str(exc), file=sys.stderr)
        sys.exit(1)
