"""Pruebas unitarias S07-001A con datos sintéticos, sin infraestructura."""
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "s07_contrato_eventos", ROOT / "scripts/s07/contrato_eventos.py")
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

NOW = "2026-11-24T03:00:00+00:00"


def event(**changes):
    values = dict(source="NOC_S05", subject="LACP", resource_id="LACP_HQ",
                  site="HQ", observed_at_utc="2026-11-24T02:59:50+00:00",
                  received_at_utc=NOW, state="NORMAL", available=True,
                  details={"switch_members": 2, "client_members": 2})
    values.update(changes)
    return m.make_event(**values)


class EventContractTests(unittest.TestCase):
    def test_baseline(self):
        e = event()
        self.assertEqual(e["schema"], m.SCHEMA)
        self.assertEqual((e["state"], e["quality"]), ("NORMAL", "VALID"))
        self.assertEqual(e["age_seconds"], 10)
        self.assertFalse(e["network_mutations_authorized"])
        self.assertEqual(e["ground_truth"], "UNKNOWN")
        self.assertEqual(e["evidence"]["endpoint"], "/api/v1/graph")

    def test_timezone_normalization(self):
        a = event(observed_at_utc="2026-11-23T21:59:50-05:00")
        self.assertEqual(a, event())

    def test_missing_source(self):
        e = event(available=False)
        self.assertEqual((e["state"], e["quality"]), ("UNKNOWN", "MISSING"))
        self.assertIsNone(e["observed_at_utc"])
        self.assertEqual(e["details"], {})

    def test_missing_timestamp(self):
        self.assertEqual(event(observed_at_utc=None)["quality"], "MISSING")

    def test_timestamp_no_zone(self):
        self.assertEqual(event(observed_at_utc="2026-11-24T02:59:50")["quality"], "INVALID")

    def test_invalid_timestamp(self):
        e = event(observed_at_utc="not-a-date")
        self.assertEqual((e["quality"], e["state"]), ("INVALID", "UNKNOWN"))

    def test_invalid_received_timestamp(self):
        with self.assertRaises(ValueError):
            event(received_at_utc="not-a-date")

    def test_future(self):
        e = event(observed_at_utc="2026-11-24T03:00:01Z")
        self.assertEqual((e["quality"], e["state"]), ("FUTURE", "UNKNOWN"))

    def test_stale(self):
        e = event(observed_at_utc="2026-11-24T02:58:59Z")
        self.assertEqual((e["quality"], e["state"]), ("STALE", "UNKNOWN"))

    def test_exact_age_boundary(self):
        self.assertEqual(event(observed_at_utc="2026-11-24T02:59:00Z")["quality"], "VALID")

    def test_unknown_valid_observation(self):
        e = event(state="UNKNOWN")
        self.assertEqual((e["state"], e["quality"]), ("UNKNOWN", "VALID"))

    def test_ia_unconfirmed_consensus(self):
        e = event(source="IA_S06", subject="ICMP_DIAGNOSIS",
                  resource_id="HQ_A_S1", peer_site="S1", state="UNKNOWN",
                  details={"consensus": "DEGRADED"})
        self.assertEqual(e["kind"], "INFERENCE")
        self.assertEqual(e["state"], "UNKNOWN")
        self.assertEqual(e["details"]["consensus"], "DEGRADED")
        self.assertEqual(e["ground_truth"], "UNKNOWN")

    def test_ia_rejects_claimed_fault_or_degradation(self):
        for state in ("FAULT", "DEGRADED", "RECOVERY"):
            with self.subTest(state=state), self.assertRaises(ValueError):
                event(source="IA_S06", subject="ICMP_DIAGNOSIS", state=state)

    def test_ia_freshness_limit(self):
        e = event(source="IA_S06", subject="ICMP_DIAGNOSIS",
                  observed_at_utc="2026-11-24T02:59:29Z")
        self.assertEqual((e["quality"], e["state"]), ("STALE", "UNKNOWN"))

    def test_invalid_source_subject(self):
        for params in ({"source": "OTHER"}, {"subject": "SHELL"},
                       {"source": "IA_S06"}):
            with self.subTest(params=params), self.assertRaises(ValueError):
                event(**params)

    def test_invalid_scope(self):
        for params in ({"site": "S9"}, {"peer_site": "HQ"},
                       {"site": None, "peer_site": "S1"},
                       {"resource_id": "HQ; comando"}):
            with self.subTest(params=params), self.assertRaises(ValueError):
                event(**params)

    def test_invalid_state_or_available(self):
        for params in ({"state": "up"}, {"available": 1}):
            with self.subTest(params=params), self.assertRaises(ValueError):
                event(**params)

    def test_invalid_details(self):
        for details in ({"x": float("nan")}, {"x": float("inf")},
                        {"x": []}, {"x": {}}, {"x": "a\nb"},
                        {"x": 10**19}, {"bad key": 1}):
            with self.subTest(details=details), self.assertRaises(ValueError):
                event(details=details)

    def test_id_stable_across_reception(self):
        a = event()
        b = event(received_at_utc="2026-11-24T03:00:01Z")
        self.assertEqual(a["event_id"], b["event_id"])
        self.assertNotEqual(a["age_seconds"], b["age_seconds"])
        batch = m.normalize_batch([a, b])
        self.assertEqual((len(batch["events"]), batch["duplicates"]), (1, 1))

    def test_distinct_observations_not_merged(self):
        a = event()
        b = event(state="DEGRADED", details={"switch_members": 1})
        self.assertNotEqual(a["event_id"], b["event_id"])
        self.assertEqual(len(m.normalize_batch([a, b])["events"]), 2)

    def test_out_of_order_retained(self):
        a = event()
        b = event(observed_at_utc="2026-11-24T02:59:45Z")
        batch = m.normalize_batch([a, b])
        self.assertEqual(batch["out_of_order"], 1)
        self.assertEqual(batch["events"], [b, a])

    def test_out_of_order_distinct_stream_not_counted(self):
        a = event()
        b = event(resource_id="LACP_S1", site="S1",
                  observed_at_utc="2026-11-24T02:59:45Z")
        self.assertEqual(m.normalize_batch([a, b])["out_of_order"], 0)

    def test_missing_timestamp_sorted_last(self):
        a = event(available=False)
        b = event()
        self.assertEqual(m.normalize_batch([a, b])["events"], [b, a])

    def test_conflicting_id_rejected(self):
        a = event()
        b = dict(a, state="FAULT")
        with self.assertRaisesRegex(ValueError, "EVENT_ID_CONFLICT"):
            m.normalize_batch([a, b])

    def test_empty_batch(self):
        batch = m.normalize_batch([])
        self.assertEqual(batch["events"], [])
        self.assertFalse(batch["network_mutations_authorized"])


if __name__ == "__main__":
    unittest.main()
