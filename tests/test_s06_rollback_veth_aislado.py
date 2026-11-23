"""S06-040: gates de seguridad de watchdog sobre veth aislada, solo mock."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import signal
import tempfile
import unittest
from unittest import mock

FILE = Path(__file__).resolve().parents[1] / "scripts/s06/rollback_veth_aislado.py"
SPEC = importlib.util.spec_from_file_location("s06_veth_watchdog", FILE)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class VethIsolatedTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        run = self.folder / "run"
        run.mkdir(mode=0o700)
        patch = mock.patch.multiple(
            m, RUN_DIR=run, STATE=run/"state.json", LOCK=run/"lock",
            INSTALL=self.folder/"libexec"/"s06-veth-rollback.py"
        )
        patch.start()
        self.addCleanup(patch.stop)

    def seed(self, state="APPLIED") -> dict:
        data = {
            "schema": m.SCHEMA, "state": state, "token": "0123456789abcdef",
            "namespace_identity_a": [9, 12],
            "namespace_identity_b": [9, 13],
            "production_changed": False, "ground_truth_verified": False
        }
        m.save_state(data)
        return data

    def test_namespaces_no_son_productivos(self):
        self.assertEqual(m.NSA, "nl360-s06-veth-a")
        self.assertEqual(m.NSB, "nl360-s06-veth-b")
        self.assertEqual(m.IFA, "s06va0")
        self.assertEqual(m.IFB, "s06vb0")
        self.assertNotIn("nl360-s02-h-hq-120", (m.NSA, m.NSB))
        self.assertEqual(m.TTL, 25)

    def test_timer_preparado_con_token_fijo(self):
        args = m.timer_args("0123456789abcdef")
        self.assertEqual(args[0], "systemd-run")
        self.assertIn("--on-active=25s", args)
        self.assertEqual(args[-4:], (str(m.INSTALL), "expire",
                                      "--token", "0123456789abcdef"))

    def test_timer_rechaza_token_inyectado(self):
        for s in ("", "../etc", "--unit=bad", "F"*16, "abcde"):
            with self.subTest(s=s), self.assertRaises(ValueError):
                m.timer_args(s)

    def test_base_y_qdisc_propia(self):
        self.assertEqual(m.qdisc_state([{
            "kind": "noqueue", "root": True, "handle": "0:"
        }]), "BASELINE")
        self.assertEqual(m.qdisc_state([{
            "kind": "netem", "root": True, "handle": "140:"
        }]), "OWN_NETEM")

    def test_qdisc_ajena_rechazada(self):
        for v in (
            [], [{"kind":"netem","root":True,"handle":"106:"}],
            [{"kind":"fq_codel","root":True,"handle":"140:"}],
            [{"kind":"noqueue","root":True},
             {"kind":"netem","root":True,"handle":"140:"}],
        ):
            with self.subTest(qdisc=v):
                self.assertEqual(m.qdisc_state(v), "FOREIGN")

    def test_qdisc_formato_ajeno_rechazado(self):
        with self.assertRaises(ValueError):
            m.qdisc_state({})

    def test_guardia_exige_root(self):
        with mock.patch.object(m.os, "geteuid", return_value=1000):
            with self.assertRaisesRegex(RuntimeError, "root_required"):
                m.trusted_install()

    def test_estado_privado_y_atomicidad(self):
        data = self.seed()
        self.assertEqual(m.read_state(), data)
        self.assertEqual(m.STATE.stat().st_mode & 0o777, 0o600)

    def test_estado_symlink_rechazado(self):
        t = self.folder / "outside"
        t.write_text("{}")
        m.STATE.symlink_to(t)
        with self.assertRaisesRegex(RuntimeError, "symlink"):
            m.read_state()

    def test_flock_rechaza_concurrencia(self):
        with m.exclusive():
            with self.assertRaisesRegex(RuntimeError, "concurrent"):
                with m.exclusive():
                    pass

    def test_gestion_alterada_es_gate(self):
        def fake(*args):
            if args == ("ip","-4","-o","addr","show","dev","ens33"):
                return "192.168.47.40/24"
            if args == ("ip","-4","route","show","default"):
                return "default via 192.168.47.3 dev ens33"
            raise AssertionError(args)
        with mock.patch.object(m, "run", side_effect=fake):
            with self.assertRaisesRegex(RuntimeError, "management"):
                m.management()

    def test_prepare_rechaza_estado_existente(self):
        self.seed("PREPARED")
        with mock.patch.object(m, "management"):
            with self.assertRaisesRegex(RuntimeError, "previous_test"):
                m.prepare()

    def test_prepare_rechaza_inventario_no_baseline(self):
        with mock.patch.object(m, "management"), \
             mock.patch.object(m, "names", return_value={m.NSA}):
            with self.assertRaisesRegex(RuntimeError, "inventory"):
                m.prepare()
        self.assertIsNone(m.read_state())

    def test_prepare_crea_solo_veth_aislada_y_sin_ipv6(self):
        calls = []
        def fake(*args):
            calls.append(args)
            return ""
        with mock.patch.object(m, "run", side_effect=fake), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "names",
                return_value={f"ns-{i}" for i in range(21)}), \
             mock.patch.object(m, "identity", side_effect=[[9,12],[9,13]]), \
             mock.patch.object(m, "inspect_both", return_value={}), \
             mock.patch.object(m, "current_qdisc", return_value="BASELINE"), \
             mock.patch.object(m, "probe", return_value="3 received"):
            result = m.prepare()
        self.assertEqual(result["state"], "PREPARED")
        self.assertIn(("ip","netns","add",m.NSA), calls)
        self.assertIn(("ip","netns","add",m.NSB), calls)
        self.assertIn(("ip","-n",m.NSA,"link","add",m.IFA,
                       "type","veth","peer","name",m.IFB), calls)
        self.assertFalse(any("ens33" in str(c) for c in calls))
        self.assertFalse(any("qdisc" in c for a in calls for c in a))
        self.assertEqual(len([a for a in calls if "disable_ipv6=1" in " ".join(a)]), 2)

    def test_start_requiere_prepare(self):
        with self.assertRaisesRegex(RuntimeError, "not_prepared"):
            m.start()

    def test_start_arma_temporizador_antes_de_netem(self):
        self.seed("PREPARED")
        commands=[]
        def fake(*args):
            commands.append(args)
            if args[0] == "systemctl":
                return "active\n"
            return ""
        with mock.patch.object(m, "run", side_effect=fake), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_pair"), \
             mock.patch.object(m, "current_qdisc",
                side_effect=["BASELINE","OWN_NETEM"]):
            result=m.start()
        self.assertEqual(result["state"], "APPLIED")
        timer_i=next(i for i,a in enumerate(commands) if a[0]=="systemd-run")
        tc_i=next(i for i,a in enumerate(commands) if "netem" in a)
        self.assertLess(timer_i,tc_i)
        self.assertEqual(commands[tc_i][4], "tc")
        self.assertIn(m.IFA,commands[tc_i])

    def test_timer_inactivo_impide_aplicar_tc(self):
        self.seed("PREPARED")
        commands=[]
        def fake(*args):
            commands.append(args)
            return "inactive\n" if args[0]=="systemctl" else ""
        with mock.patch.object(m, "run", side_effect=fake), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_pair"), \
             mock.patch.object(m, "current_qdisc", return_value="BASELINE"):
            with self.assertRaisesRegex(RuntimeError, "not_active"):
                m.start()
        self.assertEqual(m.read_state()["state"], "PREPARED")
        self.assertFalse(any("netem" in a for cmd in commands for a in cmd))

    def test_simula_muerte_real_del_controlador_SIGKILL(self):
        self.seed("PREPARED")
        def fake(*args):
            return "active\n" if args[0] == "systemctl" else ""
        with mock.patch.object(m, "run", side_effect=fake), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_pair"), \
             mock.patch.object(m, "current_qdisc",
                side_effect=["BASELINE","OWN_NETEM"]), \
             mock.patch.object(m.os, "kill") as killer:
            m.start(crash=True)
        killer.assert_called_once_with(m.os.getpid(),signal.SIGKILL)
        self.assertEqual(m.read_state()["state"],"APPLIED")

    def test_expire_solo_restauracion_propia(self):
        self.seed()
        commands=[]
        with mock.patch.object(m, "run",
                               side_effect=lambda *a: commands.append(a) or ""), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_pair"), \
             mock.patch.object(m, "current_qdisc",
                               side_effect=["OWN_NETEM","BASELINE"]), \
             mock.patch.object(m, "probe",return_value="3 received"):
            result=m.expire("0123456789abcdef")
        self.assertEqual(result["state"],"RESTORED")
        self.assertIn(("ip","netns","exec",m.NSA,"tc","qdisc","del",
                       "dev",m.IFA,"root"),commands)

    def test_expire_qdisc_ajena_escala(self):
        self.seed()
        with mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_pair"), \
             mock.patch.object(m, "current_qdisc",return_value="FOREIGN"), \
             mock.patch.object(m, "run") as cmd:
            result=m.expire("0123456789abcdef")
        self.assertEqual(result["state"],"ESCALATED")
        cmd.assert_not_called()

    def test_expire_sin_cambio_no_finge_restauracion(self):
        self.seed("APPLY_PENDING")
        with mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_pair"), \
             mock.patch.object(m, "current_qdisc",return_value="BASELINE"):
            result=m.expire("0123456789abcdef")
        self.assertEqual(result["state"],"RESTORED_NO_CHANGE")

    def test_expire_token_ajeno_rechazado(self):
        self.seed()
        with self.assertRaisesRegex(RuntimeError,"foreign_timer"):
            m.expire("abcdef0123456789")

    def test_expire_espera_lock_para_no_perder_rollback(self):
        self.seed()
        with mock.patch.object(m, "exclusive", wraps=m.exclusive) as lock, \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_pair"), \
             mock.patch.object(m, "current_qdisc",return_value="BASELINE"):
            m.expire("0123456789abcdef")
        lock.assert_called_once_with(wait=True)

    def test_cleanup_no_permitido_sin_RESTORED(self):
        self.seed("APPLIED")
        with self.assertRaisesRegex(RuntimeError,"cannot_cleanup"):
            m.cleanup()

    def test_cleanup_elimina_solo_ns_temporales(self):
        self.seed("RESTORED")
        calls=[]
        with mock.patch.object(m, "run",
             side_effect=lambda *a: calls.append(a) or ""), \
             mock.patch.object(m, "management"), \
             mock.patch.object(m, "verify_owned_pair"), \
             mock.patch.object(m, "current_qdisc",return_value="BASELINE"), \
             mock.patch.object(m, "probe",return_value="3 received"), \
             mock.patch.object(m, "names",
                               return_value={f"ns-{i}" for i in range(21)}):
            m.cleanup()
        self.assertIn(("ip","netns","del",m.NSA),calls)
        self.assertIn(("ip","netns","del",m.NSB),calls)
        self.assertNotIn(("ip","netns","del","nl360-s02-h-hq-120"),calls)
        self.assertIsNone(m.read_state())

    def test_falla_baseline_en_expire_es_escalamiento(self):
        self.seed()
        with mock.patch.object(m, "management",
                               side_effect=RuntimeError("management")), \
             mock.patch.object(m, "run") as runner:
            data=m.expire("0123456789abcdef")
        self.assertEqual(data["state"],"ESCALATED")
        runner.assert_not_called()

    def test_no_etiqueta_produccion(self):
        source=FILE.read_text(encoding="utf-8")
        self.assertIn('"ground_truth_verified": False',source)
        self.assertIn('"production_changed": False',source)
        self.assertNotIn("shell=True",source)
        self.assertNotIn("subprocess.Popen(",source)


if __name__ == "__main__":
    unittest.main()
