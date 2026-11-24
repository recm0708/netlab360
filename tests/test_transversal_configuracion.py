"""Pruebas offline de los manifiestos de configuración NETLAB360."""

import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OP = ROOT / "operacion"

spec = importlib.util.spec_from_file_location(
    "netlab360_configuracion",
    OP / "generar_configuracion.py",
)

generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class ConfigurationTests(unittest.TestCase):
    """Comprobamos fuentes, destinos y aislamiento del generador."""

    def test_protected_manifest(self):
        entries = generator.protected_entries(ROOT)

        self.assertEqual(len(entries), 13)

        self.assertEqual(
            len({row["destino"] for row in entries}),
            13,
        )

    def test_protected_source_paths(self):
        for relative in ("../archivo.py", "/etc/passwd"):
            with self.assertRaises(ValueError):
                generator.safe_source(ROOT, relative)

    def test_existing_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                ValueError, "OUTPUT_EXISTS"
            ):
                generator.prepare(ROOT, Path(directory))

    def test_relative_output_rejected(self):
        with self.assertRaisesRegex(
            ValueError, "ABSOLUTE_OUTPUT_REQUIRED"
        ):
            generator.prepare(ROOT, Path("configuracion"))

    def test_repository_output_rejected(self):
        target = ROOT / ".netlab360-test-output"

        with self.assertRaisesRegex(
            ValueError, "OUTPUT_INSIDE_REPOSITORY"
        ):
            generator.prepare(ROOT, target)

    def test_prometheus_local_only(self):
        unit = (
            OP / "plantillas/netlab360-s04-prometheus.service"
        ).read_text()

        self.assertIn(
            "--web.listen-address=127.0.0.1:9091",
            unit,
        )

        self.assertIn("NoNewPrivileges=yes", unit)
        self.assertIn("ProtectSystem=strict", unit)
        self.assertNotIn("[Install]", unit)

    def test_observer_rule_is_fixed(self):
        text = (
            OP / "plantillas/netlab360-observer"
        ).read_text()

        active = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
            and not line.lstrip().startswith("#")
        ]

        self.assertEqual(
            active,
            [
                "rc-aa-ec ALL=(root) NOPASSWD: "
                "/usr/local/libexec/netlab360-observer snapshot"
            ],
        )

    def test_generate_new_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle"

            generator.prepare(ROOT, output)

            self.assertEqual(
                len(list((output / "frr/rendered").glob("*.conf"))),
                3,
            )

            self.assertEqual(
                len(list((output / "systemd").glob("*.service"))),
                7,
            )

            self.assertFalse(
                list(output.rglob("router-pin.json"))
            )

            self.assertFalse(
                list(output.rglob("*.sqlite3"))
            )


if __name__ == "__main__":
    unittest.main()
