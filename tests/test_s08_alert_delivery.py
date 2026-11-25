"""Pruebas del historial de notificaciones y configuración autorizada."""
import importlib.util
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
R = runpy.run_path(str(ROOT / "scripts/s08/recibir_alertas.py"))


def alert(name="NETLAB360S08ProbeFailed", phase="s08", status="firing"):
    labels = {"alertname": name, "phase": phase, "probe_id": "hq-s1-icmp",
              "laboratory": "netlab360-lab"}
    return {"labels": labels, "status": status, "startsAt": "2026-01-01T00:00:00Z",
            "endsAt": "2026-01-01T00:01:00Z"}


def payload(*rows):
    return {"version": "4", "receiver": "netlab360-local", "truncatedAlerts": 0,
            "status": "firing", "alerts": list(rows)}


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "history.sqlite3"
        R["initialize"](self.path)

    def test_deduplicate_and_resolve(self):
        self.assertEqual(R["record"](self.path, payload(alert())), 1)
        self.assertEqual(R["record"](self.path, payload(alert())), 0)
        self.assertEqual(R["record"](self.path, payload(alert(status="resolved"))), 1)
        history = R["inspect"](self.path, "operational")
        self.assertEqual(history["total"], 2)
        self.assertEqual({r["status"] for r in history["records"]}, {"firing", "resolved"})
        self.assertEqual(len({r["fingerprint"] for r in history["records"]}), 1)

    def test_synthetic_separate(self):
        row = alert("NETLAB360S08Validation", "validation")
        row["labels"].update(synthetic="true", run_id="1234567890abcdef")
        R["record"](self.path, payload(row))
        self.assertEqual(R["inspect"](self.path, "operational")["total"], 0)
        self.assertEqual(R["inspect"](self.path, "validation")["total"], 1)

    def test_reject_unknown_and_atomic(self):
        with self.assertRaises(ValueError):
            R["record"](self.path, payload(alert(), alert("Unapproved")))
        self.assertEqual(R["inspect"](self.path, "operational")["total"], 0)

    def test_reject_truncated(self):
        data = payload(alert())
        data["truncatedAlerts"] = 1
        with self.assertRaises(ValueError):
            R["record"](self.path, data)

    def test_resolved_without_firing_does_not_invent(self):
        R["record"](self.path, payload(alert(status="resolved")))
        result = R["inspect"](self.path, "operational")
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["records"][0]["status"], "resolved")

    def test_s04_accepted(self):
        row = alert("NETLAB360S04WANAdminDown", "s04")
        row["labels"] = {"alertname": "NETLAB360S04WANAdminDown", "phase": "s04",
                         "site": "HQ", "interface": "s1p", "severity": "warning"}
        self.assertEqual(R["record"](self.path, payload(row)), 1)


class ConfigTests(unittest.TestCase):
    def test_render_preserves_rules(self):
        path = ROOT / "scripts/s08/desplegar_alertas.py"
        # Cargar en un intérprete separado para no mezclar módulos api.
        import subprocess
        import sys
        code = """
import runpy, sys
from pathlib import Path
m = runpy.run_path(sys.argv[1])
original = "rule_files:\\n  - s04.yml\\n  - s08.yml\\nscrape_configs: []\\n"
final = m["render"](original, Path("/private/secret"))
assert final.startswith(original)
assert "127.0.0.1:9093" in final
assert "password_file: /private/secret" in final
temporary = m["render"](original, Path("/private/secret"), Path("/tmp/test.yml"))
assert "  - /tmp/test.yml" in temporary
assert "  - /tmp/test.yml" not in final
assert 'synthetic: "true"' in m["validation_rule"]("1234567890abcdef", 1000)
try:
    m["render"](final, Path("/private/secret"))
except ValueError:
    pass
else:
    raise AssertionError("Duplicate alerting accepted")
"""
        subprocess.run([sys.executable, "-I", "-B", "-c", code, str(path)],
                       check=True, timeout=10)


if __name__ == "__main__":
    unittest.main()
