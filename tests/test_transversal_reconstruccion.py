"""Comprobamos la reconstrucción sin crear infraestructura real."""

from contextlib import redirect_stdout, redirect_stderr
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "operacion"))

import reconstruir as module


class ReconstructionTests(unittest.TestCase):

    def test_plan_does_not_execute(self):
        with patch.object(module, "execute") as run:
            with patch.object(module, "check_clean") as check:
                with redirect_stdout(io.StringIO()):
                    module.plan()

                run.assert_not_called()
                check.assert_not_called()

    def test_apply_requires_all_confirmations(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                module.arguments(["--apply"])

        args = module.arguments([
            "--apply",
            "--confirm-clean-host",
            "--confirm-snapshot",
            "--confirm-reviewed-config",
            "--confirm-new-identity",
        ])

        self.assertTrue(args.apply)

    def test_plan_rejects_confirmations(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                module.arguments([
                    "--plan", "--confirm-snapshot",
                ])

    def test_existing_containers_rejected(self):
        with patch.object(module, "read", return_value="container"):
            with self.assertRaisesRegex(
                RuntimeError, "HOST_HAS_CONTAINERS"
            ):
                module.check_empty_resources()

    def test_existing_namespaces_rejected(self):
        with patch.object(
            module, "read", side_effect=["", "namespace"]
        ):
            with self.assertRaisesRegex(
                RuntimeError, "HOST_HAS_NAMESPACES"
            ):
                module.check_empty_resources()

    def test_existing_bridge_rejected(self):
        with patch.object(
            module, "read", side_effect=["", "", "bridge"]
        ):
            with self.assertRaisesRegex(
                RuntimeError, "HOST_HAS_OVS_BRIDGES"
            ):
                module.check_empty_resources()

    def test_service_dependencies(self):
        rows = module.steps()

        def index(argv):
            return rows.index(("command", argv))

        ha = module.network_steps("HA")[0]
        lacp = module.network_steps("LACP_HQ")[0]

        for unit in module.OBSERVABILITY:
            self.assertLess(
                index((
                    "sudo", "-n", "systemctl", "start", unit
                )),
                rows.index(ha),
            )

        for unit in module.HA_SERVICES:
            self.assertLess(
                index((
                    "sudo", "-n", "systemctl", "start", unit
                )),
                rows.index(lacp),
            )

        self.assertLess(
            rows.index(("wait", ("baseline",))),
            rows.index(ha),
        )

        self.assertLess(
            rows.index(("wait", ("ha",))),
            rows.index(lacp),
        )

    def test_abort_on_failure(self):
        executor = Mock(
            side_effect=RuntimeError("SIMULATED_FAILURE")
        )

        waiter = Mock()

        with self.assertRaisesRegex(
            RuntimeError, "SIMULATED_FAILURE"
        ):
            module.run_steps(executor, waiter)

        self.assertEqual(executor.call_count, 1)
        waiter.assert_not_called()

    def test_simulated_complete_sequence(self):
        executor = Mock()
        waiter = Mock()

        module.run_steps(executor, waiter)

        self.assertEqual(
            executor.call_count,
            sum(
                kind == "command"
                for kind, _ in module.steps()
            ),
        )

        self.assertEqual(
            [x.args for x in waiter.call_args_list],
            [("baseline",), ("ha",)],
        )

    def test_readiness_requires_valid_sources(self):
        graph = {
            "telemetry": {"available": True},
            "routing": {
                "available": True,
                "routes": {
                    "S1": {"dev": "s1p"},
                    "S2": {"dev": "s2p"},
                },
            },
        }

        self.assertTrue(module.graph_ready(graph, "baseline"))
        self.assertFalse(module.graph_ready(graph, "ha"))

        graph["ha_service"] = {"available": True}

        self.assertTrue(module.graph_ready(graph, "ha"))

        graph["routing"]["routes"]["S1"]["dev"] = "s1b"

        self.assertFalse(module.graph_ready(graph, "ha"))

    def test_apply_aborts_before_execution_if_not_clean(self):
        with patch.object(
            module, "check_clean",
            side_effect=RuntimeError("HOST_HAS_CONTAINERS"),
        ):
            with patch.object(module, "run_steps") as run:
                with self.assertRaises(RuntimeError):
                    module.apply()

                run.assert_not_called()

    def test_no_automatic_rfc_actions(self):
        commands = [
            " ".join(argv)
            for kind, argv in module.steps()
            if kind == "command"
        ]

        self.assertFalse(any(
            item in command
            for command in commands
            for item in (
                "approve-execute",
                "s07-aceptar-api",
                "docker rm",
                "systemctl enable",
                "ip netns delete",
            )
        ))


if __name__ == "__main__":
    unittest.main()
