"""S06-042: seguridad del ejecutor real HQ, tests offline sin tocar red."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

FILE=Path(__file__).resolve().parents[1]/"scripts/s06/controlador_hq_protegido.py"
SPEC=importlib.util.spec_from_file_location("s06_hq_guard",FILE)
assert SPEC and SPEC.loader
g=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class HQGuardTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        directory=Path(temp.name)
        runtime=directory/"run"
        runtime.mkdir(mode=0o700)
        patch=mock.patch.multiple(g,
            RUNTIME=runtime, STATE=runtime/"state.json",
            LOCK=runtime/"lock",
            INSTALL=directory/"libexec"/"s06-hq-controlador.py")
        patch.start()
        self.addCleanup(patch.stop)

    def seed(self, state="APPLIED"):
        v={"schema":g.SCHEMA,"token":"0123456789abcdef",
           "state":state,"ns_identity":[8,7],
           "target":f"{g.NS}/{g.DEV}","human_approval":True}
        g.save(v)
        return v

    def test_target_solo_cliente_hq(self):
        self.assertEqual(g.NS,"nl360-s02-h-hq-120")
        self.assertEqual(g.DEV,"eth0")
        self.assertEqual(g.PEER,"nl360-s02-sw-hq")
        self.assertEqual(g.CLIENT_IP,"10.70.20.20")
        self.assertEqual(g.HANDLE,"142:")
        self.assertEqual(g.LATENCY,40)
        self.assertEqual(g.TTL,35)
        self.assertNotEqual(g.DEV,"ens33")

    def test_aprobacion_literal_requerida(self):
        g.authorize(g.APPROVAL)
        for s in ("", "YES", "--approve", "AUTORIZO_HQ", "EXP-001"):
            with self.subTest(s=s), self.assertRaises(RuntimeError):
                g.authorize(s)

    def test_qdisc_baseline(self):
        with mock.patch.object(g,"run",return_value='[{"kind":"noqueue","root":true}]'):
            self.assertEqual(g.qdisc(),"BASELINE")

    def test_qdisc_nuestra_con_latency(self):
        def fake(*args):
            if "-j" in args:
                return '[{"kind":"netem","root":true,"handle":"142:"}]'
            return "qdisc netem 142: root refcnt 2 limit 1000 delay 40.0ms"
        with mock.patch.object(g,"run",side_effect=fake):
            self.assertEqual(g.qdisc(),"OWN_NETEM")

    def test_qdisc_foreign_rechazada(self):
        for handle,delay in (("141:","40ms"),("142:","50ms"),
                             ("142:","40.0s")):
            def fake(*args):
                if "-j" in args:
                    return json.dumps([{"kind":"netem","root":True,
                                        "handle":handle}])
                return "qdisc netem "+handle+" root delay "+delay
            with self.subTest(handle=handle,delay=delay), \
                 mock.patch.object(g,"run",side_effect=fake):
                self.assertEqual(g.qdisc(),"FOREIGN")

    def test_root_requerido(self):
        with mock.patch.object(g.os,"geteuid",return_value=1000):
            with self.assertRaisesRegex(RuntimeError,"root_required"):
                g.trusted_install()

    def test_estado_privado(self):
        d=self.seed()
        self.assertEqual(g.load(),d)
        self.assertEqual(g.STATE.stat().st_mode & 0o777,0o600)

    def test_estado_symlink_rechazado(self):
        v=Path(g.STATE.parent)/"other"
        v.write_text("{}")
        g.STATE.symlink_to(v)
        with self.assertRaisesRegex(RuntimeError,"symlink"):
            g.load()

    def test_lock_concurrente_bloquea(self):
        with g.exclusive():
            with self.assertRaisesRegex(RuntimeError,"concurrent"):
                with g.exclusive():
                    pass

    def test_timer_token_no_inyectable(self):
        args=g.timer_args("0123456789abcdef")
        self.assertEqual(args[0],"systemd-run")
        self.assertIn("--on-active=35s",args)
        self.assertEqual(args[-4:],(str(g.INSTALL),"expire",
                                    "--token","0123456789abcdef"))
        for token in ("","F"*16,"../foo","--help","123"):
            with self.assertRaises(ValueError):
                g.timer_args(token)

    def test_audit_no_cambia_red(self):
        with mock.patch.object(g,"check_management"), \
             mock.patch.object(g,"check_network",return_value={"namespace_id":[8,7]}), \
             mock.patch.object(g,"qdisc",return_value="BASELINE"), \
             mock.patch.object(g,"run") as calls:
            a=g.audit()
        self.assertEqual(a["namespace_id"],[8,7])
        calls.assert_not_called()

    def test_audit_rechaza_qdisc_foreign(self):
        with mock.patch.object(g,"check_management"), \
             mock.patch.object(g,"check_network",return_value={"namespace_id":[8,7]}), \
             mock.patch.object(g,"qdisc",return_value="FOREIGN"):
            with self.assertRaisesRegex(RuntimeError,"qdisc"):
                g.audit()

    def test_start_rechaza_estado_previo(self):
        self.seed()
        with self.assertRaisesRegex(RuntimeError,"previous_experiment"):
            g.start(g.APPROVAL)

    def test_start_arma_watchdog_antes_de_qdisc(self):
        calls=[]
        def fake(*args):
            calls.append(args)
            if args[0]=="systemctl":
                return "active\n"
            return ""
        with mock.patch.object(g,"check_management"), \
             mock.patch.object(g,"check_network",return_value={"namespace_id":[8,7]}), \
             mock.patch.object(g,"qdisc",side_effect=["BASELINE","OWN_NETEM"]), \
             mock.patch.object(g,"run",side_effect=fake):
            d=g.start(g.APPROVAL)
        self.assertEqual(d["state"],"APPLIED")
        i_timer=next(i for i,c in enumerate(calls) if c[0]=="systemd-run")
        i_add=next(i for i,c in enumerate(calls) if "netem" in c)
        self.assertLess(i_timer,i_add)
        self.assertIn(("ip","netns","exec",g.NS,"tc","qdisc","add",
                       "dev",g.DEV,"root","handle",g.HANDLE,
                       "netem","delay","40ms"),calls)

    def test_timer_no_activo_no_instala_qdisc(self):
        calls=[]
        def fake(*args):
            calls.append(args)
            return "inactive\n" if args[0]=="systemctl" else ""
        with mock.patch.object(g,"check_management"), \
             mock.patch.object(g,"check_network",return_value={"namespace_id":[8,7]}), \
             mock.patch.object(g,"qdisc",return_value="BASELINE"), \
             mock.patch.object(g,"run",side_effect=fake):
            with self.assertRaisesRegex(RuntimeError,"timer_not_active"):
                g.start(g.APPROVAL)
        self.assertFalse(any("netem" in a for c in calls for a in c))
        self.assertEqual(g.load()["state"],"ARMING")

    def test_expire_elimina_solo_qdisc_142_hq(self):
        self.seed()
        calls=[]
        with mock.patch.object(g,"netns_identity",return_value=[8,7]), \
             mock.patch.object(g,"qdisc",side_effect=["OWN_NETEM","BASELINE","BASELINE"]), \
             mock.patch.object(g,"run",side_effect=lambda *a:calls.append(a) or ""):
            state=g.expire("0123456789abcdef")
        self.assertEqual(state["state"],"RESTORED")
        self.assertIn(("ip","netns","exec",g.NS,
                       "tc","qdisc","del","dev",g.DEV,"root"),calls)

    def test_expire_foreign_no_borra(self):
        self.seed()
        with mock.patch.object(g,"netns_identity",return_value=[8,7]), \
             mock.patch.object(g,"qdisc",return_value="FOREIGN"), \
             mock.patch.object(g,"run") as runner:
            state=g.expire("0123456789abcdef")
        self.assertEqual(state["state"],"ESCALATED")
        runner.assert_not_called()

    def test_expire_requiere_identidad_namespace(self):
        self.seed()
        with mock.patch.object(g,"netns_identity",return_value=[8,9]), \
             mock.patch.object(g,"qdisc",return_value="BASELINE"):
            state=g.expire("0123456789abcdef")
        self.assertEqual(state["state"],"ESCALATED")

    def test_expire_baseline_previo_no_finge_rollback(self):
        self.seed("APPLY_PENDING")
        with mock.patch.object(g,"netns_identity",return_value=[8,7]), \
             mock.patch.object(g,"qdisc",return_value="BASELINE"):
            state=g.expire("0123456789abcdef")
        self.assertEqual(state["state"],"RESTORED_NO_CHANGE")

    def test_expire_token_invalido(self):
        self.seed()
        with self.assertRaisesRegex(RuntimeError,"token"):
            g.expire("abcdef0123456789")

    def test_restore_manual_registra_trigger_y_restaura(self):
        self.seed("APPLIED")
        with mock.patch.object(g,"netns_identity",return_value=[8,7]), \
             mock.patch.object(g,"qdisc",
                               side_effect=["OWN_NETEM","BASELINE","BASELINE"]), \
             mock.patch.object(g,"run"):
            state=g.expire("0123456789abcdef",trigger="MANUAL_APPROVED")
        self.assertEqual(state["state"],"RESTORED")
        self.assertEqual(state["restoration_trigger"],"MANUAL_APPROVED")

    def test_trigger_ajeno_rechazado(self):
        self.seed()
        with self.assertRaisesRegex(ValueError,"trigger_invalid"):
            g.expire("0123456789abcdef",trigger="FOREIGN")

    def test_expire_espera_lock(self):
        self.seed("APPLIED")
        with mock.patch.object(g,"exclusive",wraps=g.exclusive) as lock, \
             mock.patch.object(g,"netns_identity",return_value=[8,7]), \
             mock.patch.object(g,"qdisc",return_value="BASELINE"):
            g.expire("0123456789abcdef")
        lock.assert_called_once_with(wait=True)

    def test_cleanup_no_antes_restauracion(self):
        self.seed()
        with self.assertRaisesRegex(RuntimeError,"restore_must"):
            g.cleanup()

    def test_cleanup_tras_restored_no_toca_interfaces(self):
        self.seed("RESTORED")
        with mock.patch.object(g,"check_management"), \
             mock.patch.object(g,"check_network"), \
             mock.patch.object(g,"netns_identity",return_value=[8,7]), \
             mock.patch.object(g,"qdisc",return_value="BASELINE"), \
             mock.patch.object(g,"run") as runner:
            g.cleanup()
        self.assertIsNone(g.load())
        runner.assert_not_called()

    def test_codigo_no_crea_ns_nuevos(self):
        source=FILE.read_text()
        for s in ('"netns", "add"', '"netns", "del"',
                  '"link", "add"', '"link", "del"',
                  'subprocess.Popen(', 'shell=True'):
            self.assertNotIn(s,source)


if __name__=="__main__":
    unittest.main()
