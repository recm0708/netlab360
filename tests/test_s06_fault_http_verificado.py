"""S06 FAULT HTTP HQ: verificaciones de procedencia, seguridad y restauración."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

SOURCE=Path(__file__).resolve().parents[1]/"scripts/s06/validar_fault_http_s06.py"
spec=importlib.util.spec_from_file_location("s06_fault_http_reader",SOURCE)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sample(label,i):
    active="BACKEND_S1" if label=="fault" else "BACKEND_HQ"
    return {
        "observed_utc":f"2026-11-23T17:00:{i:02d}.000+00:00",
        "ha_available":True,"active":active,
        "path":"RESPALDO" if label=="fault" else "PRINCIPAL",
        "status":"running","fib_s1":"s1p","fib_s2":"s2p",
        "nodes":{"FRONTAL_HQ":"running",
                 "BACKEND_HQ":"stopped" if label=="fault" else "running",
                 "BACKEND_S1":"running"},
    }


def rows():
    return [sample("normal",i) for i in range(3)]+[
        sample("fault",i) for i in range(3,7)
    ]+[sample("recovery",i) for i in range(7,10)]


class FaultHttpReadOnlyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source_dir=self.root/"s05/evidencias/ha-noc"
        self.source_dir.mkdir(parents=True)
        self.source=self.source_dir/"S05_HA_NOC_CICLO_20261123T170000Z.jsonl"
        self.source.write_text("\n".join(json.dumps(x) for x in rows())+"\n")
        self.log=self.root/"S06_FAULT_HTTP_Ejecucion.txt"
        timer="netlab360-s05-ha-hq-rescue-20261123T170000Z-123.timer"
        self.log.write_text("\n".join([
            "S05_HA_RESCATE_TIMER_ARMADO="+timer,
            "S05_HA_RESCATE_PLAZO=120s",
            "S05_HA_NOC_JSONL="+str(self.source),
            "S05_HA_NOC_BACKEND_HQ=DETENIDO_CONTROLADO",
            "S05_HA_NOC_CICLO=HQ_S1_HQ_OK",
            "S05_HA_NOC_SERVICIOS_RESTAURADOS=OK",
            "S05_HA_RESCATE_TIMER_CANCELADO="+timer,
            "S05_HA_CICLO_INSTANCIA=HQ_S1_HQ_OK",
            "S05_HA_GESTION=INTACTA",
            "S05_LOTE_HA_INSTANCIA=OK",
        ])+"\n")
        self.study=self.root/"s06/estudio-uniforme-v2"
        self.study.mkdir(parents=True)
        (self.study/"TEST_Manifest.json").write_text(json.dumps({
            "normal_session":"S06_WINDOW_NORMAL_20261123T153501Z_abcdef",
            "degraded_sessions":[
                "S06_WINDOW_DEGRADED_20261123T153600Z_abcdef",
                "S06_WINDOW_DEGRADED_20261123T153800Z_abcdef"
            ],
            "recovery_sessions":[
                "S06_WINDOW_RECOVERY_20261123T153700Z_abcdef",
                "S06_WINDOW_RECOVERY_20261123T153900Z_abcdef"
            ],
        }))
        for k,v in (("SOURCES",self.source_dir),("STUDY",self.study)):
            patch=mock.patch.object(m,k,v)
            patch.start()
            self.addCleanup(patch.stop)

    def test_three_phases_valid(self):
        steps,data=m.phases(rows())
        self.assertEqual(steps,["BACKEND_HQ","BACKEND_S1","BACKEND_HQ"])
        self.assertEqual(data["counts"],{
            "NORMAL_HTTP_HQ":3,"FAULT_HTTP_BACKEND_HQ":4,
            "RECOVERY_HTTP_HQ":3})

    def test_reject_no_fault(self):
        with self.assertRaisesRegex(ValueError,"sequence"):
            m.phases([sample("normal",i) for i in range(10)])

    def test_reject_no_recovery(self):
        with self.assertRaisesRegex(ValueError,"sequence"):
            m.phases([sample("normal",i) for i in range(3)]+
                     [sample("fault",i) for i in range(3,10)])

    def test_reject_fib_changed(self):
        data=rows()
        data[5]["fib_s1"]="another"
        with self.assertRaisesRegex(ValueError,"ha_or_wan"):
            m.phases(data)

    def test_reject_frontend_down(self):
        data=rows()
        data[5]["nodes"]["FRONTAL_HQ"]="down"
        with self.assertRaisesRegex(ValueError,"service_provenance"):
            m.phases(data)

    def test_reject_hq_backend_not_stopped(self):
        data=rows()
        data[5]["nodes"]["BACKEND_HQ"]="running"
        with self.assertRaisesRegex(ValueError,"not_proven_down"):
            m.phases(data)

    def test_reject_unverified_clock(self):
        data=rows()
        data[5]["observed_utc"]="2026-11-23T17:00:01+00:00"
        with self.assertRaisesRegex(ValueError,"not_monotonic"):
            m.phases(data)

    def test_log_proves_authorized_operation(self):
        source,timer,raw=m.log_file(self.log)
        self.assertEqual(source,self.source)
        self.assertIn(".timer",timer)
        self.assertGreater(len(raw),100)

    def test_log_rejects_missing_rescue_cancellation(self):
        self.log.write_text(self.log.read_text().replace(
            "S05_HA_RESCATE_TIMER_CANCELADO=","S05_HA_TIMER_MISSING="))
        with self.assertRaisesRegex(ValueError,"rescue_timer"):
            m.log_file(self.log)

    def test_log_rejects_missing_stop(self):
        self.log.write_text(self.log.read_text().replace(
            "S05_HA_NOC_BACKEND_HQ=DETENIDO_CONTROLADO","NO_STOP"))
        with self.assertRaisesRegex(ValueError,"missing_approved"):
            m.log_file(self.log)

    def test_session_parser_no_external_import_context(self):
        valid="S06_WINDOW_NORMAL_20261123T153501Z_4d1e6c"
        self.assertEqual(m.session_time(valid).year, 2026)
        self.assertEqual(m.session_time(valid).minute, 35)

    def test_session_parser_rejects_bad_identifier(self):
        with self.assertRaisesRegex(ValueError,"invalid_session_timestamp"):
            m.session_time("S06_WINDOW_NORMAL_invalido_abcdef")

    def test_session_parser_rejects_invalid_clock(self):
        with self.assertRaisesRegex(ValueError,"invalid_session_timestamp"):
            m.session_time("S06_WINDOW_NORMAL_20261399T259999Z_abcdef")

    def test_new_fault_evidence_not_training_data(self):
        obj=m.evaluate(self.log)
        self.assertEqual(obj["sample_counts"]["FAULT_HTTP_BACKEND_HQ"],4)
        self.assertFalse(obj["v2_models_retrained"])
        self.assertFalse(obj["new_machine_learning_test"])
        self.assertEqual(obj["forecast_horizon_validated"],False)

    def test_reject_old_s05_evidence_before_test(self):
        d=rows()
        for i,row in enumerate(d):
            row["observed_utc"]=f"2026-11-12T17:00:{i:02d}+00:00"
        self.source.write_text("\n".join(json.dumps(x) for x in d))
        with self.assertRaisesRegex(ValueError,"not_newer_than_test"):
            m.evaluate(self.log)

    def test_reader_has_no_network_mutators(self):
        source=SOURCE.read_text()
        for forbidden in ("subprocess.", "systemctl stop", "tc qdisc",
                          ".fit(", "sudo ", "docker run", "ip netns add"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden,source)


if __name__=="__main__":
    unittest.main()
