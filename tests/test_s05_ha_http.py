"""S05: contrato de backend HTTP y selección sin servicios/red reales."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "servicios/ha-s05/http_ha.py"
spec = importlib.util.spec_from_file_location("s05_ha_http", CODE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAILOVER = ROOT / "scripts/laboratorio/s05_ha_http_failover.py"
fspec = importlib.util.spec_from_file_location("s05_ha_http_failover", FAILOVER)
fm = importlib.util.module_from_spec(fspec)
fspec.loader.exec_module(fm)


class HAHTTPTests(unittest.TestCase):
    def test_fixed_roles_and_addresses(self):
        self.assertEqual(m.ROLES["backend-hq"]["address"], "10.70.20.21")
        self.assertEqual(m.ROLES["backend-s1"]["address"], "10.71.20.21")
        self.assertEqual(m.ROLES["frontend-hq"]["address"], "10.70.20.23")
        self.assertEqual(tuple(x["site"] for x in m.BACKENDS), ("HQ", "S1"))
        self.assertEqual({x["network"] for x in m.ROLES.values()},
                         {"nl360-s05-ha-hq", "nl360-s05-ha-s1", "nl360-s05-ha-fe"})

    def test_backend_has_verifiable_identity(self):
        status, data = m.payload("backend-hq")
        self.assertEqual(status, 200)
        self.assertEqual(data["id"], "BACKEND_HQ")
        self.assertEqual(data["site"], "HQ")
        self.assertEqual(data["status"], "healthy")
        self.assertIn("-05:00", data["observed_at_panama"])

    def test_primary_healthy_is_chosen(self):
        seen = []
        def reader(backend):
            seen.append(backend["id"])
            return {"status": "healthy"}
        status, data = m.payload("frontend-hq", reader)
        self.assertEqual(status, 200)
        self.assertEqual(data["selected_path"], "PRINCIPAL")
        self.assertEqual(data["active_backend"], "BACKEND_HQ")
        self.assertEqual(seen, ["BACKEND_HQ"])

    def test_failure_of_primary_selects_secondary(self):
        def reader(backend):
            if backend["id"] == "BACKEND_HQ":
                raise ConnectionRefusedError("caida controlada")
            return {"status": "healthy"}
        status, data = m.payload("frontend-hq", reader)
        self.assertEqual(status, 200)
        self.assertEqual(data["active_backend"], "BACKEND_S1")
        self.assertEqual(data["active_site"], "S1")
        self.assertEqual(data["selected_path"], "RESPALDO")

    def test_recovery_returns_to_primary(self):
        mode = {"primary_ok": False}
        def reader(backend):
            if backend["id"] == "BACKEND_HQ" and not mode["primary_ok"]:
                raise TimeoutError("falla")
            return {"status": "healthy"}
        self.assertEqual(m.payload("frontend-hq", reader)[1]["selected_path"],
                         "RESPALDO")
        mode["primary_ok"] = True
        self.assertEqual(m.payload("frontend-hq", reader)[1]["selected_path"],
                         "PRINCIPAL")

    def test_both_backends_down_is_explicit_503(self):
        def reader(backend):
            raise TimeoutError("offline")
        code, data = m.payload("frontend-hq", reader)
        self.assertEqual(code, 503)
        self.assertEqual(data["status"], "unavailable")
        self.assertIsNone(data["active_backend"])

    def test_rejects_wrong_backend_identity(self):
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self, n): return json.dumps(
                {"service": m.SERVICE, "role": "backend", "id": "BACKEND_S1",
                 "site": "S1", "status": "healthy"}
            ).encode()
        with patch.object(m, "urlopen", return_value=Response()):
            with self.assertRaisesRegex(ValueError, "Identidad"):
                m.backend_health(m.BACKENDS[0])

    def test_systemd_units_refer_only_fixed_namespaces(self):
        units = {
            "backend-hq": ("netlab360-s05-ha-backend-hq", "nl360-s05-ha-hq"),
            "backend-s1": ("netlab360-s05-ha-backend-s1", "nl360-s05-ha-s1"),
            "frontend-hq": ("netlab360-s05-ha-frontal-hq", "nl360-s05-ha-fe")
        }
        for role, (unit, ns) in units.items():
            config = (ROOT / "servicios/systemd" / f"{unit}.service").read_text()
            self.assertIn(f"NetworkNamespacePath=/run/netns/{ns}", config)
            self.assertIn(f"--role {role}", config)
            self.assertIn("User=rc-aa-ec", config)
            self.assertIn("NoNewPrivileges=yes", config)
            self.assertIn("ProtectSystem=strict", config)
            self.assertIn("Restart=on-failure", config)
            self.assertNotIn("ExecStart=/usr/bin/sudo", config)
            self.assertNotIn("User=root", config)


class HAHTTPFailoverTests(unittest.TestCase):
    def test_failure_script_only_touches_backend_hq_service(self):
        source = FAILOVER.read_text(encoding="utf-8")
        self.assertIn('ROOT = "netlab360-s05-ha-backend-hq.service"', source)
        self.assertIn('sudo("systemctl", "stop", ROOT)', source)
        self.assertIn('sudo("systemctl", "start", ROOT)', source)
        self.assertIn("finally:", source)
        for danger in ('"docker", "stop"', '"ip", "link", "set"',
                       '"route", "replace"', '"shutdown"', "shell=True"):
            self.assertNotIn(danger, source)

    def test_restarts_backend_even_if_fallback_not_observed(self):
        calls = []
        def sudo(*args):
            calls.append(args)
            return ""
        with patch.object(fm, "check"), \
             patch.object(fm, "fib_check"), \
             patch.object(fm, "sudo", side_effect=sudo), \
             patch.object(fm, "cmd", return_value="inactive"), \
             patch.object(fm, "wait", side_effect=[
                 RuntimeError("respaldo no responde"),
                 {"active_backend": "BACKEND_HQ"}
             ]):
            with self.assertRaisesRegex(RuntimeError, "respaldo no responde"):
                fm.experiment(5)
        self.assertIn(("systemctl", "stop", fm.ROOT), calls)
        self.assertIn(("systemctl", "start", fm.ROOT), calls)

    def test_successful_cycle_uses_same_endpoint_and_restores(self):
        calls = []
        def sudo(*args):
            calls.append(args)
            return ""
        with patch.object(fm, "check"), \
             patch.object(fm, "fib_check"), \
             patch.object(fm, "sudo", side_effect=sudo), \
             patch.object(fm, "cmd", return_value="inactive"), \
             patch.object(fm, "wait", side_effect=[
                 {"active_backend": "BACKEND_S1"},
                 {"active_backend": "BACKEND_HQ"}
             ]), \
             patch.object(fm.time, "monotonic", side_effect=[0.0, 6.0]):
            fm.experiment(5)
        self.assertEqual(calls, [
            ("systemctl", "stop", fm.ROOT),
            ("systemctl", "start", fm.ROOT)
        ])


if __name__ == "__main__":
    unittest.main()
