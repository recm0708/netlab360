"""Regresión S05 HA: solo validaciones puras, sin acceso a VM/Docker."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validacion/s05-ha-precheck.py"
spec = importlib.util.spec_from_file_location("s05_ha_precheck", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class HAReadOnlyTests(unittest.TestCase):
    def test_candidate_ips_and_namespaces_are_distinct(self):
        values = list(module.CANDIDATES.values())
        self.assertEqual(len(values), 3)
        self.assertEqual(len({x[0] for x in values}), 3)
        self.assertEqual(len({x[3] for x in values}), 3)
        self.assertEqual(set(module.SWITCHES), {"HQ", "S1", "S2"})

    def test_only_observation_from_s05_script(self):
        content = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("S05_HA_CAMBIOS_INFRAESTRUCTURA=NINGUNO", content)
        for forbidden in (
            '"add", "link"', '"link", "set"', '"route", "add"',
            '"netns", "add"', '"netns", "delete"',
            '"docker", "run"', '"docker", "stop"',
            'subprocess.Popen(', '.write_text(', '.unlink('
        ):
            self.assertNotIn(forbidden, content, forbidden)

    def test_ipv4_inventory_reader_ignores_ipv6(self):
        raw = json.dumps([
            {"addr_info": [
                {"family": "inet", "local": "10.70.20.20"},
                {"family": "inet6", "local": "::1"}
            ]},
            {"addr_info": [{"family": "inet", "local": "10.71.20.20"}]}
        ])
        self.assertEqual(
            module.addresses(raw), {"10.70.20.20", "10.71.20.20"}
        )

    def test_management_and_ownership_guards_exist(self):
        content = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("192.168.47.40", content)
        self.assertIn("192.168.47.2", content)
        self.assertIn("NETLAB360_S02_WAN_LINKS_V1", content)
        self.assertIn("NETLAB360_S02_LAN_8021Q_V1", content)
        self.assertIn('S05_HA_PRECHECK=OK_DISENO_PENDIENTE', content)


if __name__ == "__main__":
    unittest.main()
