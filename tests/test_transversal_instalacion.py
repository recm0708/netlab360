"""Pruebas offline de la interfaz de instalación NETLAB360."""

import csv
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
OP = ROOT / "operacion"
INSTALL = OP / "instalar.sh"


class InstallationTests(unittest.TestCase):
    """Validamos los manifiestos y controles sin instalar paquetes."""

    def command(self, *args):
        return subprocess.run(
            ["bash", str(INSTALL), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_shell_syntax(self):
        for file in (INSTALL, OP / "verificar.sh"):
            result = subprocess.run(
                ["bash", "-n", str(file)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_help(self):
        result = self.command("--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("--plan", result.stdout)
        self.assertIn("--confirm-clean-host", result.stdout)

    def test_apply_requires_confirmation(self):
        result = self.command("--apply")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Se requiere --confirm-clean-host",
            result.stderr,
        )

    def test_unknown_argument_is_rejected(self):
        result = self.command("--invalid")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Argumento no reconocido",
            result.stderr,
        )

    def test_system_package_manifest(self):
        path = OP / "perfiles/ubuntu-26.04-amd64/paquetes.tsv"

        with path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))

        names = [row["paquete"] for row in rows]

        self.assertEqual(len(names), len(set(names)))

        self.assertTrue({
            "docker-ce",
            "docker-compose-plugin",
            "tofu",
            "ansible-core",
            "python3-venv",
            "openvswitch-switch",
        }.issubset(names))

        for row in rows:
            self.assertRegex(
                row["paquete"],
                r"^[a-z0-9][a-z0-9+.-]*$",
            )

            self.assertIn(
                row["categoria"],
                {"base", "externo", "opcional"},
            )

    def test_oci_manifest(self):
        with (OP / "imagenes.tsv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))

        self.assertEqual(
            {row["componente"] for row in rows},
            {"frr", "faucet", "prometheus"},
        )

        for row in rows:
            self.assertEqual(row["arquitectura"], "amd64")

            self.assertIsNotNone(re.fullmatch(
                r"[a-z0-9./_-]+@sha256:[0-9a-f]{64}",
                row["referencia_inmutable"],
            ))

    def test_scientific_requirements_are_pinned(self):
        path = ROOT / "requirements-cientifico.txt"

        lines = [
            line.strip()
            for line in path.read_text().splitlines()
            if line.strip()
            and not line.lstrip().startswith("#")
        ]

        self.assertGreaterEqual(len(lines), 69)

        for line in lines:
            self.assertRegex(
                line,
                r"^[a-z0-9-]+==[a-zA-Z0-9.+!_-]+$",
            )


if __name__ == "__main__":
    unittest.main()
