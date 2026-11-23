"""S06-041: criterios de etiquetas en ventanas y captura offline sin tráfico."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

FILE=Path(__file__).resolve().parents[1]/"scripts/s06/capturar_ventanas_normales.py"
SPEC=importlib.util.spec_from_file_location("s06_normal_windows",FILE)
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def evidence(*, valid=True, qdisc="CANDIDATE_NOQUEUE"):
    return {"snapshot_valid":valid,"qdisc_state":qdisc,
            "routes_ok":{"HQ_A_S1":True,"HQ_A_S2":True},
            "services":{x:"active" for x in m.SERVICES},
            "noc_healthy":True, "checked_at_utc":"2026-11-23T00:00:00+00:00"}


def measurements(*, valid=True, avg=0.2):
    return [
        {"kind":"icmp","probe_id":p[0],"result":{
             "measurement_valid":valid,"rtt_avg_ms":avg,"loss_pct":0.0
        }} for p in m.PROBES
    ]


class WindowNormalTests(unittest.TestCase):
    def test_probes_intersede_fijos(self):
        self.assertEqual(m.PROBES,(
            ("HQ_A_S1",m.NS,"10.71.20.20"),
            ("HQ_A_S2",m.NS,"10.72.20.20")
        ))
        self.assertEqual(m.DEVICE,"eth0")

    def test_label_scoped_solo_estado_egress(self):
        r=m.classify_window(evidence(),evidence(),measurements())
        self.assertEqual(r["ground_truth_label"],"NORMAL")
        self.assertTrue(r["ground_truth_verified"])
        self.assertEqual(r["label_scope"],"HQ_CLIENT_EGRESS_NETWORK_STATE")

    def test_no_usar_rtt_en_etiqueta(self):
        a=m.classify_window(evidence(),evidence(),measurements(avg=0.1))
        b=m.classify_window(evidence(),evidence(),measurements(avg=900.0))
        self.assertEqual(a["ground_truth_label"],b["ground_truth_label"])

    def test_evidencia_insuficiente_unknown(self):
        for left,right in ((evidence(valid=False),evidence()),
                           (evidence(),evidence(valid=False)),
                           (evidence(qdisc="BLOCKED_EXISTING_NETEM"),evidence()),
                           (evidence(),evidence(qdisc="BLOCKED_EXISTING_NETEM"))):
            with self.subTest(left=left,right=right):
                r=m.classify_window(left,right,measurements())
                self.assertEqual(r["ground_truth_label"],"UNKNOWN")
                self.assertFalse(r["ground_truth_verified"])

    def test_resultados_invalidos_no_verificados(self):
        r=m.classify_window(evidence(),evidence(),measurements(valid=False))
        self.assertEqual(r["ground_truth_label"],"UNKNOWN")

    def test_sonda_ausente_unknown(self):
        r=m.classify_window(evidence(),evidence(),measurements()[:1])
        self.assertFalse(r["ground_truth_verified"])

    def test_sonda_sustituida_unknown(self):
        values=measurements()
        values[1]["probe_id"]="EXTERNAL"
        r=m.classify_window(evidence(),evidence(),values)
        self.assertEqual(r["ground_truth_label"],"UNKNOWN")

    def test_catalogo_lectura_ruta_correcta(self):
        self.assertTrue(m.route_check([{
            "dst":"10.71.20.20","dev":"eth0",
            "prefsrc":"10.70.20.20","gateway":"10.70.20.1",
        }],"10.71.20.20"))

    def test_ruta_no_ipam_falla(self):
        for override in ({"dev":"ens33"},{"gateway":"10.70.20.3"},
                         {"prefsrc":"10.70.20.2"},{"dst":"10.72.20.20"}):
            q={"dst":"10.71.20.20","dev":"eth0",
               "prefsrc":"10.70.20.20","gateway":"10.70.20.1"}
            q.update(override)
            with self.subTest(override=override):
                self.assertFalse(m.route_check([q],"10.71.20.20"))

    def test_evidence_snapshot_ok(self):
        def cmd(args):
            if args==("sudo","-n","ip","netns","exec",m.NS,
                      "tc","-j","qdisc","show","dev",m.DEVICE):
                return '[{"kind":"noqueue","root":true,"handle":"0:"}]'
            if "route" in args:
                target=args[-1]
                return json.dumps([{
                    "dst":target,"dev":"eth0",
                    "prefsrc":"10.70.20.20","gateway":"10.70.20.1",
                }])
            if args[0]=="systemctl":
                return "active\n"
            raise AssertionError(args)
        with mock.patch.object(m,"command",side_effect=cmd), \
             mock.patch.object(m,"read_json") as read:
            read.side_effect=[
                {"routing":{"available":True},"ha_service":{
                    "status":"running","active_backend":"BACKEND_HQ"},
                 "lacp":{"available":True},"sdn":{"status":"connected"},
                 "source_warnings":[],"nodes":[0]*18,"links":[0]*21},
                {"healthy":True},
            ]
            snap=m.evidence_snapshot()
        self.assertTrue(snap["snapshot_valid"])
        self.assertEqual(snap["qdisc_state"],"CANDIDATE_NOQUEUE")

    def test_evidence_snapshot_si_hay_down_unknown(self):
        def cmd(args):
            if "qdisc" in args:
                return '[{"kind":"noqueue","root":true}]'
            if "route" in args:
                target=args[-1]
                return json.dumps([{"dst":target,"dev":"eth0",
                                    "prefsrc":"10.70.20.20",
                                    "gateway":"10.70.20.1"}])
            if args[0]=="systemctl":
                return "inactive" if args[-1]=="netlab360-s05-noc" else "active"
            raise AssertionError(args)
        with mock.patch.object(m,"command",side_effect=cmd), \
             mock.patch.object(m,"read_json",return_value={"healthy":True}):
            s=m.evidence_snapshot()
        self.assertFalse(s["snapshot_valid"])

    def test_validate_limits(self):
        for rounds,packets,pause in ((0,3,0),(81,3,0),(2,1,0),
                                      (2,7,0),(2,3,-1),(2,3,6)):
            with self.subTest(values=(rounds,packets,pause)):
                with self.assertRaises(ValueError):
                    m.capture(rounds,packets,pause)

    def test_rechaza_ejecucion_root(self):
        with mock.patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaises(RuntimeError):
                m.capture(2,3,0)

    def test_end_to_end_dos_ventanas_privadas(self):
        target={
            "qdisc":{"state":"CANDIDATE_NOQUEUE"},
            "target":{"namespace":m.NS,"interface":m.DEVICE,
                      "ipv4":f"{m.CLIENT_IP}/{m.CLIENT_PREFIX}",
                      "gateway":m.CLIENT_GW},
            "namespace_count":21,
        }
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(m,"ROOT",Path(tmp)), \
             mock.patch.object(m.os,"geteuid",return_value=1000), \
             mock.patch.object(m,"precheck",return_value=target), \
             mock.patch.object(m,"evidence_snapshot",return_value=evidence()), \
             mock.patch.object(m,"measure_ping",side_effect=lambda *_:measurements()[0]):
            # Para este test las dos sondas tienen IDs diferentes.
            def ping(p,packets):
                return {"kind":"icmp","probe_id":p[0],
                        "result":{"measurement_valid":True,"rtt_avg_ms":0.2}}
            with mock.patch.object(m,"measure_ping",side_effect=ping):
                report,rows=m.capture(2,2,0)
        self.assertEqual(len(rows),2)
        self.assertEqual(report["meta"]["verified"],2)
        self.assertEqual(report["meta"]["status"],"complete")
        self.assertTrue(all(r["ground_truth_verified"] for r in rows))

    def test_salud_de_ventanas(self):
        rows=[{"ground_truth_verified":True},{"ground_truth_verified":False}]
        self.assertEqual(m.health_failures(rows),["window_2_unverified"])

    def test_codigo_sin_mutaciones_qdisc_ni_shell(self):
        s=FILE.read_text()
        for phrase in ("qdisc add","qdisc del","qdisc replace",
                       "shell=True","os.system(","subprocess.Popen("):
            self.assertNotIn(phrase,s)

    def test_serie_no_reutiliza_ground_truth_observacional(self):
        s=FILE.read_text()
        self.assertIn("classify_window(before, after, measurements)",s)
        self.assertIn('"stimulus": "NONE"',s)
        self.assertIn('"training_ready": False',s)


if __name__=="__main__":
    unittest.main()
