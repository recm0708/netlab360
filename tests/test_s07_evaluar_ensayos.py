"""Evaluación de recomendaciones con fixtures aislados."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from evaluar_ensayos_s07 import assess,TARGETS,show
from io import StringIO
from contextlib import redirect_stdout
from test_s07_contexto_rca import acquisition
from test_s07_adquisicion_integrada import baseline
from test_s07_diagnostico_rca import change
from diagnostico_rca import diagnose
from recomendaciones_rca import recommend

class EvaluationTests(unittest.TestCase):
    def test_baseline(self):
        a=acquisition()
        x=assess("HTTP","BASELINE",diagnose(a),recommend(a))
        self.assertEqual(x["observed"],0)
    def test_http_correct(self):
        b=change(baseline(),"NOC_S05","FRONTAL_HQ",state="DEGRADED",details={"scope":"HTTP_FROM_S2","status":"running","active_backend":"BACKEND_S1","selected_path":"RESPALDO"})
        a=acquisition(b)
        x=assess("HTTP","FAULT",diagnose(a),recommend(a))
        self.assertEqual(x["correct_recommendations"],1)
        self.assertEqual(x["missing"],[])
    def test_missing_hypothesis_count(self):
        a=acquisition()
        self.assertEqual(len(assess("HTTP","FAULT",diagnose(a),recommend(a))["missing"]),1)
    def test_unexpected_hypothesis_count(self):
        b=change(baseline(),"NOC_S05","FRONTAL_HQ",state="DEGRADED",details={"scope":"HTTP_FROM_S2","status":"running","active_backend":"BACKEND_S1","selected_path":"RESPALDO"})
        a=acquisition(b)
        self.assertEqual(len(assess("SDN","FAULT",diagnose(a),recommend(a))["unexpected"]),1)
    def test_no_approval(self):
        a=acquisition(); r=recommend(a);r["approval_granted"]=True
        with self.assertRaisesRegex(ValueError,"POLICY_OR_WINDOW"): assess("HTTP","BASELINE",diagnose(a),r)
    def test_expected_count(self):
        self.assertEqual(sum(map(len,TARGETS.values())),11)
    def test_presenter_only_formats_report(self):
        from copy import deepcopy
        a=acquisition()
        row=assess("HTTP","BASELINE",diagnose(a),recommend(a))
        row["window_seconds"]=0.5
        data={"rows":[row]}
        old=deepcopy(data)
        out=StringIO()
        with redirect_stdout(out):
            show(data,"HTTP")
        self.assertEqual(data,old)
        self.assertIn("\033[1;36m",out.getvalue())
        self.assertIn("PRESENTACION HISTORICA",out.getvalue())
        self.assertIn("SIN NUEVAS MUTACIONES",out.getvalue())
if __name__=="__main__": unittest.main()
