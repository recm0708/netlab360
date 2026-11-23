"""Regresión offline: docker0 puede cambiar linkdown tras iniciar contenedores.

Prueba los guardas WAN y LAN sin sudo, Docker ni namespaces.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WAN = "s02-wan-links.py"
LAN = "s02-lan-vlan.py"
MGMT_ADDR = ("2: ens33 inet 192.168.47.40/24 brd 192.168.47.255 "
             "scope global noprefixroute ens33\n")
DEFAULT = "default via 192.168.47.2 dev ens33 proto static metric 100"
CONNECTED = ("192.168.47.0/24 dev ens33 proto kernel scope link "
             "src 192.168.47.40 metric 100")
DOCKER = "172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1"


def load(name: str):
    target = ROOT / "scripts" / "laboratorio" / name
    spec = importlib.util.spec_from_file_location(
        "test_s02_guard_" + name.replace(".", "_").replace("-", "_"), target
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def snapshot(*, ens33: str = MGMT_ADDR,
             default: str = DEFAULT, connected: str = CONNECTED,
             docker: str = DOCKER, other: tuple[str, ...] = ()):
    return {
        "ens33": ens33,
        "routes": "\n".join((default, connected, docker, *other)) + "\n",
    }


class ManagementPostRestartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = [load(WAN), load(LAN)]

    def check(self, previous, current, expected: bool):
        for mod in self.modules:
            with self.subTest(module=mod.__name__):
                self.assertIs(
                    mod.management_snapshot_equal(current, previous), expected
                )

    def test_estados_iguales(self):
        s = snapshot()
        self.check(s, s, True)

    def test_docker0_linkdown_desaparece(self):
        old = snapshot(docker=DOCKER + " linkdown ")
        now = snapshot()
        self.check(old, now, True)

    def test_docker0_linkdown_aparece(self):
        old = snapshot()
        now = snapshot(docker=DOCKER + " linkdown ")
        self.check(old, now, True)

    def test_docker0_espacios_irregulares(self):
        old = snapshot(docker="  " + DOCKER + "   linkdown  ")
        now = snapshot(docker=DOCKER)
        self.check(old, now, True)

    def test_falla_ens33_alterada(self):
        self.check(snapshot(), snapshot(
            ens33=MGMT_ADDR.replace("192.168.47.40/24", "192.168.47.41/24")
        ), False)

    def test_falla_gateway_alterado(self):
        self.check(snapshot(), snapshot(
            default=DEFAULT.replace("192.168.47.2", "192.168.47.3")
        ), False)

    def test_falla_ruta_conectada_alterada(self):
        self.check(snapshot(), snapshot(
            connected=CONNECTED.replace("src 192.168.47.40",
                                        "src 192.168.47.41")
        ), False)

    def test_falla_docker0_prefijo_alterado(self):
        self.check(snapshot(), snapshot(
            docker=DOCKER.replace("172.17.0.0/16", "172.18.0.0/16")
        ), False)

    def test_falla_docker0_ip_alterada(self):
        self.check(snapshot(), snapshot(
            docker=DOCKER.replace("172.17.0.1", "172.17.0.2")
        ), False)

    def test_falla_ruta_docker0_desaparece(self):
        self.check(snapshot(), {
            "ens33": MGMT_ADDR, "routes": DEFAULT + "\n" + CONNECTED + "\n",
        }, False)

    def test_falla_ruta_extra(self):
        self.check(snapshot(), snapshot(other=(
            "10.0.0.0/24 via 192.168.47.99 dev ens33",)
        ), False)

    def test_falla_default_adicional(self):
        self.check(snapshot(), snapshot(other=(
            "default via 10.0.0.1 dev docker0 metric 200",)
        ), False)

    def test_falla_linkdown_en_ens33(self):
        self.check(snapshot(), snapshot(
            connected=CONNECTED + " linkdown"
        ), False)

    def test_falla_linkdown_no_kernel_docker0(self):
        base = DOCKER.replace("proto kernel", "proto static")
        self.check(snapshot(docker=base + " linkdown"),
                   snapshot(docker=base), False)

    def test_falla_campo_host_no_esperado(self):
        extra = snapshot()
        extra["routes_extra"] = ""
        self.check(snapshot(), extra, False)

    def test_falla_estructura_incorrecta(self):
        self.check(snapshot(), {}, False)
        self.check({}, snapshot(), False)


if __name__ == "__main__":
    unittest.main()
