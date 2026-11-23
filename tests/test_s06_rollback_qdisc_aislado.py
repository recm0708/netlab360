"""S06-038B: seguridad de qdisc en namespace efimero (solo tests offline)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

FILE = Path(__file__).resolve().parents[1] / "scripts/s06/rollback_qdisc_aislado.py"
SPEC = importlib.util.spec_from_file_location("s06_isolated_netem", FILE)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class IsolatedRollbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / "run"
        self.folder.mkdir(mode=0o700)
        patch = mock.patch.multiple(m,
            DIR=self.folder, STATE=self.folder / "state.json",
            LOCK=self.folder / "lock",
            INSTALL=Path(self.tmp.name) / "libexec" / "s06-rollback-isotest.py")
        patch.start()
        self.addCleanup(patch.stop)

    def seed(self, state="APPLIED"):
        entry = {
            "schema": m.SCHEMA,
            "token": "abcdef0123456789",
            "state": state,
            "namespace": m.NS, "device": m.IFACE,
            "ns_identity": [4, 12],
        }
        m.save_state(entry)
        return entry

    def test_target_no_es_produccion(self):
        self.assertEqual(m.NS, "nl360-s06-isotest")
        self.assertEqual(m.IFACE, "dummy0")
        self.assertNotEqual(m.NS, "nl360-s02-h-hq-120")
        self.assertNotEqual(m.IFACE, "ens33")
        self.assertEqual(m.TTL, 20)

    def test_timer_token_y_argumentos(self):
        cmd = m.timer_command("abcdef0123456789")
        self.assertEqual(cmd[0], "systemd-run")
        self.assertIn("--on-active=20s", cmd)
        self.assertEqual(cmd[-4:], [str(m.INSTALL), "expire",
                                    "--token", "abcdef0123456789"])
        self.assertNotIn("bash", cmd)
        self.assertNotIn("shell", cmd)

    def test_timer_rechaza_inyeccion(self):
        for token in ("", "../../root", "1234", "G" * 16, "--help" * 4):
            with self.subTest(token=token), self.assertRaises(ValueError):
                m.timer_command(token)

    def test_base_qdisc_valido(self):
        self.assertEqual(m.qdisc_state([{
            "root": True, "kind": "noqueue", "handle": "0:"
        }]), "BASELINE")

    def test_qdisc_propia(self):
        self.assertEqual(m.qdisc_state([{
            "root": True, "kind": "netem", "handle": "106:"
        }]), "OWN_NETEM")

    def test_qdisc_ajena_no_se_reconoce(self):
        for x in (
            [{"root": True, "kind": "netem", "handle": "55:"}],
            [{"root": True, "kind": "fq_codel", "handle": "106:"}],
            [{"root": True, "kind": "netem", "handle": "106:"},
             {"root": True, "kind": "noqueue"}],
            [],
        ):
            with self.subTest(qdisc=x):
                self.assertEqual(m.qdisc_state(x), "FOREIGN")

    def test_qdisc_no_json_rechazado(self):
        with self.assertRaises(ValueError):
            m.qdisc_state({})

    def test_preparar_rechaza_ns_preexistente(self):
        with mock.patch.object(m, "management"), \
             mock.patch.object(m, "namespace_names",
                               return_value={m.NS} | {f"other{i}" for i in range(20)}):
            with self.assertRaisesRegex(RuntimeError, "inventory"):
                m.prepare()
        self.assertIsNone(m.read_state())

    def test_preparar_rechaza_estado_preexistente(self):
        self.seed("PREPARED")
        with mock.patch.object(m, "management"):
            with self.assertRaisesRegex(RuntimeError, "previous_test"):
                m.prepare()

    def test_preparar_solo_espacio_sin_rutas(self):
        calls = []
        def fake_run(*args):
            calls.append(args)
            return ""
        with mock.patch.object(m, "run", side_effect=fake_run), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "namespace_names",
                               return_value={f"ns{i}" for i in range(21)}), \
             mock.patch.object(m, "inspect_dummy"), \
             mock.patch.object(m, "namespace_identity", return_value=[4, 12]), \
             mock.patch.object(m, "qdisc", return_value="BASELINE"):
            z = m.prepare()
        self.assertEqual(z["state"], "PREPARED")
        self.assertEqual(z["ns_identity"], [4, 12])
        self.assertIn(("ip", "netns", "add", m.NS), calls)
        self.assertIn(("ip", "-n", m.NS, "link", "add",
                       "dummy0", "type", "dummy"), calls)
        self.assertFalse(any("ens33" in str(q) for q in calls))
        self.assertFalse(any("netem" in str(q) for q in calls))

    def test_start_rechaza_sin_prepare(self):
        with self.assertRaisesRegex(RuntimeError, "not_prepared"):
            m.start()

    def test_start_arma_timer_antes_de_tc(self):
        self.seed("PREPARED")
        commands = []
        def fake_run(*args):
            commands.append(args)
            if args[0] == "systemctl":
                return "active\n"
            return ""
        with mock.patch.object(m, "run", side_effect=fake_run), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_namespace"), \
             mock.patch.object(m, "namespace_names",
                               return_value={f"ns{i}" for i in range(21)} | {m.NS}), \
             mock.patch.object(m, "qdisc", side_effect=("BASELINE", "OWN_NETEM")):
            state = m.start()
        self.assertEqual(state["state"], "APPLIED")
        idx_timer = next(i for i, args in enumerate(commands)
                         if args[0] == "systemd-run")
        idx_tc = next(i for i, args in enumerate(commands)
                      if "netem" in args)
        self.assertLess(idx_timer, idx_tc)
        self.assertEqual(m.read_state()["state"], "APPLIED")

    def test_start_timer_no_activo_impide_tc(self):
        self.seed("PREPARED")
        calls = []
        def fake_run(*args):
            calls.append(args)
            return "inactive" if args[0] == "systemctl" else ""
        with mock.patch.object(m, "run", side_effect=fake_run), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_namespace"), \
             mock.patch.object(m, "namespace_names",
                               return_value={f"ns{i}" for i in range(21)} | {m.NS}), \
             mock.patch.object(m, "qdisc", return_value="BASELINE"):
            with self.assertRaisesRegex(RuntimeError, "not_active"):
                m.start()
        self.assertFalse(any("netem" in q for args in calls for q in args))
        self.assertEqual(m.read_state()["state"], "PREPARED")

    def test_expire_restaura_solo_qdisc_propia(self):
        self.seed()
        calls = []
        def fake_run(*args):
            calls.append(args)
            return ""
        with mock.patch.object(m, "run", side_effect=fake_run), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_namespace"), \
             mock.patch.object(m, "qdisc",
                               side_effect=("OWN_NETEM", "BASELINE")):
            state = m.expire("abcdef0123456789")
        self.assertEqual(state["state"], "RESTORED")
        self.assertIn(("ip", "netns", "exec", m.NS, "tc", "qdisc",
                       "del", "dev", "dummy0", "root"), calls)

    def test_expire_no_borra_qdisc_ajena(self):
        self.seed()
        with mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_namespace"), \
             mock.patch.object(m, "qdisc", return_value="FOREIGN"), \
             mock.patch.object(m, "run") as runner:
            state = m.expire("abcdef0123456789")
        self.assertEqual(state["state"], "ESCALATED")
        runner.assert_not_called()

    def test_expire_sin_cambio_no_elimina_nada(self):
        self.seed("APPLY_PENDING")
        with mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_namespace"), \
             mock.patch.object(m, "qdisc", return_value="BASELINE"), \
             mock.patch.object(m, "run") as runner:
            state = m.expire("abcdef0123456789")
        self.assertEqual(state["state"], "RESTORED_NO_CHANGE")
        runner.assert_not_called()

    def test_expire_inconsistencia_identidad_escala(self):
        self.seed()
        with mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_namespace",
                               side_effect=RuntimeError("ns changed")), \
             mock.patch.object(m, "run") as runner:
            state = m.expire("abcdef0123456789")
        self.assertEqual(state["state"], "ESCALATED")
        runner.assert_not_called()

    def test_expire_token_ajeno_rechazado(self):
        self.seed()
        with self.assertRaisesRegex(RuntimeError, "foreign_timer"):
            m.expire("0123456789abcdef")

    def test_cleanup_prohibido_en_estado_activo(self):
        self.seed()
        with self.assertRaisesRegex(RuntimeError, "cannot_cleanup"):
            m.cleanup()

    def test_cleanup_solo_de_nuestra_ns(self):
        self.seed("RESTORED")
        calls = []
        with mock.patch.object(m, "run", side_effect=lambda *a: calls.append(a) or ""), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_namespace"), \
             mock.patch.object(m, "namespace_names", return_value=set()), \
             mock.patch.object(m, "qdisc", return_value="BASELINE"):
            m.cleanup()
        self.assertIn(("ip", "netns", "del", m.NS), calls)
        self.assertNotIn(("ip", "netns", "del", "nl360-s02-h-hq-120"), calls)
        self.assertIsNone(m.read_state())

    def test_lock_concurrente_bloquea(self):
        with m.exclusive():
            with self.assertRaisesRegex(RuntimeError, "concurrent"):
                with m.exclusive():
                    pass

    def test_guardia_requiere_root(self):
        with mock.patch.object(m.os, "geteuid", return_value=1000):
            with self.assertRaisesRegex(RuntimeError, "root_required"):
                m.verify_installed()

    def test_sin_etiquetado_automatico(self):
        source = FILE.read_text(encoding="utf-8")
        self.assertNotIn('"ground_truth_verified": True', source)
        self.assertNotIn("shell=True", source)
        self.assertNotIn("subprocess.Popen", source)


if __name__ == "__main__":
    unittest.main()
