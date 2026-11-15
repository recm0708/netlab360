"""Contrato offline para lotes 145A/145B: no tocar redes, asegurar rollback."""
from __future__ import annotations
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts/operacion/s05-lote-145a-instalar-observador.sh"
ROLLOUT = ROOT / "scripts/operacion/s05-lote-145b-activar-noc.sh"


class NocRolloutBashTests(unittest.TestCase):
    def test_sintaxis_de_los_dos_lotes(self):
        for path in (INSTALL, ROLLOUT):
            with self.subTest(path=path):
                r = subprocess.run(["bash", "-n", str(path)],
                                   capture_output=True, text=True, timeout=8)
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_instalacion_atómica_y_rollback(self):
        text = INSTALL.read_text()
        for key in (
            "trap rollback EXIT", "MUTATED=1", "ACCEPTED=1",
            "BACKUP=/var/backups/netlab360/",
            "sha256sum", "sudo -n mv -f -T",
            "ROOT_HELPER=OK_FIB_LACP_SDN",
            "LOTE145A_HELPER_ROOT_NOC=OK",
            '"BACKUP" "$BIN"'
        ):
            self.assertIn(key, text)
        self.assertNotIn("systemctl restart", text)

    def test_145b_reinicia_solo_noc_y_preserva_rollback(self):
        text = ROLLOUT.read_text()
        self.assertIn("trap rollback EXIT", text)
        self.assertIn("LOTE145B_NOC_LACP_SDN=OK", text)
        self.assertIn("S05_NOC_DOS_MUESTRAS_LACP_SDN=OK", text)
        for line in text.splitlines():
            if "systemctl restart" in line:
                self.assertIn("netlab360-s05-noc", line)

    def test_ninguno_modifica_redes_ni_hace_reboot(self):
        for path in (INSTALL, ROLLOUT):
            text = path.read_text()
            for forbidden in (
                "clear", "qm stop", "reboot",
                "docker stop", "docker restart",
                "ovs-vsctl del-br", "netns delete",
                "ip link set", "ip route replace",
                "systemctl restart netlab360-s05-ha",
                "systemctl restart netlab360-s04",
            ):
                with self.subTest(file=path.name, forbidden=forbidden):
                    self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
