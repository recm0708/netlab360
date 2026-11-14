"""Pruebas offline del dominio SDN S05: no puede conectar troncales ni gestionar WAN."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/s05/sdn/faucet.yaml"


class TestS05FaucetIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

    def test_faucet_un_solo_datapath_exclusivo(self):
        self.assertEqual(self.data["version"], 2)
        self.assertEqual(set(self.data["dps"]), {"br-s05-sdn"})
        dp = self.data["dps"]["br-s05-sdn"]
        self.assertEqual(dp["dp_id"], 0x505)
        self.assertEqual(dp["hardware"], "Open vSwitch")

    def test_dos_vlans_no_coinciden_con_s02(self):
        vlans = self.data["vlans"]
        self.assertEqual({name: row["vid"] for name, row in vlans.items()},
                         {"s05_experimento": 410, "s05_restringida": 420})
        self.assertTrue({x["vid"] for x in vlans.values()}
                        .isdisjoint({110, 120, 130, 210, 220, 230, 310, 320, 330}))

    def test_puertos_asignados_de_forma_determinista(self):
        ports = self.data["dps"]["br-s05-sdn"]["interfaces"]
        self.assertEqual(set(ports), {1, 2, 3})
        self.assertEqual([ports[n]["name"] for n in (1, 2, 3)],
                         ["sdna0", "sdnb0", "sdnc0"])
        self.assertEqual(ports[1]["native_vlan"], "s05_experimento")
        self.assertEqual(ports[2]["native_vlan"], "s05_experimento")
        self.assertEqual(ports[3]["native_vlan"], "s05_restringida")
        self.assertNotIn("routers", self.data)

    def test_no_se_declaran_puertos_de_gestion_ni_trunks_s02(self):
        body = CONFIG.read_text(encoding="utf-8")
        for forbidden in ("ens33", "vmnet8", "tr-sw", "s1p", "s2p",
                          "nl360-s02-sw-hq", "nl360-s02-sw-s1",
                          "nl360-s02-sw-s2", "10.70.", "10.71.", "10.72."):
            self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()
