"""Contrato local de Grafana: fuente única, paneles delimitados y acceso local."""
import configparser
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "servicios/observabilidad/grafana"


class GrafanaTests(unittest.TestCase):
    def test_dashboard_contract(self):
        dashboard = json.loads((CONFIG / "dashboards/sondas.json").read_text())
        self.assertEqual(dashboard["uid"], "netlab360-s08-observacion")
        self.assertFalse(dashboard["editable"])
        self.assertEqual(len(dashboard["panels"]), 10)
        self.assertEqual({p["id"] for p in dashboard["panels"]}, set(range(1, 11)))
        for panel in dashboard["panels"]:
            self.assertEqual(panel["datasource"]["uid"], "netlab360-prometheus")
            for target in panel["targets"]:
                self.assertIn('{job="netlab360-s08-blackbox"}', target["expr"])
                self.assertEqual(target["datasource"]["uid"], "netlab360-prometheus")
                self.assertNotIn("vector(", target["expr"])
                self.assertNotEqual(target["instant"], target["range"])
        for minutes in (5, 15, 60):
            # Comparar títulos completos para distinguir 5 min de 15 min.
            expected = {
                f"SLI observado · {minutes} min": 1,
                f"Cobertura · {minutes} min": 4,
            }
            selected = [p for p in dashboard["panels"] if p["title"] in expected]
            self.assertEqual(len(selected), 2)
            self.assertEqual(
                {p["title"]: len(p["targets"]) for p in selected}, expected
            )
            for panel in selected:
                for target in panel["targets"]:
                    self.assertIn(f"[{minutes}m]", target["expr"])

    def test_single_source(self):
        text = (CONFIG / "provisioning/datasources/prometheus.yml").read_text()
        self.assertEqual(text.count("type: prometheus"), 1)
        self.assertIn("url: http://127.0.0.1:9091", text)
        self.assertIn("editable: false", text)

    def test_security_and_isolation(self):
        config = configparser.ConfigParser(interpolation=None)
        config.read(CONFIG / "grafana.ini")
        self.assertEqual(config["server"]["http_addr"], "127.0.0.1")
        self.assertFalse(config.getboolean("auth.anonymous", "enabled"))
        self.assertFalse(config.getboolean("users", "allow_sign_up"))
        self.assertFalse(config.getboolean("unified_alerting", "enabled"))
        for name in ("admin_password", "secret_key"):
            self.assertTrue(config["security"][name].startswith("$__file{"))
        unit = (ROOT / "operacion/plantillas/netlab360-s08-grafana.service").read_text()
        for setting in ("NoNewPrivileges=yes", "ProtectSystem=strict",
                        "IPAddressDeny=any", "IPAddressAllow=localhost",
                        "User=netlab360-s08-grafana", "CapabilityBoundingSet="):
            self.assertIn(setting, unit)


if __name__ == "__main__":
    unittest.main()
