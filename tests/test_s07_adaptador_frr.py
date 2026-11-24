"""Fixtures de tablas FRR y FIB, sin ejecutar comandos en CI."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
import adaptador_frr as m

NOW="2026-11-24T03:00:00Z"
STAMP="2026-11-24T02:59:59Z"
HEADER="Neighbor ID Pri State Up Time Dead Time Address Interface RXmtL RqstL DBsmL"


def table(site,state="Full"):
    return HEADER+"\n"+"\n".join(
        f"{m.LOOPS[peer]} 1 {state}/- 00:10:00 00:00:39 {remote} {iface}:{local} 0 0 0"
        for iface,(peer,local,remote) in m.LINKS[site].items())


def route(site,peer,backup=False):
    next_peer=peer if site=="HQ" else "HQ"
    iface=next(i for i,(p,_,_) in m.LINKS[site].items()
               if p==next_peer and i.endswith("b" if backup else "p"))
    return json.dumps([{"dst":m.LOOPS[peer],"dev":iface,"gateway":m.LINKS[site][iface][2]}])


def record(site):
    return {"received_at_utc":NOW,"neighbors":{"raw":table(site),"observed_at_utc":STAMP},
            "routes":{p:{"raw":route(site,p),"observed_at_utc":STAMP}
                      for p in m.SITES if p!=site}}


class FrrAdapterTests(unittest.TestCase):
    def test_full_inventory(self):
        events=[e for s in m.SITES for e in m.project_site(s,record(s))]
        self.assertEqual(len(events),14)
        self.assertEqual(sum(e["subject"]=="OSPF" for e in events),8)
        self.assertTrue(all(e["state"]=="NORMAL" and e["quality"]=="VALID" for e in events))
        self.assertTrue(all(e["network_mutations_authorized"] is False for e in events))

    def test_neighbor_id_wrong(self):
        self.assertIsNone(m.parse_neighbors("HQ",table("HQ").replace("10.79.0.2","10.79.9.9")))

    def test_neighbor_address_wrong(self):
        self.assertIsNone(m.parse_neighbors("HQ",table("HQ").replace("10.78.0.2","10.78.0.99")))

    def test_duplicate_neighbor(self):
        t=table("HQ")
        self.assertIsNone(m.parse_neighbors("HQ",t+"\n"+t.splitlines()[1]))

    def test_missing_neighbor_not_fault(self):
        r=record("HQ")
        r["neighbors"]["raw"]="\n".join(table("HQ").splitlines()[:-1])
        events=m.project_site("HQ",r)
        self.assertEqual(next(e for e in events if e["resource_id"]=="OSPF-HQ-s2b")["quality"],"MISSING")

    def test_nonfull(self):
        r=record("S1")
        r["neighbors"]["raw"]=table("S1","Init")
        self.assertEqual(m.project_site("S1",r)[0]["state"],"DEGRADED")

    def test_unrecognized_output(self):
        self.assertIsNone(m.parse_neighbors("HQ","error"))

    def test_backup(self):
        r=record("HQ")
        r["routes"]["S1"]["raw"]=route("HQ","S1",True)
        e=next(e for e in m.project_site("HQ",r) if e["resource_id"]=="FIB-HQ-S1")
        self.assertEqual(e["state"],"DEGRADED")
        self.assertEqual(e["details"]["selection"],"BACKUP")

    def test_wrong_gateway(self):
        self.assertIsNone(m.parse_route("HQ","S1",route("HQ","S1").replace("10.78.0.2","10.78.0.99")))

    def test_wrong_destination(self):
        self.assertIsNone(m.parse_route("HQ","S1",route("HQ","S1").replace("10.79.0.2","10.79.0.3")))

    def test_missing_router(self):
        r={"received_at_utc":NOW}
        self.assertTrue(all(e["quality"]=="MISSING" for e in m.project_site("HQ",r)))

    def test_timestamp_preserved(self):
        self.assertEqual(m.project_site("HQ",record("HQ"))[0]["age_seconds"],1)

    def test_identity_mismatch(self):
        row={"Id":"wrong","Name":"/"+m.NAMES["HQ"],"State":{"Running":True,"Pid":100},
             "HostConfig":{"NetworkMode":"none"},"Config":{"Labels":{"com.docker.compose.project":"netlab360-s02-wan"}}}
        with patch.object(m,"run",return_value=json.dumps([row])):
            with self.assertRaisesRegex(RuntimeError,"ROUTER_IDENTITY"):
                m.inspect("HQ","expected")

    def test_no_observation_on_pid_change(self):
        with patch.object(m,"management"), patch.object(m,"ownership",return_value={"R-"+s:"id" for s in m.SITES}), \
             patch.object(m,"inspect",side_effect=[101,102,201,202,301,302]), \
             patch.object(m,"capture",return_value={"raw":"unused","observed_at_utc":STAMP}):
            _,batch=m.collect()
        self.assertTrue(all(e["quality"]=="MISSING" for e in batch["events"]))


if __name__=="__main__":
    unittest.main()
