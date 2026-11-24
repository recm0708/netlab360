"""G4 TSDB: pruebas offline sin reiniciar servicios reales."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/observabilidad/s04_verificar_persistencia_tsdb.py"
spec = importlib.util.spec_from_file_location("netlab360_s04_tsdb", SOURCE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PersistenceTests(unittest.TestCase):
    def make_data(self):
        wan = [[100.0, 1.0], [102.0, 0.0], [104.0, 0.0], [106.0, 1.0]]
        firing = [[102.0, 1.0], [104.0, 1.0]]
        return {
            "schema": "NETLAB360_S04_G4_TSDB_V1",
            "prometheus_start_utc": "2026-10-27T05:10:00Z",
            "window_start_utc": "2026-10-27T06:04:45Z",
            "window_end_utc": "2026-10-27T06:07:00Z",
            "step_seconds": 2,
            "wan": wan,
            "firing": firing,
        }

    def test_series_validas(self):
        data = self.make_data()
        mod.check_values(data["wan"], data["firing"])

    def test_reinicio_real_mantiene_valores(self):
        before = self.make_data()
        after = self.make_data()
        after["prometheus_start_utc"] = "2026-10-27T07:00:00Z"
        mod.validate_after(before, after)

    def test_sin_reinicio_es_rechazado(self):
        s = self.make_data()
        with self.assertRaisesRegex(RuntimeError, "no fue reiniciado"):
            mod.validate_after(s, s.copy())

    def test_perdida_de_muestras_es_rechazada(self):
        before = self.make_data()
        after = self.make_data()
        after["prometheus_start_utc"] = "2026-10-27T07:00:00Z"
        after["wan"] = after["wan"][:2]
        with self.assertRaisesRegex(RuntimeError, "TSDB distinta"):
            mod.validate_after(before, after)

    def test_no_inferir_down_si_serie_solo_up(self):
        with self.assertRaisesRegex(RuntimeError, "DOWN/UP"):
            mod.check_values([[100.0, 1.0], [102.0, 1.0]], [[102.0, 1.0]])

    def test_firing_falso_rechazado(self):
        with self.assertRaisesRegex(RuntimeError, "firing invalida"):
            mod.check_values([[100.0, 0.0], [102.0, 1.0]], [[100.0, 0.0]])

    def test_filtro_prometheus_local(self):
        with self.assertRaises(ValueError):
            mod.get_json("https://example.com/api/v1/alerts")


if __name__ == "__main__":
    unittest.main()
