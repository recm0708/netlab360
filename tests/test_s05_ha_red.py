"""Contrato offline para red HA S05: no se tocan switches ni Docker en CI."""
import importlib.util
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/laboratorio/s05-ha-red-servicios.py"
spec = importlib.util.spec_from_file_location("s05_ha_red", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class HADeploymentContract(TestCase):
    def test_ownership_and_unique_resources(self):
        self.assertEqual(m.OWNER, "NETLAB360_S05_HA_RED_V1")
        self.assertEqual(len(m.ROWS), 3)
        for field in ("role", "ns", "port", "peer", "addr"):
            self.assertEqual(len({r[field] for r in m.ROWS}), 3)
        self.assertEqual({r["site"] for r in m.ROWS}, {"HQ", "S1"})
        self.assertEqual({r["vid"] for r in m.ROWS}, {120, 220})
        self.assertTrue(all(len(r["port"]) <= 15 for r in m.ROWS))

    def test_management_and_s02_are_never_modified(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in (
            '"ens33", "down"', '"ens33", "up"',
            '"route", "replace"', '"route", "del"',
            '"docker", "stop"', '"docker", "run"',
            '"tr-sw", "delete"', '"trunk0", "delete"',
            '"br0", "delete"', '"kill", "-TERM"'
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn('S05_HA_RED_UP=OK', source)
        self.assertIn("S05_HA_SERVIDORES_HTTP=NO_INICIADOS", source)

    def test_state_guard_refuses_other_owners(self):
        with patch.object(m.STATE.__class__, "is_file", return_value=True), \
             patch.object(m.STATE.__class__, "is_symlink", return_value=False), \
             patch.object(m.STATE.__class__, "read_text",
                          return_value='{"owner":"OTHERS","roles":[],"namespaces":[],"ports":[]}'):
            with self.assertRaisesRegex(RuntimeError, "inválido"):
                m.read_state()

    def test_plan_only_prints_desired_resources(self):
        with patch("builtins.print") as printed:
            m.plan()
        self.assertGreaterEqual(printed.call_count, 4)
        text = "\n".join(str(c.args[0]) for c in printed.call_args_list)
        self.assertIn("S05_HA_PLAN_NS=3_PUERTOS=3", text)
        self.assertIn("S05_HA_PLAN_FRR=NO_CAMBIOS", text)
        self.assertIn("10.70.20.23", text)


if __name__ == "__main__":
    import unittest
    unittest.main()
