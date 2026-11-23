"""S06-035: validaciones no invasivas de la interfaz experimental."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

FILE = Path(__file__).resolve().parents[1] / "scripts/s06/precheck_escenarios.py"
SPEC = importlib.util.spec_from_file_location("s06_precheck_escenarios", FILE)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class ExperimentPrecheckTests(unittest.TestCase):
    def test_catalogo_no_incluye_cambios(self):
        self.assertEqual(m.NS, "nl360-s02-h-hq-120")
        self.assertEqual(m.DEVICE, "eth0")
        commands = m.READ_ONLY_COMMANDS
        self.assertEqual(len(commands), 6)
        flat = " ".join(" ".join(cmd) for cmd in commands)
        self.assertNotIn(" qdisc add ", flat)
        self.assertNotIn(" qdisc replace ", flat)
        self.assertNotIn(" qdisc del ", flat)
        self.assertNotIn(" ens33 up ", flat)

    def test_gestion_conservada(self):
        m.check_management(
            "2: ens33 inet 192.168.47.40/24 scope global ens33",
            "default via 192.168.47.2 dev ens33 proto static metric 100",
        )

    def test_gateway_alterado_rechazado(self):
        with self.assertRaisesRegex(RuntimeError, "Ruta"):
            m.check_management(
                "2: ens33 inet 192.168.47.40/24 scope global ens33",
                "default via 192.168.47.3 dev ens33 proto static metric 100",
            )

    def test_ip_gestion_alterada_rechazada(self):
        with self.assertRaisesRegex(RuntimeError, "IP"):
            m.check_management(
                "2: ens33 inet 192.168.47.41/24 scope global ens33",
                "default via 192.168.47.2 dev ens33",
            )

    def test_interfaz_candidato_correcta(self):
        m.check_address([{
            "ifname": "eth0", "operstate": "UP",
            "addr_info": [{"family": "inet", "local": "10.70.20.20", "prefixlen": 24}],
        }])

    def test_interfaz_ausente_rechazada(self):
        with self.assertRaisesRegex(RuntimeError, "down"):
            m.check_address([{
                "ifname": "eth0", "operstate": "DOWN",
                "addr_info": [{"family": "inet", "local": "10.70.20.20", "prefixlen": 24}],
            }])

    def test_ip_cliente_alterada_rechazada(self):
        with self.assertRaisesRegex(RuntimeError, "IPv4"):
            m.check_address([{
                "ifname": "eth0", "operstate": "UP",
                "addr_info": [{"family": "inet", "local": "10.70.20.21", "prefixlen": 24}],
            }])

    def test_ruta_cliente_correcta(self):
        m.check_default([{"dst": "default", "gateway": "10.70.20.1", "dev": "eth0"}])

    def test_ruta_cliente_incorrecta_rechazada(self):
        with self.assertRaisesRegex(RuntimeError, "Gateway"):
            m.check_default([{"dst": "default", "gateway": "10.70.20.2", "dev": "eth0"}])

    def test_qdisc_noqueue_candidato(self):
        x = m.classify_qdisc([{"kind": "noqueue", "handle": "0:", "root": True}])
        self.assertEqual(x["state"], "CANDIDATE_NOQUEUE")
        self.assertFalse(x["mutating_action_executed"])

    def test_qdisc_preexistente_netem_bloqueado(self):
        x = m.classify_qdisc([{"kind": "netem", "root": True, "handle": "1:"}])
        self.assertEqual(x["state"], "BLOCKED_EXISTING_NETEM")

    def test_qdisc_fqcodel_requiere_revision(self):
        x = m.classify_qdisc([{"kind": "fq_codel", "root": True, "handle": "0:"}])
        self.assertEqual(x["state"], "REVIEW_QDISC_BEFORE_CHANGE")

    def test_qdisc_vacia_requiere_revision(self):
        self.assertEqual(m.classify_qdisc([])["state"], "REVIEW_QDISC_BEFORE_CHANGE")

    def test_qdisc_json_invalido(self):
        with self.assertRaises(ValueError):
            m.classify_qdisc({})

    def test_url_externa_rechazada(self):
        with self.assertRaisesRegex(ValueError, "URL"):
            m.read_json("https://example.com")

    def test_dataset_qa_preparado_sin_ground_truth(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "s06/datasets/curated" / m.CURATED_ID
            path.mkdir(parents=True)
            (path / "reporte_calidad.json").write_text(json.dumps({
                "schema": "NETLAB360_S06_CURATED_V1",
                "ground_truth_labels_available": 0,
                "training_ready": False,
                "record_counts": {"normalized_rows": 375},
            }))
            with mock.patch.object(m, "BASE", Path(d)):
                result = m.validate_curated()
            self.assertFalse(result["ground_truth_verified"])

    def test_dataset_qa_falso_rechazado(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "s06/datasets/curated" / m.CURATED_ID
            path.mkdir(parents=True)
            (path / "reporte_calidad.json").write_text(json.dumps({
                "schema": "NETLAB360_S06_CURATED_V1",
                "ground_truth_labels_available": 1,
                "training_ready": True,
                "record_counts": {"normalized_rows": 375},
            }))
            with mock.patch.object(m, "BASE", Path(d)):
                with self.assertRaises(RuntimeError):
                    m.validate_curated()

    def test_json_plan_privado(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(m, "BASE", Path(d)):
                p = m.save({"schema": m.SCHEMA, "actions_executed": "READ_ONLY"})
            self.assertTrue(p.exists())
            self.assertEqual(json.loads(p.read_text())["actions_executed"], "READ_ONLY")
            self.assertEqual(p.parent.stat().st_mode & 0o777, 0o700)


if __name__ == "__main__":
    unittest.main()
