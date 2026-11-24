"""Pruebas offline de clasificador de eventos FIB y seguridad del monitor S05."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OBSERVER = ROOT / "scripts/validacion/s05_observar_conmutacion_noc.py"
FAILOVER = ROOT / "scripts/laboratorio/s02_failover_wan.py"
spec = importlib.util.spec_from_file_location("s05_observador", OBSERVER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def graph(primary="selected", backup="standby", *, source=True,
          topology="active", site="S1"):
    return {
        "project": "NETLAB360",
        "observed_at_utc": "2026-11-11T03:00:00+00:00",
        "telemetry": {"available": source, "topology": topology},
        "routing": {"available": source, "traffic_measured": False,
                    "routes": {site: {"dev": "s1p" if primary == "selected" else "s1b",
                                      "gateway": "10.78.0.2" if primary == "selected" else "10.78.0.6"}}},
        "links": [
            {"id": f"WAN-PRIMARIA-HQ-{site}", "route_selection": primary,
             "status": "admin-up" if primary == "selected" else "admin-down"},
            {"id": f"WAN-RESPALDO-HQ-{site}", "route_selection": backup,
             "status": "admin-up"},
        ],
    }


class ObserverTests(unittest.TestCase):
    def test_primary_state(self):
        d = module.clasificar(graph(), "S1")
        self.assertEqual(d["fase"], "PRINCIPAL")
        self.assertEqual(d["fib_interfaz"], "s1p")

    def test_backup_selected_during_failure(self):
        d = module.clasificar(graph("unavailable", "selected"), "S1")
        self.assertEqual(d["fase"], "RESPALDO")
        self.assertEqual(d["fib_interfaz"], "s1b")

    def test_no_unverified_green_or_backup(self):
        d = module.clasificar(graph("unavailable", "selected", source=False), "S1")
        self.assertEqual(d["fase"], "SIN_FUENTE_VERIFICABLE")

    def test_unexpected_pair_is_transition_not_success(self):
        d = module.clasificar(graph("standby", "standby"), "S1")
        self.assertEqual(d["fase"], "TRANSICION")

    def test_precheck_refuses_false_baseline(self):
        with patch.object(module, "consultar", return_value=graph(
                "unavailable", "selected")):
            with self.assertRaises(module.ObservacionError):
                module.precheck("S1")

    def test_precheck_accepts_verified_baseline(self):
        with patch.object(module, "consultar", return_value=graph()):
            state = module.precheck("S1")
        self.assertEqual(state["fase"], "PRINCIPAL")

    def test_observer_is_read_only_and_bounded(self):
        text = OBSERVER.read_text(encoding="utf-8")
        self.assertIn('API = "http://127.0.0.1:9130/api/v1/graph"', text)
        self.assertNotIn("subprocess", text)
        self.assertNotIn("sudo", text)
        self.assertIn("15 <= args.seconds <= 180", text)
        self.assertIn("progress == 3", text)

    def test_failover_restores_after_observation_window(self):
        code = FAILOVER.read_text(encoding="utf-8")
        self.assertIn('--hold-seconds', code)
        self.assertIn('0 <= args.hold_seconds <= 30', code)
        self.assertIn('time.sleep(args.hold_seconds)', code)
        self.assertIn('finally:', code)
        self.assertIn('ns(h, "ip", "link", "set", x["interface"], "up")', code)
        self.assertLess(code.index("time.sleep(args.hold_seconds)"),
                        code.index("finally:"))


if __name__ == "__main__":
    unittest.main()
