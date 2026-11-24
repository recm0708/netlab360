"""Contrato offline del ciclo NOC HA HQ→S1→HQ; sin modificar systemd real."""
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validacion/s05_ha_noc_ciclo.py"
spec = importlib.util.spec_from_file_location("s05_ha_noc_ciclo", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def obs(active="BACKEND_HQ"):
    return {
        "observed_utc": "2026-11-11T14:00:00+00:00",
        "ha_available": True, "active": active,
        "path": "PRINCIPAL" if active == "BACKEND_HQ" else "RESPALDO",
        "status": "running", "fib_s1": "s1p", "fib_s2": "s2p",
        "nodes": {"FRONTAL_HQ": "running", "BACKEND_HQ": "running",
                  "BACKEND_S1": "running"},
    }


class NOCFailoverContractTests(unittest.TestCase):
    def test_phase_needs_actual_backend_and_frontend(self):
        self.assertTrue(m.is_phase(obs("BACKEND_HQ"), "BACKEND_HQ"))
        self.assertTrue(m.is_phase(obs("BACKEND_S1"), "BACKEND_S1"))
        self.assertFalse(m.is_phase(obs("BACKEND_HQ"), "BACKEND_S1"))
        row = obs("BACKEND_S1")
        row["nodes"]["FRONTAL_HQ"] = "unknown"
        self.assertFalse(m.is_phase(row, "BACKEND_S1"))

    def test_static_commands_only_stop_ha_backend_hq(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('ROOT = "netlab360-s05-ha-backend-hq.service"', source)
        self.assertIn('"systemctl", "stop", ROOT', source)
        self.assertIn('"systemctl", "start", ROOT', source)
        self.assertIn("finally:", source)
        for forbidden in ("docker stop", "ip link set", "ip netns delete",
                          "route replace", "sudo -n systemctl reboot"):
            self.assertNotIn(forbidden, source)

    def test_sample_requires_three_nodes_and_fib(self):
        class Result:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self): return json.dumps({
                "counts": {"extensions": 3},
                "nodes": [{"id": x, "status": "running"} for x in m.NODES],
                "ha_service": {"available": True, "active_backend": "BACKEND_HQ",
                               "selected_path": "PRINCIPAL", "status": "running"},
                "routing": {"available": True,
                            "routes": {"S1": {"dev": "s1p"}, "S2": {"dev": "s2p"}}}
            }).encode()
        with patch.object(m, "urlopen", return_value=Result()):
            result = m.sample()
        self.assertTrue(m.is_phase(result, "BACKEND_HQ"))

    def test_backup_failure_always_starts_hq_again(self):
        cmds = []
        def fake_cmd(*args):
            cmds.append(args)
            return "active"
        with TemporaryDirectory() as d, \
             patch.object(m, "OUTPUT_DIR", Path(d)), \
             patch.object(m, "precheck"), \
             patch.object(m, "sample", return_value=obs()), \
             patch.object(m, "cmd", side_effect=fake_cmd), \
             patch.object(m, "wait_phase", side_effect=[
                 RuntimeError("No se observó respaldo"),
                 obs()
             ]):
            with self.assertRaisesRegex(RuntimeError, "No se observó respaldo"):
                m.run_trial(5)
        self.assertIn(("sudo", "-n", "systemctl", "stop", m.ROOT), cmds)
        self.assertIn(("sudo", "-n", "systemctl", "start", m.ROOT), cmds)


if __name__ == "__main__":
    unittest.main()
