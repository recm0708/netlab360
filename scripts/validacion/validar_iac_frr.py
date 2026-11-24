#!/usr/bin/env python3
"""Validar las candidatas FRR de Ansible contra la configuracion B2-L3 aprobada.
Compara comandos FRR ignorando comentarios, espacios vacios y descripciones;
no arranca redes ni modifica archivos. Requiere dos argumentos: ruta de salida.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def comandos(path: Path) -> list[str]:
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("!") or stripped.startswith("description "):
            continue
        result.append(stripped)
    return result


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Uso: python3 scripts/validacion/validar-iac-frr.py DIRECTORIO_GENERADO")
    target = Path(sys.argv[1]).resolve(strict=True)
    if target == ROOT or ROOT in target.parents:
        raise ValueError("Las configuraciones generadas deben estar FUERA del repositorio")
    for router in ("R-HQ", "R-S1"):
        candidate = target / (router + ".frr.conf")
        baseline = ROOT / "topologias" / "b2-frr" / "configs" / (router + ".frr.conf")
        assert candidate.is_file(), f"Candidato ausente: {router}"
        current, previous = comandos(candidate), comandos(baseline)
        if current != previous:
            import difflib
            print("\n".join(difflib.unified_diff(previous, current, fromfile=str(baseline),
                                                 tofile=str(candidate), lineterm="")), file=sys.stderr)
            raise ValueError(f"FRR_CONFIG_COMPLIANCE_{router}=NON_COMPLIANT")
        print(f"FRR_CONFIG_COMPLIANCE_{router}=COMPLIANT")
    print("IAC_CONFIG_FIEL_A_B2=SI")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, AssertionError, OSError) as exc:
        print(f"IAC_CONFIG_VALIDACION=ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
