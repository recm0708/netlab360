"""Pruebas aisladas del orquestador de incidentes S04: sin Docker ni redes reales."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/observabilidad/s04-incidente-wan.py"
spec = importlib.util.spec_from_file_location("netlab360_s04_incidente_wan", MODULE_PATH)
assert spec is not None and spec.loader is not None
incident = importlib.util.module_from_spec(spec)
spec.loader.exec_module(incident)


class IncidentTests(unittest.TestCase):
    def test_alert_filtrada_por_sede_e_interfaz(self):
        snapshot = {
            "status": "success",
            "data": {"alerts": [
                {"labels": {"alertname": incident.ALERT, "site": "S1",
                            "interface": "s1p"}, "state": "firing"},
                {"labels": {"alertname": incident.ALERT, "site": "HQ",
                            "interface": "s1p"}, "state": "pending"},
            ]},
        }
        with patch.object(incident, "read_json", return_value=snapshot):
            self.assertEqual(incident.alert_state(), "pending")

    def test_alert_ausente_es_inactiva(self):
        with patch.object(incident, "read_json", return_value={
            "status": "success", "data": {"alerts": []},
        }):
            self.assertEqual(incident.alert_state(), "inactive")

    def test_alert_duplicada_se_rechaza(self):
        item = {"labels": {"alertname": incident.ALERT, "site": "HQ",
                           "interface": "s1p"}, "state": "firing"}
        with patch.object(incident, "read_json", return_value={
            "status": "success", "data": {"alerts": [item, item]},
        }):
            with self.assertRaises(RuntimeError):
                incident.alert_state()

    def test_filtro_direcciones_loopback(self):
        with self.assertRaises(ValueError):
            incident.read_json("https://example.org/api/v1/alerts")

    def test_restauracion_aun_si_falla_corte(self):
        calls = []

        class FakeS02:
            def ns(self, _pid, *args):
                calls.append(args)
                if args[-1] == "down":
                    raise RuntimeError("Corte simulado interrumpido")
                return ""

            def wait_fib(self, _pid, _target, _device, limit=90):
                return "dev s1p"

            def ping(self, _pid, _target):
                return None

            def host_guard(self, _before):
                return None

        with self.assertRaisesRegex(RuntimeError, "Incidente incompleto"):
            incident.observed_failure(
                FakeS02(),
                {"R-HQ": "100", "R-S1": "101"},
                ("addr", "route"),
                seconds=20,
            )
        self.assertIn(("ip", "link", "set", "s1p", "down"), calls)
        self.assertIn(("ip", "link", "set", "s1p", "up"), calls)


if __name__ == "__main__":
    unittest.main()
