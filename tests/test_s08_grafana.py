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
                f"Éxito observado (SLI) · {minutes} min": 1,
                f"Cobertura de muestras · {minutes} min": 4,
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

    def test_private_installation_prefix(self):
        prefix = "/opt/netlab360-grafana"
        unit = (ROOT / "operacion/plantillas/netlab360-s08-grafana.service").read_text()
        self.assertIn(f"WorkingDirectory={prefix}/grafana-13.3.2", unit)
        self.assertIn(f"--homepath={prefix}/grafana-13.3.2", unit)
        self.assertIn(f"--config={prefix}/grafana-config/grafana.ini", unit)
        config = configparser.ConfigParser(interpolation=None)
        config.read(CONFIG / "grafana.ini")
        self.assertEqual(config["paths"]["provisioning"], f"{prefix}/grafana-config/provisioning")
        provider = (CONFIG / "provisioning/dashboards/netlab360.yml").read_text()
        self.assertIn(f"path: {prefix}/grafana-config/dashboards", provider)
        installer = (ROOT / "scripts/s08/desplegar_grafana.sh").read_text()
        self.assertIn(f"PREFIX={prefix}", installer)
        self.assertIn('-g "$ACCOUNT" -m 0750 "$PREFIX"', installer)
        self.assertIn('sudo -n -u "$ACCOUNT" test -x "$INSTALL/bin/grafana"', installer)

    def test_visual_contract(self):
        dashboard = json.loads((CONFIG / "dashboards/sondas.json").read_text())
        self.assertEqual(dashboard["timezone"], "America/Panama")
        panels = {p["id"]: p for p in dashboard["panels"]}
        for i in (1, 2):
            self.assertEqual(panels[i]["type"], "state-timeline")
            self.assertFalse(panels[i]["fieldConfig"]["defaults"]["custom"]["spanNulls"])
        self.assertEqual(panels[3]["fieldConfig"]["defaults"]["unit"], "ms")
        for i, nominal in ((6, 30), (8, 90), (10, 360)):
            p = panels[i]
            self.assertEqual(p["type"], "table")
            self.assertTrue(all(t["format"] == "time_series" for t in p["targets"]))
            self.assertEqual([t["id"] for t in p["transformations"]], ["seriesToRows", "extractFields", "groupingToMatrix", "organize"])
            self.assertEqual(list(p["transformations"][3]["options"]["renameByName"].values()),
                             ["Sonda", "Adquiridas", "Adq. correctas", "Medidas", "Éxitos"])
            matrix = p["transformations"][2]["options"]
            self.assertEqual(matrix, {"rowField": "Sonda", "columnField": "Contador",
                                      "valueField": "Value", "emptyValue": "null"})
            self.assertEqual(p["transformations"][1]["options"]["source"], "Metric")
            steps = p["fieldConfig"]["defaults"]["thresholds"]["steps"]
            self.assertEqual([(s["value"], s["color"]) for s in steps],
                             [(None, "orange"), (nominal, "green"), (nominal + 1, "orange")])
            sli = panels[i - 1]["fieldConfig"]["defaults"]
            self.assertEqual(sli["unit"], "percent")
            self.assertEqual(sli["thresholds"]["steps"][-1]["color"], "blue")


    def test_sli_cards(self):
        dashboard = json.loads((CONFIG / "dashboards/sondas.json").read_text())
        panels = {p["id"]: p for p in dashboard["panels"]}
        for panel_id in (5, 7, 9):
            panel = panels[panel_id]
            self.assertEqual(panel["type"], "stat")
            x = ((panel_id - 5) // 2) * 8
            self.assertEqual(panel["gridPos"], {"x": x, "y": 19, "w": 8, "h": 8})
            coverage = panels[panel_id + 1]
            self.assertEqual(coverage["gridPos"], {"x": x, "y": 27, "w": 8, "h": 7})
            self.assertEqual(coverage["options"]["cellHeight"], "sm")
            self.assertEqual(coverage["fieldConfig"]["defaults"]["custom"]["minWidth"], 85)
            self.assertEqual(coverage["fieldConfig"]["overrides"][0]["properties"][1]["value"], 156)
            self.assertEqual(panel["options"]["orientation"], "auto")
            self.assertEqual(panel["options"]["colorMode"], "background")
            self.assertFalse(panel["options"]["wideLayout"])
            self.assertEqual(panel["options"]["justifyMode"], "center")
            self.assertTrue(panel["options"]["reduceOptions"]["values"])
            self.assertEqual(panel["options"]["reduceOptions"]["limit"], 5)
            self.assertEqual(panel["options"]["graphMode"], "none")
            self.assertEqual(panel["transformations"], [
                {"id": "seriesToRows", "options": {}},
                {"id": "sortBy", "options": {"sort": [{"field": "Metric", "desc": False}]}},
            ])
            defaults = panel["fieldConfig"]["defaults"]
            self.assertEqual((defaults["min"], defaults["max"], defaults["decimals"]), (0, 100, 2))
            self.assertEqual([(s["value"], s["color"]) for s in defaults["thresholds"]["steps"]],
                             [(None, "red"), (95, "orange"), (99, "blue")])
            self.assertEqual({m["options"]["match"] for m in defaults["mappings"]}, {"null", "nan"})
            self.assertTrue(all(m["options"]["result"]["color"] == "gray" for m in defaults["mappings"]))
            self.assertEqual(panel["targets"][0]["legendFormat"], "{{probe_id}}")


    def test_visible_probe_names(self):
        dashboard = json.loads((CONFIG / "dashboards/sondas.json").read_text())
        panels = {p["id"]: p for p in dashboard["panels"]}
        names = {
            "hq-s1-icmp": "HQ → S1 · ICMP",
            "hq-s2-icmp": "HQ → S2 · ICMP",
            "s2-hq-http": "S2 → FE-HQ · HTTP",
            "s2-hq-icmp": "S2 → FE-HQ · ICMP",
            "s2-hq-tcp": "S2 → FE-HQ · TCP",
        }
        for i in (1, 2, 3, 4):
            p = panels[i]
            overrides = {o["matcher"]["options"]: o["properties"][0]["value"]
                         for o in p["fieldConfig"]["overrides"]}
            self.assertEqual(overrides, names if i != 4 else {"s2-hq-http": names["s2-hq-http"]})
            self.assertEqual(p["targets"][0]["legendFormat"], "{{probe_id}}")
        for i in (1, 2):
            defaults = panels[i]["fieldConfig"]["defaults"]
            self.assertEqual(defaults["color"]["mode"], "fixed")
            self.assertEqual(defaults["mappings"][0]["options"]["0"]["color"], "red")
            self.assertEqual(defaults["mappings"][0]["options"]["1"]["color"], "green")
            self.assertFalse(defaults["custom"]["spanNulls"])
        for i in range(5, 11):
            field = "Metric" if i % 2 else "Sonda"
            override = next(o for o in panels[i]["fieldConfig"]["overrides"]
                            if o["matcher"]["options"] == field)
            mapping = next(p["value"] for p in override["properties"] if p["id"] == "mappings")
            self.assertEqual({k: v["text"] for k, v in mapping[0]["options"].items()}, names)
            if not i % 2:
                self.assertEqual(panels[i]["fieldConfig"]["defaults"]["mappings"][0]["options"]["result"]["text"],
                                 "Sin datos")


if __name__ == "__main__":
    unittest.main()
