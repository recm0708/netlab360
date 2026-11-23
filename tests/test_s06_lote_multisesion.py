"""S06-043: tests offline de secuenciación segura de sesiones en HQ real."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

FILE=Path(__file__).resolve().parents[1]/"scripts/s06/ejecutar_lote_hq.py"
SPEC=importlib.util.spec_from_file_location("s06_multisesion",FILE)
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def meta_session(folder: Path, token="0123456789abcdef",
                 label="DEGRADED", windows=4):
    folder.mkdir(parents=True)
    rows=[]
    for i in range(1,windows+1):
        x={
            "schema":m.WINDOW_SCHEMA, "session_id":folder.name,
            "window_index":i, "ground_truth_label":label,
            "ground_truth_verified":True,
            "label_scope":"HQ_CLIENT_EGRESS_NETWORK_STATE",
            "network_changes_by_collector":False,
            "before":{"routes_verified":True, "guard":{
                "state":"APPLIED" if label=="DEGRADED" else "RESTORED",
                "qdisc":"OWN_NETEM" if label=="DEGRADED" else "BASELINE",
                "token":token
            }},
            "after":{"routes_verified":True, "guard":{
                "state":"APPLIED" if label=="DEGRADED" else "RESTORED",
                "qdisc":"OWN_NETEM" if label=="DEGRADED" else "BASELINE",
                "token":token
            }},
            "measurements":[
                {"probe_id":p,"result":{
                    "measurement_valid":True,"rtt_avg_ms":40 if label=="DEGRADED" else 0.1
                }} for p in ("HQ_A_S1","HQ_A_S2")
            ],
        }
        rows.append(x)
    raw="".join(json.dumps(x)+"\n" for x in rows).encode()
    (folder/"ventanas.jsonl").write_bytes(raw)
    (folder/"metadata.json").write_text(json.dumps({
        "schema":m.WINDOW_SCHEMA,"session_id":folder.name,
        "controller_token":token,"expected_class":label,
        "status":"complete","samples_recorded":windows,
        "verified":windows,"unknown":0,
        "data_digest_sha256":hashlib.sha256(raw).hexdigest()
    }))
    return "S06_042_SESION="+folder.name+"\nS06_042_DIRECTORIO="+str(folder)+"\n"


class MultiSessionTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        patch=mock.patch.object(m,"BASE",Path(temp.name))
        patch.start()
        self.addCleanup(patch.stop)

    def test_target_real_no_interfaces_aisladas(self):
        self.assertEqual(m.CLIENT,"nl360-s02-h-hq-120/eth0")
        self.assertEqual(m.EXE,"/usr/local/libexec/netlab360/s06-hq-controlador.py")
        self.assertEqual(m.ROUND_DEGRADED,4)
        self.assertEqual(m.ROUND_RECOVERY,6)
        source=FILE.read_text()
        for token in ('"netns", "add"', '"netns", "del"',
                      '"link", "add"', '"link", "del"', 'shell=True'):
            self.assertNotIn(token,source)

    def test_ciclos_solo_dos_o_tres(self):
        with mock.patch.object(m.os,"geteuid",return_value=1000):
            for cycles in (0,1,4):
                with self.subTest(cycles=cycles),self.assertRaises(ValueError):
                    m.orchestrate(cycles,m.APPROVAL)

    def test_aprobacion_explicita_obligatoria(self):
        with mock.patch.object(m.os,"geteuid",return_value=1000):
            with self.assertRaisesRegex(RuntimeError,"approval"):
                m.orchestrate(3,"YES")

    def test_prohibe_root_global(self):
        with mock.patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(RuntimeError,"unprivileged"):
                m.orchestrate(3,m.APPROVAL)

    def test_no_puede_repetir_estado_applied(self):
        with mock.patch.object(m,"guard_state",return_value={
            "state":"APPLIED","qdisc":"OWN_NETEM"}):
            with self.assertRaisesRegex(RuntimeError,"previous_cycle_not_clean"):
                m.check_ready()

    def test_no_puede_repetir_estado_restored_sin_cleanup(self):
        with mock.patch.object(m,"guard_state",return_value={
            "state":"RESTORED","qdisc":"BASELINE"}):
            with self.assertRaisesRegex(RuntimeError,"previous_cycle_not_clean"):
                m.check_ready()

    def test_check_ready_pide_audit_root(self):
        with mock.patch.object(m,"guard_state",return_value={
                "state":"NONE","qdisc":"BASELINE"}), \
             mock.patch.object(m,"guard",return_value="S06_042_GUARD_AUDIT=OK_READONLY\n") as g:
            m.check_ready()
        g.assert_called_once_with("audit")

    def test_guard_prefix_cerrado(self):
        with mock.patch.object(m,"run",return_value="OK") as caller:
            m.guard("audit")
        caller.assert_called_once_with(["sudo","-n",m.EXE,"audit"])

    def test_guard_parseado_rechaza_otro_target(self):
        with mock.patch.object(m,"guard",return_value=(
            'S06_042_STATE_JSON={"schema":"NETLAB360_S06_HQ_EXPERIMENT_GUARD_V1",'
            '"target":"other/eth0","state":"NONE"}\n'
        )):
            with self.assertRaisesRegex(RuntimeError,"target"):
                m.guard_state()

    def test_sesion_degradada_valida(self):
        folder=m.BASE/"datasets/raw"/"S06_WINDOW_DEGRADED_20261123T070344Z_abcdef"
        log=meta_session(folder)
        v=m.validated_session(log,"DEGRADED","0123456789abcdef",4)
        self.assertEqual(v["windows"],4)
        self.assertAlmostEqual(v["rtt_avg_ms"],40)

    def test_sesion_recovery_valida(self):
        folder=m.BASE/"datasets/raw"/"S06_WINDOW_RECOVERY_20261123T070420Z_abcdef"
        log=meta_session(folder,label="RECOVERY",windows=6)
        v=m.validated_session(log,"RECOVERY","0123456789abcdef",6)
        self.assertEqual(v["measurement_count"],12)

    def test_ventana_unknown_bloquea(self):
        folder=m.BASE/"datasets/raw"/"S06_WINDOW_DEGRADED_20261123T070344Z_abcdef"
        log=meta_session(folder)
        lines=(folder/"ventanas.jsonl").read_text().splitlines()
        row=json.loads(lines[0]);row["ground_truth_label"]="UNKNOWN"
        lines[0]=json.dumps(row);raw=("\n".join(lines)+"\n").encode()
        (folder/"ventanas.jsonl").write_bytes(raw)
        meta=json.loads((folder/"metadata.json").read_text())
        meta["data_digest_sha256"]=hashlib.sha256(raw).hexdigest()
        (folder/"metadata.json").write_text(json.dumps(meta))
        with self.assertRaisesRegex(RuntimeError,"labeled"):
            m.validated_session(log,"DEGRADED","0123456789abcdef",4)

    def test_checksum_fuente_alterada_bloquea(self):
        folder=m.BASE/"datasets/raw"/"S06_WINDOW_DEGRADED_20261123T070344Z_abcdef"
        log=meta_session(folder)
        (folder/"ventanas.jsonl").write_text("evil")
        with self.assertRaises(RuntimeError):
            m.validated_session(log,"DEGRADED","0123456789abcdef",4)

    def test_token_ajeno_bloquea(self):
        folder=m.BASE/"datasets/raw"/"S06_WINDOW_DEGRADED_20261123T070344Z_abcdef"
        log=meta_session(folder)
        with self.assertRaisesRegex(RuntimeError,"ground_truth"):
            m.validated_session(log,"DEGRADED","0000000000000000",4)

    def test_symlink_ventanas_bloquea(self):
        folder=m.BASE/"datasets/raw"/"S06_WINDOW_DEGRADED_20261123T070344Z_abcdef"
        log=meta_session(folder)
        old=folder/"ventanas.jsonl";other=folder/"other.jsonl"
        old.rename(other);old.symlink_to(other)
        with self.assertRaisesRegex(RuntimeError,"symlink"):
            m.validated_session(log,"DEGRADED","0123456789abcdef",4)

    def test_watchdog_escala_no_limpia(self):
        with mock.patch.object(m,"guard_state",return_value={
            "token":"0123456789abcdef","state":"ESCALATED"}):
            with self.assertRaisesRegex(RuntimeError,"ESCALATED"):
                m.wait_recovery("0123456789abcdef",timeout=1)

    def test_watchdog_requiere_trigger_watchdog(self):
        with mock.patch.object(m,"guard_state",return_value={
            "token":"0123456789abcdef","state":"RESTORED",
            "qdisc":"BASELINE","restoration_trigger":"MANUAL_APPROVED",
            "final_qdisc_state":"BASELINE"}):
            with self.assertRaisesRegex(RuntimeError,"not_autonomous"):
                m.wait_recovery("0123456789abcdef",timeout=1)

    def test_watchdog_exito(self):
        with mock.patch.object(m,"guard_state",return_value={
            "token":"0123456789abcdef","state":"RESTORED",
            "qdisc":"BASELINE","restoration_trigger":"WATCHDOG",
            "final_qdisc_state":"BASELINE"}):
            self.assertEqual(m.wait_recovery("0123456789abcdef")["state"],
                             "RESTORED")

    def test_maniesto_privado(self):
        path=m.BASE/"manifest.json"
        m.save_manifest(path,{"schema":m.SCHEMA,"cycles":[]})
        self.assertEqual(path.stat().st_mode & 0o777,0o600)

    def test_no_ciclo_siguiente_si_primero_falla(self):
        seen=[]
        def f(index,folder,report):
            seen.append(index)
            raise RuntimeError("synthetic_failure")
        with mock.patch.object(m.os,"geteuid",return_value=1000), \
             mock.patch.object(m,"check_ready"), \
             mock.patch.object(m,"run_one",side_effect=f):
            with self.assertRaisesRegex(RuntimeError,"synthetic_failure"):
                m.orchestrate(3,m.APPROVAL)
        self.assertEqual(seen,[1])

    def test_tres_ciclos_exitosos_en_mock(self):
        def fake(index,folder,report):
            row={"number":index,"status":"complete",
                 "degraded":{"windows":4},
                 "recovery":{"windows":6}}
            report["cycles"].append(row)
            return row
        with mock.patch.object(m.os,"geteuid",return_value=1000), \
             mock.patch.object(m,"check_ready"), \
             mock.patch.object(m,"run_one",side_effect=fake) as runner:
            v=m.orchestrate(3,m.APPROVAL)
        self.assertEqual(v["status"],"complete")
        self.assertEqual(runner.call_count,3)


if __name__=="__main__":
    unittest.main()
