"""Regresión offline: la API NOC parcial no debe provocar KeyError ni falsos OK."""
from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(site: str):
    path = ROOT / f"scripts/laboratorio/s05_lacp_{site}_integracion.py"
    spec = importlib.util.spec_from_file_location(f"test_s05_noc_{site}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def graph(routes: dict) -> dict:
    return {
        "ha_service": {"available": True, "active_backend": "BACKEND_HQ"},
        "routing": {"routes": routes},
    }


class TestS05NocFibSnapshots(unittest.TestCase):
    def test_respuesta_parcial_pasa_al_siguiente_intento(self):
        partial = graph({"S2": {"dev": "s2p"}})
        valid = graph({"S1": {"dev": "s1p"}, "S2": {"dev": "s2p"}})
        for site in ("hq", "s1", "s2"):
            with self.subTest(site=site):
                m = load(site)
                with mock.patch.object(m, "cmd", return_value="active"), \
                     mock.patch.object(m, "urlopen"), \
                     mock.patch.object(m.json, "load", side_effect=[partial, valid]) as load_json, \
                     mock.patch.object(m.time, "sleep") as sleep, \
                     redirect_stdout(io.StringIO()) as output:
                    m.assert_services()
                self.assertEqual(load_json.call_count, 2)
                sleep.assert_called_once_with(1)
                self.assertIn("NOC_FIB_NO_VALIDADO_INTENTO_1=SI", output.getvalue())
                self.assertIn("SERVICIOS_HA_FIB=OK", output.getvalue())

    def test_tres_respuestas_parciales_bloquean_lote(self):
        partial = graph({"S2": {"dev": "s2p"}})
        for site in ("hq", "s1", "s2"):
            with self.subTest(site=site):
                m = load(site)
                with mock.patch.object(m, "cmd", return_value="active"), \
                     mock.patch.object(m, "urlopen"), \
                     mock.patch.object(m.json, "load", return_value=partial) as load_json, \
                     mock.patch.object(m.time, "sleep"), \
                     redirect_stdout(io.StringIO()) as output:
                    with self.assertRaisesRegex(RuntimeError, "no confirmó HA/FIB"):
                        m.assert_services()
                self.assertEqual(load_json.call_count, 3)
                self.assertNotIn("SERVICIOS_HA_FIB=OK", output.getvalue())

    def test_rechaza_ruta_respaldo_como_estado_principal(self):
        wrong = graph({"S1": {"dev": "s1b"}, "S2": {"dev": "s2p"}})
        for site in ("hq", "s1", "s2"):
            with self.subTest(site=site):
                m = load(site)
                with mock.patch.object(m, "cmd", return_value="active"), \
                     mock.patch.object(m, "urlopen"), \
                     mock.patch.object(m.json, "load", return_value=wrong), \
                     mock.patch.object(m.time, "sleep"):
                    with self.assertRaises(RuntimeError):
                        m.assert_services()


if __name__ == "__main__":
    unittest.main()
