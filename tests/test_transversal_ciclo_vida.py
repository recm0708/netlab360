"""Validamos el catálogo sin realizar operaciones de red."""

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "operacion/ciclo_vida.py"

spec = importlib.util.spec_from_file_location(
    "netlab360_ciclo_vida", SOURCE
)

lifecycle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lifecycle)


class LifecycleTests(unittest.TestCase):

    def test_catalog_complete(self):
        self.assertTrue(lifecycle.validate_catalog())
        self.assertEqual(len(lifecycle.DEPLOYMENT), 19)

    def test_network_components(self):
        self.assertEqual(
            [row[0] for row in lifecycle.NETWORK_COMPONENTS],
            ["WAN", "LAN", "HA", "LACP_HQ",
             "LACP_S1", "LACP_S2", "SDN"],
        )

    def test_confirmation_contracts(self):
        for name, _, flag in lifecycle.NETWORK_COMPONENTS:
            expected = (
                "--snapshot-confirmado"
                if name in {"WAN", "LAN"}
                else "--confirm-isolated"
            )
            self.assertEqual(flag, expected)

    def test_service_order(self):
        units = lifecycle.UNITS
        self.assertEqual(len(units), 7)
        self.assertEqual(len(set(units)), 7)

        self.assertLess(
            units.index("netlab360-s04-exporter.service"),
            units.index("netlab360-s04-prometheus.service"),
        )

        self.assertLess(
            units.index("netlab360-s05-ha-backend-hq.service"),
            units.index("netlab360-s05-ha-frontal-hq.service"),
        )

        self.assertFalse(
            any("s07-api" in unit for unit in units)
        )

    def test_deployment_only_plan(self):
        output = io.StringIO()

        with patch.object(subprocess, "run") as run:
            with redirect_stdout(output):
                lifecycle.deployment_plan()

            run.assert_not_called()

        self.assertIn(
            "DESPLIEGUE_EJECUTADO=NO",
            output.getvalue(),
        )

    def test_shutdown_reverse_order(self):
        output = io.StringIO()

        with redirect_stdout(output):
            lifecycle.shutdown_plan()

        lines = output.getvalue().splitlines()

        actual = [
            line.split("=", 1)[1]
            for line in lines
            if line.startswith("DETENER_SERVICIO=")
        ]

        self.assertEqual(
            actual, list(reversed(lifecycle.UNITS))
        )

    def test_apply_not_available(self):
        result = subprocess.run(
            [
                "bash",
                str(ROOT / "operacion/desplegar.sh"),
                "--apply",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        self.assertNotEqual(result.returncode, 0)

    def test_containers_exact(self):
        self.assertEqual(len(lifecycle.CONTAINERS), 4)

        self.assertEqual(
            len(set(lifecycle.CONTAINERS)), 4
        )


if __name__ == "__main__":
    unittest.main()
