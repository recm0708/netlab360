"""Pruebas de inferencia exploratoria y abstención sin ejecutar modelos."""
from datetime import datetime, timedelta
import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
package = ROOT / "servicios/consola-s08/api"
spec = importlib.util.spec_from_file_location(
    "netlab360_s08_inference", package / "__init__.py", submodule_search_locations=[str(package)])
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_inference import inference_reader as m, contracts

NOW = "2026-01-01T00:00:10+00:00"
STAMP = "2026-01-01T00:00:05+00:00"


def fixture():
    return {"schema":"NETLAB360_S06_047_NOC_AI_ADAPTER_V1",
            "mode":"READ_ONLY_EXPLORATORY","network_mutations_authorized":False,
            "production_deployment_authorized":False,"graph_s05_independent":True,
            "routes":{route:{"route":route,"available":True,"ground_truth":"UNKNOWN",
                             "network_mutations_authorized":False,
                             "production_deployment_authorized":False,
                             "methods":{method:"NORMAL" for method in m.adapter.METHODS},
                             "consensus":"NORMAL","state":"NORMAL",
                             "reason":"BASELINE_AND_UNANIMOUS_NORMAL_SCOPED",
                             "rtt_avg_ms":1.25,"loss_pct":0,"observed_at_utc":STAMP}
                      for route in ("HQ_A_S1","HQ_A_S2")}}


class InferenceTests(unittest.TestCase):
    def test_scope(self):
        rows = m.project(fixture(),NOW,"OK")
        self.assertEqual(len(rows),2)
        self.assertTrue(all(r["kind"]=="INFERENCE" and r["quality"]=="VALID" for r in rows))
        self.assertTrue(all(r["details"]["ground_truth"]=="UNKNOWN" for r in rows))
        self.assertTrue(all(r["state"]=="NORMAL" and r["network_mutations_authorized"] is False for r in rows))

    def test_degradation_is_unconfirmed(self):
        p = fixture()
        for row in p["routes"].values():
            row.update(methods={method:"DEGRADED" for method in m.adapter.METHODS},
                       consensus="DEGRADED",state="UNKNOWN",reason="DEGRADATION_INDICATION_UNCONFIRMED")
        rows = m.project(p,NOW,"OK")
        self.assertTrue(all(r["state"]=="UNKNOWN" and r["details"]["consensus"]=="DEGRADED" for r in rows))

    def test_disagreement(self):
        p = fixture()
        row = p["routes"]["HQ_A_S1"]
        row["methods"]["P95_RTT"]="DEGRADED"
        row.update(consensus="UNKNOWN",state="UNKNOWN",reason="MODEL_DISAGREEMENT")
        rows = m.project(p,NOW,"OK")
        self.assertEqual((rows[0]["quality"],rows[0]["state"]),("VALID","UNKNOWN"))

    def test_absence(self):
        p = fixture()
        p["routes"]={}
        for payload, transport in ((p,"OK"),(None,"UNAVAILABLE")):
            rows = m.project(payload,NOW,transport)
            self.assertTrue(all(r["quality"]=="MISSING" and r["details"]=={} for r in rows))

    def test_authorization_rejected(self):
        p = fixture()
        p["network_mutations_authorized"]=True
        self.assertTrue(all(r["quality"]=="INVALID" for r in m.project(p,NOW,"OK")))

    def test_stale_future(self):
        p = fixture()
        p["routes"]["HQ_A_S1"]["observed_at_utc"]=(datetime.fromisoformat(NOW)-timedelta(seconds=31)).isoformat()
        p["routes"]["HQ_A_S2"]["observed_at_utc"]=(datetime.fromisoformat(NOW)+timedelta(seconds=1)).isoformat()
        rows = m.project(p,NOW,"OK")
        self.assertEqual([r["quality"] for r in rows],["STALE","FUTURE"])
        self.assertTrue(all(r["details"]=={} and r["state"]=="UNKNOWN" for r in rows))

    def test_contract_never_confirms_degradation(self):
        for state in ("DEGRADED","FAULT","RECOVERY"):
            row=contracts.source_metadata(source="IA_S06",transport="OK",
                observed_at_utc=STAMP,received_at_utc=NOW,state=state)
            self.assertEqual(row["state"],"UNKNOWN")

    def test_fixed_gateway(self):
        with patch.object(m.readers,"_fetch_fixed",return_value=(fixture(),NOW,"OK")) as fetch:
            self.assertEqual(len(m.collect()),2)
            fetch.assert_called_once_with(9130,m.PATH,m.readers.MAX_BYTES)


AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("fastapi","httpx","pydantic"))
if AVAILABLE:
    from fastapi.testclient import TestClient
    from netlab360_s08_inference import storage, security, sessions
    from netlab360_s08_inference.main import create_app


@unittest.skipUnless(AVAILABLE and os.geteuid()!=0,"API S08 con dependencias y sin root")
class InferenceHttpTests(unittest.TestCase):
    def test_protected_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)/"estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory,"viewer","synthetic test phrase only","VIEWER")
            token=sessions.issue(directory,"viewer")["token"]
            with TestClient(create_app(directory),base_url="http://127.0.0.1:9140") as client:
                with patch.object(m,"collect",return_value=m.project(fixture(),NOW,"OK")) as collect:
                    self.assertEqual(client.get("/api/v1/diagnostics").status_code,401)
                    collect.assert_not_called()
                    client.cookies.set("netlab360_session",token)
                    self.assertEqual(client.get("/api/v1/diagnostics?route=other").status_code,400)
                    collect.assert_not_called()
                    response=client.get("/api/v1/diagnostics")
                    self.assertEqual(response.status_code,200)
                    rows=response.json()["observations"]
                    self.assertEqual(len(rows),2)
                    self.assertEqual(rows[0]["details"]["rtt_avg_ms"],1.25)
                    self.assertEqual(rows[0]["details"]["ground_truth"],"UNKNOWN")
                    self.assertEqual(client.post("/api/v1/diagnostics").status_code,405)
                    collect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
