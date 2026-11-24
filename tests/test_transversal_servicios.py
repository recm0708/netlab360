"""Validamos el instalador sin modificar systemd ni sudoers."""

from contextlib import redirect_stdout, redirect_stderr
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "operacion"))

import instalar_servicios as module


class ServicesTests(unittest.TestCase):

    def test_exact_inventory(self):
        rows = module.source_pairs()

        self.assertEqual(len(rows), 8)
        self.assertEqual(
            len({destination for _, destination, _ in rows}),
            8,
        )

        self.assertEqual(
            sum(p.suffix == ".service" for p, _, _ in rows),
            7,
        )

    def test_sources_exist(self):
        for source, _, _ in module.source_pairs():
            self.assertTrue(source.is_file(), source)
            self.assertFalse(source.is_symlink(), source)

    def test_units_validate(self):
        for source, _, _ in module.source_pairs():
            if source.suffix == ".service":
                module.validate_unit(source)

    def test_observer_policy(self):
        source = (
            ROOT / "operacion/plantillas/netlab360-observer"
        )

        module.validate_observer_rule(source.read_text())

    def test_wildcard_rejected(self):
        with self.assertRaisesRegex(
            RuntimeError, "SUDOERS_POLICY_INVALID"
        ):
            module.validate_observer_rule(
                "rc-aa-ec ALL=(root) NOPASSWD: ALL"
            )

    def test_multiple_commands_rejected(self):
        with self.assertRaises(RuntimeError):
            module.validate_observer_rule(
                "rc-aa-ec ALL=(root) NOPASSWD: "
                "/usr/local/libexec/netlab360-observer "
                "snapshot, /bin/bash"
            )

    def test_destination_collision(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "unit"
            path.write_text("preservar")

            with self.assertRaisesRegex(
                RuntimeError, "DESTINATION_EXISTS"
            ):
                module.absent(path)

            self.assertEqual(path.read_text(), "preservar")

    def test_dangling_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "unit"
            path.symlink_to(Path(folder) / "absent")

            with self.assertRaises(RuntimeError):
                module.absent(path)

    def test_confirmations_required(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                module.arguments(["--apply"])

    def test_plan_has_no_writes(self):
        with patch.object(module, "install_new") as write:
            with patch.object(module, "check_host") as check:
                with redirect_stdout(io.StringIO()):
                    module.plan()

                write.assert_not_called()
                check.assert_not_called()

    def test_host_failure_aborts_installation(self):
        with patch.object(
            module, "check_host",
            side_effect=RuntimeError("HOST_HAS_CONTAINERS"),
        ):
            with patch.object(module, "install_new") as write:
                with self.assertRaises(RuntimeError):
                    module.apply()

                write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
