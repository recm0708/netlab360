"""Reglas estáticas del único ensayo HTTP #32, sin ejecutar systemctl."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/operacion/s05-lote-ha-instancia-con-watchdog.sh"


class TestGuardedHA(unittest.TestCase):
    def test_script_only_modifies_backend_and_guarded_timer(self):
        content = PATH.read_text(encoding="utf-8")
        self.assertIn('BACKEND="netlab360-s05-ha-backend-hq.service"', content)
        self.assertIn('"--run" && "${2:-}" == "--confirm-fault"', content)
        self.assertIn('systemd-run --unit="$SUFFIX" --on-active=120s', content)
        self.assertIn('systemctl start "$BACKEND"', content)
        self.assertIn('test "$(systemctl is-active "$BACKEND")" = active', content)
        self.assertIn('systemctl stop "$TIMER"', content)
        for forbidden in (
            "docker stop", "ip link set", "netns delete",
            "systemctl reboot", "ovs-vsctl del-br", "route replace"
        ):
            self.assertNotIn(forbidden, content)

    def test_precheck_does_not_trigger_trial(self):
        code = PATH.read_text(encoding="utf-8")
        self.assertIn('if [[ "$MODE" == "--precheck" ]]; then', code)
        self.assertIn("exit 0", code)
        self.assertIn("S05_HA_INSTANCIA_MODO=SOLO_LECTURA", code)


if __name__ == "__main__":
    unittest.main()
