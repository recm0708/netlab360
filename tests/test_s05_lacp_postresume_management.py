"""S05 LACP: verificación estable de gestión tras pausa/resume y rutas Docker/SDN."""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = "default via 192.168.47.2 dev ens33 proto static metric 100"
CONNECTED = ("192.168.47.0/24 dev ens33 proto kernel scope link "
             "src 192.168.47.40 metric 100")
EXTRAS = (
    "172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1",
    "172.31.200.0/24 dev br-test-sdn proto kernel scope link src 172.31.200.1",
)


def load(site: str):
    path = ROOT / f"scripts/laboratorio/s05-lacp-{site}-integracion.py"
    spec = importlib.util.spec_from_file_location(f"s05_management_{site}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot(*, ip: str = "192.168.47.40/24", default: str = DEFAULT,
             connected: str = CONNECTED, extras: tuple[str, ...] = (),
             ifindex: int = 2) -> dict[str, str]:
    return {
        "ens33": (f"{ifindex}: ens33 inet {ip} brd 192.168.47.255 "
                  "scope global noprefixroute ens33"),
        "routes": "\n".join((default, connected, *extras)) + "\n",
    }


class TestS05ResumeManagementRouting(unittest.TestCase):
    def test_ignora_exclusivamente_rutas_ajenas_docker_ovs(self):
        previous = snapshot()
        current = snapshot(extras=EXTRAS, ifindex=3)
        for site in ("hq", "s1", "s2"):
            with self.subTest(site=site):
                module = load(site)
                with mock.patch.object(module, "management", return_value=current), \
                     redirect_stdout(io.StringIO()) as stdout:
                    module.assert_management_preserved(previous)
                self.assertIn("GESTION_CRITICA=CONSERVADA", stdout.getvalue())

    def test_no_acepta_cambio_de_direccion_ens33(self):
        previous = snapshot()
        current = snapshot(ip="192.168.47.41/24", extras=EXTRAS)
        for site in ("hq", "s1", "s2"):
            with self.subTest(site=site):
                module = load(site)
                with mock.patch.object(module, "management", return_value=current):
                    with self.assertRaisesRegex(RuntimeError, "Direcciones IPv4"):
                        module.assert_management_preserved(previous)

    def test_no_acepta_cambio_de_gateway(self):
        current = snapshot(default="default via 192.168.47.3 dev ens33 proto static metric 100",
                           extras=EXTRAS)
        for site in ("hq", "s1", "s2"):
            with self.subTest(site=site):
                module = load(site)
                with mock.patch.object(module, "management", return_value=current):
                    with self.assertRaisesRegex(RuntimeError, "Rutas de ens33"):
                        module.assert_management_preserved(snapshot())

    def test_no_acepta_cambio_de_ruta_conectada_ens33(self):
        current = snapshot(
            connected=("192.168.47.0/24 dev ens33 proto kernel scope link "
                       "src 192.168.47.41 metric 100"), extras=EXTRAS)
        for site in ("hq", "s1", "s2"):
            with self.subTest(site=site):
                module = load(site)
                with mock.patch.object(module, "management", return_value=current):
                    with self.assertRaisesRegex(RuntimeError, "Rutas de ens33"):
                        module.assert_management_preserved(snapshot())

    def test_no_acepta_ruta_default_adicional_ajena(self):
        current = snapshot(extras=(
            "default via 10.0.0.1 dev docker0 metric 200",
            *EXTRAS,
        ))
        for site in ("hq", "s1", "s2"):
            with self.subTest(site=site):
                module = load(site)
                with mock.patch.object(module, "management", return_value=current):
                    with self.assertRaisesRegex(RuntimeError, "Rutas de ens33"):
                        module.assert_management_preserved(snapshot())

    def test_registro_igual_heredado_no_se_rompe(self):
        previous = {"x": 1}
        for site in ("hq", "s1", "s2"):
            with self.subTest(site=site):
                module = load(site)
                with mock.patch.object(module, "management", return_value=previous):
                    module.assert_management_preserved(previous)


if __name__ == "__main__":
    unittest.main()
