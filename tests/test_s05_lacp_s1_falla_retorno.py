"""Contrato offline S05 LACP S1: falla 2→1→2 con rescate al perder SSH."""
from __future__ import annotations

import importlib.util
import io
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/laboratorio/s05_lacp_s1_falla_retorno.py"
spec = importlib.util.spec_from_file_location("s05_lacp_s1_falla", PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestS05LACPS1Failover(unittest.TestCase):
    def test_single_member_is_exclusively_owned(self):
        self.assertEqual(module.MEMBER, "s5c1")
        self.assertEqual(module.lab.CLIENT, "nl360-s05-lacp-s1")
        self.assertEqual(module.lab.SW, "nl360-s02-sw-s1")
        self.assertEqual(module.lab.SW_BOND, "s5bond0")
        self.assertTrue(module.MAX_FALLBACK_SECONDS >= 60)

    def test_capturas_tienen_identidad_de_sede(self):
        src = PATH.read_text(encoding="utf-8")
        self.assertIn("INICIO_CAPTURA_S05_53_LACP_S1_UN_ENLACE", src)
        self.assertIn("FIN_CAPTURA_S05_53_LACP_S1_UN_ENLACE", src)
        self.assertIn("INICIO_CAPTURA_S05_54_LACP_S1_RETORNO", src)
        self.assertIn("FIN_CAPTURA_S05_54_LACP_S1_RETORNO", src)
        self.assertNotIn("_LACP_HQ_UN_ENLACE", src)
        self.assertNotIn("_LACP_HQ_RETORNO", src)

    def test_confirmation_required_for_run(self):
        p = subprocess.run(
            [sys.executable, str(PATH), "run"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--confirm-failover", p.stderr)

    def test_code_never_mutates_host_or_wan(self):
        source = PATH.read_text(encoding="utf-8")
        for cmd in ('"docker", "restart"', '"systemctl", "restart"',
                    '"netns", "delete"', '"link", "delete"',
                    '"ens33", "down"'):
            self.assertNotIn(cmd, source)
        self.assertIn('MEMBER, "down"', source)
        self.assertIn('MEMBER, "up"', source)
        self.assertIn('"--on-active=', source)
        self.assertIn("signal.SIGHUP", source)
        self.assertIn("S05_LACP_S1_ESTADOS_2_1_2=OK", source)

    def _simulate(self, fail_during_availability: bool) -> tuple[list, list]:
        record = {
            "status": "active",
            "alias": "S05_S1_1234567890abcdef",
            "before": {"mgmt": {}, "switch": {}},
        }
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(module, "precheck", return_value=record))
            stack.enter_context(mock.patch.object(
                module.lab, "alias_of", return_value=record["alias"]
            ))
            status = stack.enter_context(mock.patch.object(module.lab, "bond_ports"))
            stack.enter_context(mock.patch.object(module, "check_baseline"))
            stack.enter_context(mock.patch.object(module.lab, "status"))
            stack.enter_context(mock.patch.object(module, "check_http"))
            failures = stack.enter_context(mock.patch.object(module, "failsafe_arm", return_value="rescate-prueba"))
            cancel = stack.enter_context(mock.patch.object(module, "failsafe_cancel"))
            iface = stack.enter_context(mock.patch.object(module.lab, "ip_ns"))
            stack.enter_context(mock.patch.object(
                module, "availability",
                side_effect=RuntimeError("corte en prueba") if fail_during_availability else None,
            ))
            with redirect_stdout(io.StringIO()):
                if fail_during_availability:
                    with self.assertRaisesRegex(RuntimeError, "Ensayo incompleto"):
                        module.exercise()
                else:
                    module.exercise()
            failures.assert_called_once()
            self.assertEqual(
                [c.args[-1] for c in iface.call_args_list], ["down", "up"]
            )
            self.assertIn(mock.call(module.lab.CLIENT, module.lab.CLIENT_BOND, 1, attempts=15), status.call_args_list)
            self.assertIn(mock.call(module.lab.SW, module.lab.SW_BOND, 1, attempts=15), status.call_args_list)
            self.assertIn(mock.call(module.lab.CLIENT, module.lab.CLIENT_BOND, 2, attempts=15), status.call_args_list)
            self.assertIn(mock.call(module.lab.SW, module.lab.SW_BOND, 2, attempts=15), status.call_args_list)
            cancel.assert_called_once_with("rescate-prueba")
            return iface.call_args_list, status.call_args_list

    def test_success_restores_member_and_cancels_timer(self):
        self._simulate(fail_during_availability=False)

    def test_failure_still_restores_member_and_cancels_timer_if_healthy(self):
        self._simulate(fail_during_availability=True)

    def test_availability_usa_ping_verificado_y_http(self):
        with mock.patch.object(module.lab, "ping_verified") as ping, \
             mock.patch.object(module, "check_http") as http:
            module.availability()
        self.assertEqual(ping.call_count, 4)
        self.assertEqual(
            [call.args[1] for call in ping.call_args_list],
            [module.lab.GW, "10.70.20.23", "10.71.20.21", "10.72.20.20"]
        )
        self.assertTrue(all(
            call.kwargs["prefix"] == "S05_LACP_S1_FALLBACK_PING"
            for call in ping.call_args_list
        ))
        http.assert_called_once()

    def test_check_baseline_uses_management_guard(self):
        data={"before":{"mgmt":{"ens33":"baseline","routes":"baseline"},"switch":{}}}
        with mock.patch.object(module.lab,"assert_management_preserved") as guard, \
             mock.patch.object(module.lab,"assert_protected") as ports, \
             mock.patch.object(module.lab,"assert_services") as services:
            module.check_baseline(data)
            guard.assert_called_once_with(data["before"]["mgmt"])
            ports.assert_called_once_with({})
            services.assert_called_once()

    def test_check_baseline_rejects_management_change(self):
        data={"before":{"mgmt":{},"switch":{}}}
        with mock.patch.object(module.lab,"assert_management_preserved",side_effect=RuntimeError("Rutas de ens33")), \
             mock.patch.object(module.lab,"assert_protected") as ports:
            with self.assertRaisesRegex(RuntimeError,"Rutas de ens33"):
                module.check_baseline(data)
            ports.assert_not_called()

    def test_timer_already_unloaded(self):
        with mock.patch.object(module.lab,"cmd",side_effect=["not-found","inactive"]) as cmd:
            module.failsafe_cancel("rescate-prueba")
            self.assertEqual(cmd.call_count,2)
            self.assertFalse(any("stop" in call.args for call in cmd.call_args_list))

    def test_identity_checks_ownership(self):
        with mock.patch.object(module.lab, "identity"), \
             mock.patch.object(module.lab, "read_state", return_value={
                 "status": "active", "alias": "propia"
             }), \
             mock.patch.object(module.lab, "alias_of", return_value="otra"):
            with self.assertRaisesRegex(RuntimeError, "sin propiedad"):
                module.identity()


if __name__ == "__main__":
    unittest.main()
