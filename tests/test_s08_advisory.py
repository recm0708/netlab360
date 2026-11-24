"""Pruebas de lectura asesora S08, sin iniciar el broker protegido."""
import importlib.util
from pathlib import Path
import os
import socket
import stat
import struct
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
package = ROOT / "servicios/consola-s08/api"
spec = importlib.util.spec_from_file_location(
    "netlab360_s08_advisory", package / "__init__.py", submodule_search_locations=[str(package)])
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_advisory import advisory_reader as m

NOW = "2026-01-01T00:00:10+00:00"
STAMP = "2026-01-01T00:00:05+00:00"


def fixture(section):
    candidate = {"schema":"NETLAB360_S07_INCIDENT_V1","status":"CANDIDATE",
                 "confirmed":False,"root_cause":None,"ground_truth":"UNKNOWN",
                 "network_mutations_authorized":False}
    diagnosis = {"schema":"NETLAB360_S07_RCA_V1","root_cause":None,
                 "confirmed_incidents":0,"network_mutations_authorized":False,
                 "hypotheses":[{"status":"HYPOTHESIS","confirmed":False,
                                "root_cause":None,"network_mutations_authorized":False}],
                 "coverage_gaps":[{"context_id":"HQ"}]}
    recommendations = {"schema":"NETLAB360_S07_RECOMMENDATION_V1",
                       "approval_granted":False,"requires_fresh_evidence":True,
                       "network_mutations_authorized":False,
                       "recommendations":[{"requires_fresh_evidence":True,
                                           "network_mutations_authorized":False}]}
    catalog = {"schema":"NETLAB360_S07_RUNBOOK_CATALOG_V1","version":1,
               "network_mutations_authorized":False,"actions":{
                   "read":{"execution_authorized":False,"mutation":False,"approval_required":False},
                   "change":{"execution_authorized":False,"mutation":True,"approval_required":True}}}
    data = {"incidents":[candidate],"hypotheses":{"diagnosis":diagnosis,
            "recommendations":recommendations},"runbooks":catalog}[section]
    return {"schema":"NETLAB360_S07_API_V1","ok":True,"result":{
        "source":"OPERATOR_ADVISORY_SNAPSHOT","observed_at_utc":STAMP,
        "historical":True,"authorization_evidence":False,"data":data}}


