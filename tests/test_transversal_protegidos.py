"""Verificamos la instalación protegida sin intervenir el sistema."""

import csv
import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "operacion/instalar_protegidos.py"

spec = importlib.util.spec_from_file_location(
    "netlab360_instalar_protegidos",
    SOURCE,
)

installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class ProtectedInstallationTests(unittest.TestCase):
    """Validamos el alcance cerrado y las precondiciones."""

    def test_complete_manifest(self):
        rows = installer.read_manifest(ROOT)

        self.assertEqual(len(rows), 13)
        self.assertEqual(len(installer.STATE_NAMES), 8)

        self.assertEqual(
            {row["fuente"] for row in rows},
            set(installer.ALLOWED),
        )

    def test_destination_matches_source(self):
        for row in installer.read_manifest(ROOT):
            self.assertEqual(
                row["destino"],
                str(
                    installer.LIBEXEC /
                    installer.ALLOWED[row["fuente"]]
                ),
            )

    def test_plan_never_installs(self):
        buffer = io.StringIO()

        with patch.object(installer, "install_new") as apply:
            with redirect_stdout(buffer):
                installer.main(["--plan"])

            apply.assert_not_called()

        self.assertIn(
            "INSTALACION_EJECUTADA=NO",
            buffer.getvalue(),
        )

    def test_apply_requires_confirmations(self):
        with patch.object(installer, "install_new") as apply:
            with self.assertRaises(SystemExit):
                installer.main(["--apply"])

            apply.assert_not_called()

    def test_non_root_rejected(self):
        with patch.object(
            installer.os, "geteuid", return_value=1000
        ):
            with self.assertRaisesRegex(
                ValueError, "ROOT_REQUIRED"
            ):
                installer.install_new([])

    def test_existing_resource_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                ValueError, "EXISTING_RESOURCE"
            ):
                installer.check_absent([Path(directory)])

    def test_broken_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "link"

            path.symlink_to(Path(directory) / "absent")

            with self.assertRaisesRegex(
                ValueError, "EXISTING_RESOURCE"
            ):
                installer.check_absent([path])

    def test_path_traversal_rejected(self):
        for source in ("../outside.py", "/etc/passwd"):
            with self.assertRaisesRegex(
                ValueError, "INVALID_SOURCE_PATH"
            ):
                installer.source_path(ROOT, source)

    def test_manifest_rejects_wrong_destination(self):
        rows = installer.read_manifest(ROOT)

        rows[0]["destino"] = "/usr/local/libexec/other"

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / installer.MANIFEST

            manifest.parent.mkdir(parents=True)

            with manifest.open("w", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "fuente",
                        "destino",
                        "propietario",
                        "grupo",
                        "modo",
                    ],
                    delimiter="\t",
                )

                writer.writeheader()
                writer.writerows(rows)

            with self.assertRaisesRegex(
                ValueError,
                "INVALID_MANIFEST_DESTINATION"
            ):
                installer.read_manifest(root)

    def test_clean_destination_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            installer.check_absent([
                Path(directory) / "new-file",
            ])

if __name__ == "__main__":
    unittest.main()
