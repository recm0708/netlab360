"""S06-047: NOC IA opcional, sin prometer estado global ni mutar redes."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "servicios/topologia-s05/app.py"
UI = ROOT / "servicios/topologia-s05/index.html"
spec = importlib.util.spec_from_file_location("netlab360_s06_047_noc", APP)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sample(route="HQ_A_S1", observed=None):
    if observed is None:
        observed = datetime.now(timezone.utc).isoformat()
    return {
        "schema": "NETLAB360_S06_046_FRESH_INFERENCE_V1",
        "mode": "FRESH_READONLY_EXPLORATORY",
        "route": route, "observed_at_utc": observed,
        "age_seconds": .8, "fresh_telemetry_verified": True,
        "ground_truth_label": "UNKNOWN",
        "new_independent_validation": False,
        "production_deployment_authorized": False,
        "network_mutations_authorized": False,
        "model_generalization_demonstrated": False,
        "binary_consensus": "NORMAL",
        "operational_state": "NORMAL",
        "reason": "BASELINE_AND_UNANIMOUS_NORMAL_SCOPED",
        "predictions": {
            "P95_RTT": "NORMAL",
            "IsolationForest": "NORMAL",
            "LogisticRegression": "NORMAL",
        },
        "features": {
            "rtt_avg_ms": .089, "rtt_p95_ms": .100,
            "rtt_mdev_ms": .003, "loss_pct": 0,
        },
        "explanation": {
            "source": "NETLAB360_REAL_HQ_TO_S1_S2",
            "target": "nl360-s02-h-hq-120/eth0",
            "scope": "HQ_CLIENT_EGRESS_NETWORK_STATE",
            "confidence_calibrated": False,
            "model_generalization_demonstrated": False,
        },
    }


class StubReply:
    status = 200

    def __init__(self, payload):
        self.raw = json.dumps(payload).encode()
        self.headers = {"Content-Length": str(len(self.raw))}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, n):
        return self.raw[:n]


class BridgeTests(unittest.TestCase):
    def test_valid_source_yields_scoped_normal(self):
        value = m._s06_ai_validate("HQ_A_S1", sample())
        self.assertEqual(value["state"], "NORMAL")
        self.assertEqual(value["ground_truth"], "UNKNOWN")
        self.assertTrue(value["available"])
        self.assertEqual(value["methods"]["LogisticRegression"], "NORMAL")
        self.assertFalse(value["production_deployment_authorized"])
        self.assertFalse(value["network_mutations_authorized"])

    def test_wrong_route_fails(self):
        with self.assertRaisesRegex(ValueError, "CONTRACT|INVALID|ROUTE"):
            m._s06_ai_validate("HQ_A_S2", sample("HQ_A_S1"))

    def test_invalid_schema_fails(self):
        d = sample()
        d["schema"] = "fake"
        with self.assertRaises(ValueError):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_untrusted_ground_truth_fails(self):
        d = sample()
        d["ground_truth_label"] = "NORMAL"
        with self.assertRaises(ValueError):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_production_authorized_fails(self):
        d = sample()
        d["production_deployment_authorized"] = True
        with self.assertRaises(ValueError):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_missing_or_extra_models_fail(self):
        d = sample()
        del d["predictions"]["P95_RTT"]
        with self.assertRaisesRegex(ValueError, "METHODS"):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_inconsistent_consensus_fails(self):
        d = sample()
        d["predictions"]["P95_RTT"] = "DEGRADED"
        with self.assertRaisesRegex(ValueError, "CONSENSUS"):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_degradation_indication_remains_unknown(self):
        d = sample()
        d["predictions"] = {k: "DEGRADED" for k in m.S06_AI_METHODS}
        d["binary_consensus"] = "DEGRADED"
        d["operational_state"] = "UNKNOWN"
        d["reason"] = "DEGRADATION_INDICATION_UNCONFIRMED"
        out = m._s06_ai_validate("HQ_A_S1", d)
        self.assertEqual(out["state"], "UNKNOWN")
        self.assertEqual(out["consensus"], "DEGRADED")

    def test_disagreement_remains_unknown(self):
        d = sample()
        d["predictions"]["IsolationForest"] = "DEGRADED"
        d["binary_consensus"] = "UNKNOWN"
        d["operational_state"] = "UNKNOWN"
        d["reason"] = "MODEL_DISAGREEMENT"
        out = m._s06_ai_validate("HQ_A_S1", d)
        self.assertEqual(out["state"], "UNKNOWN")

    def test_stale_source_fails(self):
        old = (datetime.now(timezone.utc) - timedelta(seconds=34)).isoformat()
        d = sample(observed=old)
        with self.assertRaisesRegex(ValueError, "STALE"):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_future_source_fails(self):
        future = (datetime.now(timezone.utc) + timedelta(seconds=6)).isoformat()
        d = sample(observed=future)
        with self.assertRaisesRegex(ValueError, "STALE"):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_timestamp_without_timezone_fails(self):
        d = sample(observed="2026-11-23T09:00:00")
        with self.assertRaisesRegex(ValueError, "ZONE"):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_loss_invalid_fails(self):
        d = sample()
        d["features"]["loss_pct"] = 33.33
        with self.assertRaises(ValueError):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_nonfinite_feature_fails(self):
        d = sample()
        d["features"]["rtt_avg_ms"] = float("nan")
        with self.assertRaises(ValueError):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_provenance_change_fails(self):
        d = sample()
        d["explanation"]["source"] = "invented"
        with self.assertRaisesRegex(ValueError, "PROVENANCE"):
            m._s06_ai_validate("HQ_A_S1", d)

    def test_offline_route_never_changes_graph(self):
        class FakeOpener:
            def open(self, url, timeout=None):
                raise OSError("unavailable")
        with patch.object(m, "build_opener", return_value=FakeOpener()):
            result = m.s06_diagnostics()
        self.assertEqual(result["schema"], "NETLAB360_S06_047_NOC_AI_ADAPTER_V1")
        self.assertEqual(set(result["routes"]), set(m.S06_AI_ROUTES))
        self.assertTrue(all(row["state"] == "UNKNOWN" and not row["available"]
                            for row in result["routes"].values()))
        self.assertTrue(result["graph_s05_independent"])

    def test_both_routes_are_fixed_loopback_reads(self):
        class FakeOpener:
            def __init__(self):
                self.calls = []

            def open(self, url, timeout=None):
                self.calls.append((url, timeout))
                return StubReply(sample(url.rsplit("=", 1)[1]))
        opener = FakeOpener()
        with patch.object(m, "build_opener", return_value=opener):
            result = m.s06_diagnostics()
        self.assertTrue(all(row["available"] for row in result["routes"].values()))
        self.assertEqual([u for u, _ in opener.calls], [
            m.S06_AI_ENDPOINT + "HQ_A_S1",
            m.S06_AI_ENDPOINT + "HQ_A_S2",
        ])
        self.assertTrue(all(t <= 1.2 for _, t in opener.calls))
        self.assertFalse(result["network_mutations_authorized"])

    def test_a_failure_does_not_hide_other_route(self):
        class FakeOpener:
            def open(self, url, timeout=None):
                if url.endswith("HQ_A_S1"):
                    raise OSError("offline")
                return StubReply(sample("HQ_A_S2"))
        with patch.object(m, "build_opener", return_value=FakeOpener()):
            result = m.s06_diagnostics()
        self.assertFalse(result["routes"]["HQ_A_S1"]["available"])
        self.assertTrue(result["routes"]["HQ_A_S2"]["available"])

    def test_unexpected_model_fields_not_forwarded(self):
        d = sample()
        d["secret_untrusted_key"] = "not for browser"
        row = m._s06_ai_validate("HQ_A_S1", d)
        self.assertNotIn("secret_untrusted_key", row)

    def test_s05_existing_graph_unchanged_contract(self):
        text = APP.read_text()
        self.assertIn('elif route == "/api/v1/graph":', text)
        self.assertIn('elif route == "/healthz":', text)
        self.assertIn('elif route == "/api/v1/s06/diagnostics":', text)
        self.assertIn("server.serve_forever()", text)

    def test_s06_ui_ids_and_no_mutation_actions(self):
        html = UI.read_text()
        for marker in ('id="ai-s1-state"', 'id="ai-s2-state"',
                       'id="ai-s1-meta"', 'id="ai-s2-meta"',
                       'function updateAI()', 'aiRenderRoute(',
                       'updateAI();setInterval(updateAI,3000);'):
            self.assertIn(marker, html)
        self.assertNotIn("ai-script-shell", html)
        self.assertIn('state.textContent=', html)


if __name__ == "__main__":
    unittest.main()
