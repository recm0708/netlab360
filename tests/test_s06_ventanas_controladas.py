"""S06-042 pruebas del ground truth independiente de RTT en red HQ."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest import mock

FILE=Path(__file__).resolve().parents[1]/"scripts/s06/capturar_ventanas_controladas.py"
SPEC=importlib.util.spec_from_file_location("s06_controlled_windows",FILE)
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def evidence(state="APPLIED", qdisc="OWN_NETEM", token="abcd",
             valid=True, timestamps=True):
    guard={"schema":"NETLAB360_S06_HQ_EXPERIMENT_GUARD_V1",
           "state":state,"qdisc":qdisc,"token":token,
           "target":f"{m.NS}/{m.DEVICE}",
           "human_approval":True,
           "ground_truth_degraded_verified":True}
    if timestamps:
        guard["applied_at_utc"]="2026-11-23T08:00:00+00:00"
        guard["expired_at_utc"]="2026-11-23T08:00:35+00:00"
    return {"guard":guard,"routes_verified":valid}


def measure(rtt=0.2, valid=True):
    return [{"probe_id":p[0],"result":{
        "measurement_valid":valid,"rtt_avg_ms":rtt,
        "loss_pct":0.0}} for p in m.PROBES]


class ControlledWindowTests(unittest.TestCase):
    def test_catalogo_ninguna_interfaz_temporal(self):
        self.assertEqual(m.NS,"nl360-s02-h-hq-120")
        self.assertEqual(m.DEVICE,"eth0")
        self.assertEqual(len(m.PROBES),2)
        self.assertNotIn("dummy0",FILE.read_text())

    def test_degraded_con_estado_real_verificado(self):
        z=m.classify("DEGRADED",evidence(),evidence(),measure(rtt=40))
        self.assertEqual(z["ground_truth_label"],"DEGRADED")
        self.assertTrue(z["ground_truth_verified"])

    def test_degraded_no_etiqueta_por_rtt_alto(self):
        a=m.classify("DEGRADED",evidence(),evidence(),measure(rtt=0.01))
        b=m.classify("DEGRADED",evidence(),evidence(),measure(rtt=400))
        self.assertEqual(a,b)

    def test_recovery_con_estado_restored(self):
        b=evidence(state="RESTORED",qdisc="BASELINE")
        a=evidence(state="RESTORED",qdisc="BASELINE")
        z=m.classify("RECOVERY",b,a,measure())
        self.assertEqual(z["ground_truth_label"],"RECOVERY")

    def test_no_recovery_sin_estado_restored(self):
        z=m.classify("RECOVERY",evidence(),evidence(),measure())
        self.assertEqual(z["ground_truth_label"],"UNKNOWN")

    def test_ambiguo_si_watchdog_expira_mitad_ventana(self):
        b=evidence()
        a=evidence(state="RESTORED",qdisc="BASELINE")
        z=m.classify("DEGRADED",b,a,measure())
        self.assertFalse(z["ground_truth_verified"])

    def test_qdisc_ajena_no_es_degraded(self):
        z=m.classify("DEGRADED",evidence(qdisc="FOREIGN"),
                     evidence(),measure())
        self.assertFalse(z["ground_truth_verified"])

    def test_token_cambia_bloquea(self):
        z=m.classify("DEGRADED",evidence(token="abc"),
                     evidence(token="def"),measure())
        self.assertFalse(z["ground_truth_verified"])

    def test_rutas_invalidas_bloquean(self):
        z=m.classify("DEGRADED",evidence(valid=False),
                     evidence(),measure())
        self.assertFalse(z["ground_truth_verified"])

    def test_measure_invalido_bloquea(self):
        z=m.classify("DEGRADED",evidence(),evidence(),measure(valid=False))
        self.assertEqual(z["ground_truth_label"],"UNKNOWN")

    def test_missing_time_event_bloquea(self):
        z=m.classify("DEGRADED",evidence(timestamps=False),
                     evidence(),measure())
        self.assertFalse(z["ground_truth_verified"])

    def test_label_ilegal_rechazado(self):
        with self.assertRaises(ValueError):
            m.classify("FAULT",evidence(),evidence(),measure())

    def test_rango_de_paquetes_y_rondas(self):
        for a,b,c in (("DEGRADED",1,2),("RECOVERY",16,2),
                      ("DEGRADED",2,1),("RECOVERY",2,4)):
            with self.subTest(a=a,b=b,c=c),self.assertRaises(ValueError):
                m.capture(a,b,c)

    def test_no_ejecucion_global_root(self):
        with mock.patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaises(RuntimeError):
                m.capture("DEGRADED",2,2)

    def test_guard_parsing(self):
        payload='S06_042_STATE=APPLIED\nS06_042_STATE_JSON={"schema":"NETLAB360_S06_HQ_EXPERIMENT_GUARD_V1","state":"APPLIED","target":"nl360-s02-h-hq-120/eth0"}\n'
        with mock.patch.object(m,"command",return_value=payload):
            z=m.read_guard()
        self.assertEqual(z["state"],"APPLIED")

    def test_no_contiene_acciones_mutantes(self):
        src=FILE.read_text()
        for text in ("qdisc add","qdisc del","qdisc replace",
                     "netns add","netns del","shell=True"):
            self.assertNotIn(text,src)


if __name__=="__main__":
    unittest.main()
