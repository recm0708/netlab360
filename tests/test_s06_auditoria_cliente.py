"""S06-039: pruebas offline de auditoria no invasiva de cliente conectado."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

FILE = Path(__file__).resolve().parents[1] / "scripts/s06/auditar_cliente_productivo.py"
SPEC = importlib.util.spec_from_file_location("s06_audit_client", FILE)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class ProductionReadonlyAuditTests(unittest.TestCase):
    def test_clientes_y_destinos_fijos(self):
        self.assertEqual(m.NS, "nl360-s02-h-hq-120")
        self.assertEqual(m.DEVICE, "eth0")
        self.assertEqual(m.PROBES, {
            "HQ_A_S1": "10.71.20.20", "HQ_A_S2": "10.72.20.20",
        })

    def test_catalogo_solo_consultas(self):
        calls = [m.LINK_CMD, m.QDISC_CMD, m.NS_CMD, m.STATE_ABSENT_CMD]
        calls.extend(m.ROUTE_COMMANDS.values())
        for args in calls:
            s = " ".join(args)
            for word in (" qdisc add", " qdisc del", " qdisc replace",
                         " link set ", " netns del ", " iptables ", " apply"):
                self.assertNotIn(word, s)

    def test_rechaza_ejecucion_root(self):
        with mock.patch.object(m.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "root"):
                m.inspect()

    def test_ruta_esperada(self):
        actual = m.confirm_route([{
            "dst": "10.71.20.20", "dev": "eth0",
            "prefsrc": "10.70.20.20", "gateway": "10.70.20.1"
        }], "10.71.20.20")
        self.assertEqual(actual["interface"], "eth0")
        self.assertEqual(actual["gateway_seen"], "10.70.20.1")

    def test_ruta_sin_gateway_es_bloqueante(self):
        with self.assertRaisesRegex(RuntimeError, "Next-hop"):
            m.confirm_route([{
                "dst": "10.71.20.20", "dev": "eth0",
                "prefsrc": "10.70.20.20"
            }], "10.71.20.20")

    def test_rechaza_salida_por_ens33(self):
        with self.assertRaisesRegex(RuntimeError, "cliente"):
            m.confirm_route([{
                "dst": "10.71.20.20", "dev": "ens33",
                "prefsrc": "192.168.47.40",
            }], "10.71.20.20")

    def test_rechaza_siguiente_salto_ajeno(self):
        with self.assertRaisesRegex(RuntimeError, "gateway"):
            m.confirm_route([{
                "dst": "10.71.20.20", "dev": "eth0",
                "prefsrc": "10.70.20.20", "gateway": "10.70.20.99"
            }], "10.71.20.20")

    def test_rechaza_ruta_incorrecta_o_ambigua(self):
        with self.assertRaises(RuntimeError):
            m.confirm_route([], "10.71.20.20")
        with self.assertRaises(RuntimeError):
            m.confirm_route([{"dst": "10.72.20.20", "dev": "eth0",
                              "prefsrc": "10.70.20.20"}], "10.71.20.20")

    def test_link_up_y_tipo_sin_autorizar_cambio(self):
        x = m.confirm_link([{
            "ifname": "eth0", "ifindex": 8, "operstate": "UP",
            "linkinfo": {"info_kind": "veth"},
            "link_index": 4, "link_netnsid": 0,
        }])
        self.assertEqual(x["link_type"], "veth")
        self.assertTrue(x["production_connected"])

    def test_link_sin_tipo_muestra_incertidumbre(self):
        x = m.confirm_link([{"ifname": "eth0", "operstate": "UP"}])
        self.assertEqual(x["link_type"], "UNKNOWN_REVIEW")

    def test_link_cambiado_rechazado(self):
        for value in ([], [{"ifname": "ens33", "operstate": "UP"}],
                      [{"ifname": "eth0", "operstate": "DOWN"}]):
            with self.subTest(link=value), self.assertRaises(RuntimeError):
                m.confirm_link(value)

    def test_qdisc_original_noqueue(self):
        x = m.confirm_qdisc([{"root": True, "kind": "noqueue", "handle": "0:"}])
        self.assertEqual(x["state"], "CANDIDATE_NOQUEUE")

    def test_qdisc_netem_bloqueado(self):
        with self.assertRaisesRegex(RuntimeError, "Qdisc"):
            m.confirm_qdisc([{"root": True, "kind": "netem", "handle": "106:"}])

    def test_estado_aislado_residual_bloquea(self):
        with self.assertRaisesRegex(RuntimeError, "Restos"):
            m.ensure_isolated_cleanup({m.NS} | {f"ns{i}" for i in range(20)}, False)
        with self.assertRaisesRegex(RuntimeError, "Restos"):
            m.ensure_isolated_cleanup({m.ISOLATED_NS, m.NS} |
                                      {f"ns{i}" for i in range(19)}, True)

    def test_inventario_21_requerido(self):
        with self.assertRaisesRegex(RuntimeError, "Inventario"):
            m.ensure_isolated_cleanup({m.NS}, True)

    def test_inventario_aislado_limpio(self):
        m.ensure_isolated_cleanup({m.NS} | {f"ns{i}" for i in range(20)}, True)

    def test_servicio_caido_bloquea(self):
        services = {x: "active" for x in m.SERVICES}
        m.confirm_services(services)
        services["netlab360-s05-noc"] = "inactive"
        with self.assertRaisesRegex(RuntimeError, "Servicio"):
            m.confirm_services(services)

    def test_muestra_que_no_es_una_aprobacion(self):
        with mock.patch.object(m.os, "geteuid", return_value=1000), \
             mock.patch.object(m, "inspect_035", return_value={
                 "qdisc": {"qdiscs": [{"root": True, "kind": "noqueue"}]},
                 "dataset": {"rows": 375, "ground_truth_verified": False}
             }), \
             mock.patch.object(m, "command") as cmd, \
             mock.patch.object(m, "subprocess") as sp, \
             mock.patch.object(m, "read_json") as api:
            def respond(argv):
                if argv == m.NS_CMD:
                    return "\n".join([m.NS] + [f"ns{i}" for i in range(20)])
                if argv == m.LINK_CMD:
                    return json.dumps([{"ifname": "eth0", "operstate": "UP",
                                        "linkinfo": {"info_kind": "veth"}}])
                if argv == m.QDISC_CMD:
                    return '[{"root":true,"kind":"noqueue"}]'
                for name, v in m.ROUTE_COMMANDS.items():
                    if argv == v:
                        return json.dumps([{
                            "dst": m.PROBES[name], "dev": "eth0",
                            "prefsrc": "10.70.20.20", "gateway": "10.70.20.1"
                        }])
                if argv[0] == "systemctl":
                    return "active"
                raise AssertionError("unexpected " + str(argv))
            cmd.side_effect = respond
            sp.run.return_value.returncode = 0
            api.return_value = {
                "lacp": {"available": True}, "sdn": {"status": "connected"},
                "ha_service": {"status": "running", "active_backend": "BACKEND_HQ"},
                "nodes": [None] * 18, "links": [None] * 21,
            }
            report = m.inspect()
        self.assertFalse(report["production_change_authorized"])
        self.assertFalse(report["network_changes_executed"])
        self.assertFalse(report["ground_truth_verified"])
        self.assertFalse(report["training_ready"])
        self.assertEqual(len(report["pending_gates"]), 6)

    def test_reporte_privado(self):
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(m, "BASE", Path(tmp)):
            f = m.save({"schema": m.SCHEMA, "production_change_authorized": False})
            self.assertEqual(f.parent.stat().st_mode & 0o777, 0o700)
            self.assertFalse(json.loads(f.read_text())["production_change_authorized"])


if __name__ == "__main__":
    unittest.main()
