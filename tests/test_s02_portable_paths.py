"""Regresión offline: scripts de la fase 2 portables a runners GitHub."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "s02-wan-links.py",
    "s02-lan-vlan.py",
    "s02-http-acl-demo.py",
)


def load_script(name: str):
    script = ROOT / "scripts" / "laboratorio" / name
    spec = importlib.util.spec_from_file_location(
        "test_portability_" + name.replace("-", "_").replace(".", "_"),
        script,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestS02PortablePaths(unittest.TestCase):
    def test_each_module_uses_checked_out_repository(self):
        for filename in FILES:
            with self.subTest(script=filename):
                module = load_script(filename)
                self.assertEqual(module.ROOT, ROOT)
                self.assertTrue((module.ROOT / "inventario/ipam/topologia-s02.yaml").is_file())

    def test_wan_lan_ipam_paths_follow_repository(self):
        for filename in FILES[:2]:
            with self.subTest(script=filename):
                module = load_script(filename)
                self.assertEqual(module.IPAM, ROOT / "inventario/ipam/topologia-s02.yaml")

    def test_http_loads_lan_module_from_same_repository(self):
        module = load_script("s02-http-acl-demo.py")
        self.assertEqual(module.lan.ROOT, ROOT)
        self.assertEqual(module.lan.IPAM, ROOT / "inventario/ipam/topologia-s02.yaml")


if __name__ == "__main__":
    unittest.main()
