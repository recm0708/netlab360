"""S06-038A: tests offline del guard privilegiado NOOP.

No requiere sudo, systemd, root, namespaces ni acceso a interfaces.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

TARGET = Path(__file__).resolve().parents[1] / "scripts/s06/guardia_protegida.py"
SPEC = importlib.util.spec_from_file_location("s06_guard_root", TARGET)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

NIC = json.dumps([{
    "ifname": "eth0", "operstate": "UP",
    "addr_info": [{"family": "inet", "local": "10.70.20.20", "prefixlen": 24}]
}])
ROUTE = json.dumps([{
    "dst": "default", "gateway": "10.70.20.1", "dev": "eth0"
}])
QDISC = json.dumps([{"kind": "noqueue", "root": True, "handle": "0:"}])


def readonly_response(cmd):
    if cmd == ("ip", "-4", "-o", "addr", "show", "dev", "ens33"):
        return "2: ens33 inet 192.168.47.40/24 scope global ens33"
    if cmd == ("ip", "-4", "route", "show", "default"):
        return "default via 192.168.47.2 dev ens33 proto static metric 100"
    if cmd == ("ip", "netns", "list"):
        return "\n".join(
            ["nl360-s02-h-hq-120"] + [f"ns-{i}" for i in range(20)]
        )
    if cmd == ("ip", "-n", m.NAMESPACE, "-j", "addr", "show", "dev", "eth0"):
        return NIC
    if cmd == ("ip", "-n", m.NAMESPACE, "-j", "route", "show", "default"):
        return ROUTE
    if cmd == ("ip", "netns", "exec", m.NAMESPACE,
               "tc", "-j", "qdisc", "show", "dev", m.DEVICE):
        return QDISC
    raise AssertionError(f"unexpected command {cmd}")


class GuardRootNoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = Path(self.tmp.name) / "run"
        self.run_dir.mkdir(mode=0o700)
        self.install = Path(self.tmp.name) / "install" / "s06-guardia.py"
        self.install.parent.mkdir()
        self.install.write_text("root test")
        self.patch = mock.patch.multiple(
            m,
            RUN_DIR=self.run_dir,
            STATE=self.run_dir / "guardia.json",
            LOCK=self.run_dir / "guardia.lock",
            INSTALL=self.install,
        )
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_catalogo_fijo(self):
        self.assertEqual(m.NAMESPACE, "nl360-s02-h-hq-120")
        self.assertEqual(m.DEVICE, "eth0")
        self.assertEqual(m.MIN_TTL, 5)
        self.assertEqual(m.MAX_TTL, 30)

    def test_timer_noop_con_destino_fijo(self):
        cmd = m.timer_args("0123456789abcdef", 8)
        self.assertEqual(cmd[0], "systemd-run")
        self.assertIn("--on-active=8s", cmd)
        self.assertEqual(cmd[-4:], [
            str(self.install), "expire", "--token", "0123456789abcdef"
        ])
        self.assertNotIn("ens33", " ".join(cmd))
        self.assertNotIn("qdisc", " ".join(cmd))

    def test_timer_rechaza_token_invalido(self):
        for token in ("../etc", "G" * 16, "", "1" * 8):
            with self.subTest(token=token):
                with self.assertRaises(ValueError):
                    m.timer_args(token, 8)

    def test_timer_rechaza_ttl_extremo(self):
        for ttl in (0, 4, 31, 1000, True):
            with self.subTest(ttl=ttl):
                with self.assertRaises(ValueError):
                    m.timer_args("0123456789abcdef", ttl)

    def test_preflight_sano(self):
        with mock.patch.object(m, "command", side_effect=readonly_response):
            state = m.baseline()
        self.assertEqual(state["qdisc"], "noqueue")
        self.assertEqual(state["management"], m.HOST_IP)
        self.assertFalse(state["network_changes"])

    def test_preflight_rechaza_management_cambiada(self):
        def other(*args):
            ret = readonly_response(args)
            if args == ("ip", "-4", "route", "show", "default"):
                return ret.replace("192.168.47.2", "192.168.47.3")
            return ret
        with mock.patch.object(m, "command", side_effect=other):
            with self.assertRaisesRegex(RuntimeError, "management"):
                m.baseline()

    def test_preflight_rechaza_qdisc_ajena(self):
        def other(*args):
            ret = readonly_response(args)
            if args[-4:] == ("qdisc", "show", "dev", "eth0"):
                return json.dumps([{"kind": "netem", "root": True}])
            return ret
        with mock.patch.object(m, "command", side_effect=other):
            with self.assertRaisesRegex(RuntimeError, "qdisc"):
                m.baseline()

    def test_lectura_estado_sin_archivo(self):
        self.assertIsNone(m.read_state())

    def test_escritura_atomicamente_conserva_modo(self):
        plan = {"schema": m.SCHEMA, "token": "0123456789abcdef", "state": "ARMED_NOOP"}
        m.write_state(plan)
        self.assertEqual(m.read_state(), plan)
        self.assertEqual(m.STATE.stat().st_mode & 0o777, 0o600)

    def test_estado_symlink_rechazado(self):
        outside = self.run_dir / "outside.json"
        outside.write_text("{}")
        m.STATE.symlink_to(outside)
        with self.assertRaisesRegex(RuntimeError, "symlink"):
            m.read_state()
        with self.assertRaisesRegex(RuntimeError, "symlink"):
            m.write_state({"schema": m.SCHEMA})

    def test_estado_schema_ajeno_rechazado(self):
        m.STATE.write_text('{"schema":"another"}')
        m.STATE.chmod(0o600)
        with self.assertRaisesRegex(RuntimeError, "schema"):
            m.read_state()

    def test_estado_permiso_inseguro_rechazado(self):
        m.STATE.write_text('{"schema":"' + m.SCHEMA + '"}')
        m.STATE.chmod(0o666)
        with self.assertRaisesRegex(RuntimeError, "root_private"):
            m.read_state()

    def test_bloqueo_concurrente_fail_closed(self):
        import fcntl
        with m.exclusive():
            with self.assertRaisesRegex(RuntimeError, "concurrent"):
                with m.exclusive():
                    pass

    def test_expire_sin_token_rechazado(self):
        with self.assertRaisesRegex(ValueError, "invalid_token"):
            m.expire("bad")

    def test_expire_con_token_ajeno_no_escribe(self):
        plan = {"schema": m.SCHEMA, "token": "0123456789abcdef", "state": "ARMED_NOOP"}
        m.write_state(plan)
        with self.assertRaisesRegex(RuntimeError, "mismatch"):
            m.expire("aaaaaaaaaaaaaaaa")
        self.assertEqual(m.read_state(), plan)

    def test_expire_requiere_estado_armado(self):
        plan = {"schema": m.SCHEMA, "token": "0123456789abcdef", "state": "ARMING"}
        m.write_state(plan)
        with self.assertRaisesRegex(RuntimeError, "timer_state"):
            m.expire("0123456789abcdef")

    def test_expire_no_mutacion_de_red(self):
        plan = {"schema": m.SCHEMA, "token": "0123456789abcdef",
                "state": "ARMED_NOOP", "network_changes": False}
        m.write_state(plan)
        with mock.patch.object(m, "baseline", return_value={"qdisc": "noqueue"}):
            result = m.expire("0123456789abcdef")
        self.assertEqual(result["state"], "EXPIRED_NOOP")
        self.assertFalse(result["network_changes"])
        self.assertEqual(m.read_state()["state"], "EXPIRED_NOOP")

    def test_expire_baseline_falla_escala(self):
        plan = {"schema": m.SCHEMA, "token": "0123456789abcdef",
                "state": "ARMED_NOOP", "network_changes": False}
        m.write_state(plan)
        with mock.patch.object(m, "baseline", side_effect=RuntimeError("changed")):
            result = m.expire("0123456789abcdef")
        self.assertEqual(result["state"], "ESCALATED")
        self.assertFalse(result["network_changes"])

    def test_limpieza_solo_despues_expiracion(self):
        plan = {"schema": m.SCHEMA, "token": "0123456789abcdef",
                "state": "ARMED_NOOP"}
        m.write_state(plan)
        with self.assertRaisesRegex(RuntimeError, "cannot_clean"):
            m.cleanup()
        self.assertTrue(m.STATE.exists())
        plan["state"] = "EXPIRED_NOOP"
        m.write_state(plan)
        with mock.patch.object(m, "baseline", return_value={"qdisc": "noqueue"}):
            m.cleanup()
        self.assertFalse(m.STATE.exists())

    def test_codigo_no_contiene_mutaciones_de_qdisc(self):
        c = TARGET.read_text()
        for forbidden in ("qdisc add", "qdisc del", "qdisc replace",
                          "tc qdisc add", "tc qdisc change", "shell=True"):
            self.assertNotIn(forbidden, c)
        self.assertNotIn("subprocess.Popen(", c)

    def test_usuario_normal_no_puede_ejecutar(self):
        with mock.patch.object(m.os, "geteuid", return_value=1000):
            with self.assertRaisesRegex(RuntimeError, "root_required"):
                m.trusted_install()


if __name__ == "__main__":
    unittest.main()
