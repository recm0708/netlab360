"""S07-001B: adaptadores probados con fixtures explícitamente sintéticos."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/s07"))
import adaptadores_noc as m

NOW = "2026-11-24T03:00:00Z"
STAMP = "2026-11-24T02:59:55Z"


def graph():
    return {
        "project": "NETLAB360", "phase": "S05", "schema_version": 1,
        "observed_at_utc": NOW,
        "telemetry": {"available": True, "topology": "active", "last_sample_utc": STAMP},
        "links": [{"id": k, "type": "wan", "from": "R-HQ",
                   "to": "R-"+v, "status": "admin-up"} for k, v in m.WAN.items()],
        "nodes": [{"id": k, "site": s, "vlan": v, "type": "host",
                   "vlan_admin": "admin-up"} for k, (s, v) in m.VLANS.items()],
        "lacp": {"available": True, "status": "observed", "observed_at_utc": STAMP,
                 "sites": {s: {"status": "up", "switch_members": 2, "client_members": 2}
                           for s in m.SITES}},
        "sdn": {"available": True, "status": "connected", "connected": True,
                "flow_count": 25, "observed_at_utc": STAMP},
        "ha_service": {"available": True, "status": "running", "active_backend": "BACKEND_HQ",
                       "selected_path": "PRINCIPAL", "observed_at_utc": STAMP},
    }


def ia():
    return {"schema": "NETLAB360_S06_047_NOC_AI_ADAPTER_V1",
            "mode": "READ_ONLY_EXPLORATORY", "graph_s05_independent": True,
            "production_deployment_authorized": False, "network_mutations_authorized": False,
            "routes": {r: {"route": r, "available": True, "state": "NORMAL",
                           "consensus": "NORMAL", "ground_truth": "UNKNOWN",
                           "reason": "BASELINE_AND_UNANIMOUS_NORMAL_SCOPED",
                           "production_deployment_authorized": False,
                           "network_mutations_authorized": False,
                           "observed_at_utc": STAMP, "rtt_avg_ms": .1, "loss_pct": 0,
                           "methods": {k: "NORMAL" for k in m.METHODS}}
                       for r in ("HQ_A_S1", "HQ_A_S2")}}


def lookup(g, resource):
    return next(e for e in m.graph_events(g, NOW) if e["resource_id"] == resource)


class AdapterTests(unittest.TestCase):
    def test_inventory(self):
        events = m.graph_events(graph(), NOW)
        self.assertEqual(len(events), 19)
        self.assertTrue(all(e["quality"] == "VALID" for e in events))
        self.assertEqual(len({e["resource_id"] for e in events}), 19)

    def test_no_invented_wan_or_vlan_operational_state(self):
        for e in m.graph_events(graph(), NOW):
            if e["subject"] in ("WAN", "VLAN"):
                self.assertEqual(e["state"], "UNKNOWN")
                self.assertEqual(e["details"]["admin_state"], "admin-up")
                self.assertEqual(e["details"]["scope"], "ADMIN_STATE_ONLY")

    def test_timestamp_from_actual_signal(self):
        e = lookup(graph(), "LACP-HQ")
        self.assertEqual(e["observed_at_utc"], "2026-11-24T02:59:55+00:00")

    def test_graph_missing_timestamp_not_replaced(self):
        g = graph()
        del g["lacp"]["observed_at_utc"]
        self.assertEqual(lookup(g, "LACP-HQ")["quality"], "MISSING")

    def test_stale_signal(self):
        g = graph()
        g["telemetry"]["last_sample_utc"] = "2026-11-24T02:50:00Z"
        self.assertEqual(lookup(g, "MULTISEDE")["quality"], "STALE")

    def test_bad_graph_envelope(self):
        for g in (None, [], {"project": "other"}, dict(graph(), schema_version=True)):
            self.assertTrue(all(e["quality"] == "MISSING" for e in m.graph_events(g, NOW)))

    def test_duplicate_resource_not_selected(self):
        g = graph()
        g["links"].append(g["links"][0])
        self.assertEqual(lookup(g, g["links"][0]["id"])["quality"], "MISSING")

    def test_incorrect_identity(self):
        g = graph()
        g["nodes"][0]["site"] = "S2"
        self.assertEqual(lookup(g, "VLAN-110")["quality"], "MISSING")

    def test_lacp_degraded(self):
        g = graph()
        g["lacp"]["sites"]["HQ"].update(status="degraded", switch_members=1)
        self.assertEqual(lookup(g, "LACP-HQ")["state"], "DEGRADED")

    def test_lacp_bad_count(self):
        g = graph()
        g["lacp"]["sites"]["HQ"]["client_members"] = True
        self.assertEqual(lookup(g, "LACP-HQ")["quality"], "MISSING")

    def test_lacp_partial_preserves_good_site(self):
        g = graph()
        g["lacp"].update(available=False, status="partial")
        g["lacp"]["sites"]["S1"] = {"status": "unknown"}
        self.assertEqual(lookup(g, "LACP-S1")["quality"], "MISSING")
        self.assertEqual(lookup(g, "LACP-HQ")["state"], "NORMAL")

    def test_sdn_disconnected(self):
        g = graph()
        g["sdn"].update(status="disconnected", connected=False, flow_count=None)
        self.assertEqual(lookup(g, "FAUCET")["state"], "FAULT")

    def test_sdn_inconsistent(self):
        g = graph()
        g["sdn"]["flow_count"] = 0
        self.assertEqual(lookup(g, "FAUCET")["quality"], "MISSING")

    def test_ha_backup_not_global_fault(self):
        g = graph()
        g["ha_service"].update(active_backend="BACKEND_S1", selected_path="RESPALDO")
        self.assertEqual(lookup(g, "FRONTAL_HQ")["state"], "DEGRADED")

    def test_ha_offline(self):
        g = graph()
        g["ha_service"].update(status="offline", active_backend=None, selected_path=None)
        self.assertEqual(lookup(g, "FRONTAL_HQ")["state"], "FAULT")

    def test_ha_inconsistent(self):
        g = graph()
        g["ha_service"]["selected_path"] = "RESPALDO"
        self.assertEqual(lookup(g, "FRONTAL_HQ")["quality"], "MISSING")

    def test_ia_normal(self):
        events = m.ia_events(ia(), NOW)
        self.assertEqual(len(events), 2)
        self.assertTrue(all(e["state"] == "NORMAL" and e["ground_truth"] == "UNKNOWN"
                            for e in events))

    def test_ia_unconfirmed_degradation(self):
        d = ia()
        d["routes"]["HQ_A_S1"].update(state="UNKNOWN", consensus="DEGRADED",
            reason="DEGRADATION_INDICATION_UNCONFIRMED", methods={k:"DEGRADED" for k in m.METHODS})
        e = m.ia_events(d, NOW)[0]
        self.assertEqual((e["state"], e["quality"]), ("UNKNOWN", "VALID"))
        self.assertEqual(e["details"]["consensus"], "DEGRADED")

    def test_ia_invalid_label(self):
        d = ia()
        d["routes"]["HQ_A_S1"]["ground_truth"] = "NORMAL"
        self.assertEqual(m.ia_events(d, NOW)[0]["quality"], "MISSING")

    def test_ia_disagreement_cannot_claim_normal(self):
        d = ia()
        d["routes"]["HQ_A_S1"]["methods"]["P95_RTT"] = "DEGRADED"
        self.assertEqual(m.ia_events(d, NOW)[0]["quality"], "MISSING")

    def test_ia_offline(self):
        self.assertTrue(all(e["state"] == "UNKNOWN" and e["quality"] == "MISSING"
                            for e in m.ia_events(None, NOW)))

    def test_ia_nonfinite(self):
        d = ia()
        d["routes"]["HQ_A_S1"]["rtt_avg_ms"] = float("nan")
        self.assertEqual(m.ia_events(d, NOW)[0]["quality"], "MISSING")

    def test_ia_authorization_rejected(self):
        d = ia()
        d["network_mutations_authorized"] = True
        self.assertTrue(all(e["quality"] == "MISSING" for e in m.ia_events(d, NOW)))

    def test_batch_independent_sources(self):
        with patch.object(m, "read_source", side_effect=[(graph(), NOW, "HTTP_OK"),
                                                        (None, NOW, "UNAVAILABLE_OR_INVALID")]):
            batch = m.collect()
        self.assertEqual(len(batch["events"]), 21)
        self.assertFalse(batch["network_mutations_authorized"])
        self.assertEqual(sum(e["quality"] == "VALID" for e in batch["events"]), 19)

    def test_source_allowlist(self):
        with self.assertRaises(ValueError):
            m.read_source("http://other")

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            m.unique_pairs([("key", 1), ("key", 2)])

    def test_redirects_rejected(self):
        self.assertIsNone(m.NoRedirect().redirect_request(None, None, 302, "", {}, "http://other"))


if __name__ == "__main__":
    unittest.main()