class AdvisoryTests(unittest.TestCase):
    def test_fresh_summary(self):
        rows = [m.project(s,fixture(s),NOW,"OK") for s in m.SECTIONS]
        self.assertTrue(all(r["quality"]=="VALID" and r["state"]=="UNKNOWN"
                            and r["kind"]=="ADVISORY_SNAPSHOT" for r in rows))
        self.assertEqual(rows[0]["details"]["candidates"],1)
        self.assertEqual(rows[1]["details"]["hypotheses"],1)
        self.assertEqual(rows[1]["details"]["recommendations"],1)
        self.assertEqual(rows[2]["details"]["controlled_change_runbooks"],1)
        self.assertTrue(all(r["network_mutations_authorized"] is False for r in rows))

    def test_stale_and_future(self):
        for stamp,quality in (("2025-12-31T23:58:00+00:00","STALE"),
                              ("2026-01-01T00:00:11+00:00","FUTURE")):
            p=fixture("incidents")
            p["result"]["observed_at_utc"]=stamp
            row=m.project("incidents",p,NOW,"OK")
            self.assertEqual((row["quality"],row["state"],row["details"]),(quality,"UNKNOWN",{}))
            self.assertIsNotNone(row["observed_at_utc"])

    def test_empty_not_missing(self):
        p=fixture("incidents")
        p["result"]["data"]=[]
        self.assertEqual(m.project("incidents",p,NOW,"OK")["details"]["candidates"],0)

    def test_authority_rejected(self):
        p=fixture("hypotheses")
        p["result"]["authorization_evidence"]=True
        self.assertEqual(m.project("hypotheses",p,NOW,"OK")["quality"],"INVALID")

    def test_confirmed_incident_rejected(self):
        p=fixture("incidents")
        p["result"]["data"][0]["confirmed"]=True
        self.assertEqual(m.project("incidents",p,NOW,"OK")["quality"],"INVALID")

    def test_runbook_execution_rejected(self):
        p=fixture("runbooks")
        p["result"]["data"]["actions"]["change"]["execution_authorized"]=True
        self.assertEqual(m.project("runbooks",p,NOW,"OK")["quality"],"INVALID")

    def test_missing_independent(self):
        with patch.object(m,"fetch",side_effect=[(None,NOW,"NOT_STARTED"),
                     (fixture("hypotheses"),NOW,"OK"),(None,NOW,"UNAVAILABLE")]):
            rows=m.collect()
        self.assertEqual([r["quality"] for r in rows],["MISSING","VALID","MISSING"])
        self.assertEqual(rows[0]["transport"],"NOT_STARTED")

    def test_arbitrary_route_rejected(self):
        with patch.object(m,"UnixHTTP") as factory:
            with self.assertRaises(ValueError):
                m.fetch("rfcs")
            factory.assert_not_called()

    def test_fixed_get(self):
        with patch.object(m,"UnixHTTP") as factory:
            response=MagicMock(status=200)
            response.getheader.side_effect=lambda key,default="": (
                "application/json" if key=="Content-Type" else default)
            import json
            response.read.return_value=json.dumps(fixture("incidents")).encode()
            conn=factory.return_value
            conn.getresponse.return_value.__enter__.return_value=response
            self.assertEqual(m.fetch("incidents")[2],"OK")
            conn.request.assert_called_once()
            self.assertEqual(conn.request.call_args.args[:2],("GET","/api/v1/incidents"))
            response.read.assert_called_once_with(m.MAX_BYTES+1)

    def test_peer_uid_rejected(self):
        with patch.object(Path,"lstat",side_effect=[
                MagicMock(st_mode=stat.S_IFSOCK|0o660,st_uid=0),
                MagicMock(st_mode=stat.S_IFDIR|0o755,st_uid=0)]),                 patch.object(m.socket,"socket") as factory:
            sock=factory.return_value
            sock.getsockopt.return_value=struct.pack("3i",123,1000,1000)
            with self.assertRaisesRegex(ValueError,"UNTRUSTED_UNIX_PEER"):
                m.UnixHTTP("localhost",timeout=3).connect()
            sock.close.assert_called_once()

    def test_socket_symlink_rejected(self):
        with patch.object(Path,"lstat",side_effect=[
                MagicMock(st_mode=stat.S_IFLNK|0o777,st_uid=0),
                MagicMock(st_mode=stat.S_IFDIR|0o755,st_uid=0)]),                 patch.object(m.socket,"socket") as factory:
            with self.assertRaisesRegex(ValueError,"UNTRUSTED_UNIX_SOCKET"):
                m.UnixHTTP("localhost",timeout=3).connect()
            factory.assert_not_called()


AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("fastapi","httpx","pydantic"))
if AVAILABLE:
    from fastapi.testclient import TestClient
    from netlab360_s08_advisory import storage, security, sessions
    from netlab360_s08_advisory.main import create_app


@unittest.skipUnless(AVAILABLE and os.geteuid()!=0,"API S08 con dependencias y sin root")
class AdvisoryHttpTests(unittest.TestCase):
    def test_protected_advisory(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)/"estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory,"viewer","synthetic test phrase only","VIEWER")
            token=sessions.issue(directory,"viewer")["token"]
            with TestClient(create_app(directory),base_url="http://127.0.0.1:9140") as client:
                rows=[m.project(s,fixture(s),NOW,"OK") for s in m.SECTIONS]
                with patch.object(m,"collect",return_value=rows) as collect:
                    self.assertEqual(client.get("/api/v1/advisory").status_code,401)
                    collect.assert_not_called()
                    client.cookies.set("netlab360_session",token)
                    self.assertEqual(client.get("/api/v1/advisory?path=rfcs").status_code,400)
                    collect.assert_not_called()
                    response=client.get("/api/v1/advisory")
                    self.assertEqual(response.status_code,200)
                    self.assertEqual(len(response.json()["observations"]),3)
                    self.assertEqual(response.json()["infrastructure_state"],"UNKNOWN")
                    self.assertEqual(client.post("/api/v1/advisory").status_code,405)
                    collect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
