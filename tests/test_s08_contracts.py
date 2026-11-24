"""Validación offline de metadatos S08; sin acceso a fuentes reales."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "s08_contracts", ROOT / "servicios/consola-s08/api/contracts.py")
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

NOW = "2026-11-24T21:20:00+00:00"


def metadata(**changes):
    values = dict(source="NOC_S05", transport="OK",
                  observed_at_utc="2026-11-24T21:19:50+00:00",
                  received_at_utc=NOW, state="NORMAL")
    values.update(changes)
    return m.source_metadata(**values)


class SourceMetadataTests(unittest.TestCase):
    def test_valid(self):
        r = metadata()
        self.assertEqual(r["schema"], m.SCHEMA)
        self.assertEqual((r["quality"], r["state"], r["age_seconds"]),
                         ("VALID", "NORMAL", 10))
        self.assertIs(r["network_mutations_authorized"], False)

    def test_timezone(self):
        self.assertEqual(metadata(observed_at_utc="2026-11-24T16:19:50-05:00"),
                         metadata())

    def test_boundary(self):
        r = metadata(observed_at_utc="2026-11-24T21:19:00Z")
        self.assertEqual(r["quality"], "VALID")

    def test_stale(self):
        r = metadata(observed_at_utc="2026-11-24T21:18:59Z")
        self.assertEqual((r["quality"], r["state"], r["age_seconds"]),
                         ("STALE", "UNKNOWN", 61))

    def test_future(self):
        r = metadata(observed_at_utc="2026-11-24T21:20:01Z")
        self.assertEqual((r["quality"], r["state"]), ("FUTURE", "UNKNOWN"))

    def test_missing_stamp(self):
        r = metadata(observed_at_utc=None)
        self.assertEqual((r["quality"], r["state"]), ("MISSING", "UNKNOWN"))
        self.assertIsNone(r["observed_at_utc"])
        self.assertIsNone(r["age_seconds"])

    def test_invalid_stamps(self):
        for stamp in ("bad", "2026-11-24T21:19:50", 123, True):
            with self.subTest(stamp=stamp):
                r = metadata(observed_at_utc=stamp)
                self.assertEqual((r["quality"], r["state"]), ("INVALID", "UNKNOWN"))

    def test_bad_receipt(self):
        with self.assertRaisesRegex(ValueError, "INVALID_TIMESTAMP"):
            metadata(received_at_utc="2026-11-24T21:20:00")

    def test_unavailable_and_not_started(self):
        for transport in ("UNAVAILABLE", "NOT_STARTED"):
            with self.subTest(transport=transport):
                r = metadata(transport=transport)
                self.assertEqual((r["transport"], r["quality"], r["state"]),
                                 (transport, "MISSING", "UNKNOWN"))
                self.assertIsNone(r["observed_at_utc"])

    def test_invalid_transport_response(self):
        r = metadata(transport="INVALID")
        self.assertEqual((r["quality"], r["state"]), ("INVALID", "UNKNOWN"))

    def test_valid_unknown(self):
        r = metadata(state="UNKNOWN")
        self.assertEqual((r["quality"], r["state"]), ("VALID", "UNKNOWN"))

    def test_inference_age(self):
        r = metadata(source="IA_S06", observed_at_utc="2026-11-24T21:19:29Z")
        self.assertEqual((r["kind"], r["max_age_seconds"], r["quality"], r["state"]),
                         ("INFERENCE", 30, "STALE", "UNKNOWN"))

    def test_advisory_is_not_health(self):
        r = metadata(source="ADVISORY_S07")
        self.assertEqual((r["kind"], r["quality"], r["state"]),
                         ("ADVISORY_SNAPSHOT", "VALID", "UNKNOWN"))

    def test_reject_unknown_source(self):
        for source in ("https://example.org", "/etc/passwd", [], None):
            with self.subTest(source=source):
                with self.assertRaisesRegex(ValueError, "INVALID_SOURCE"):
                    metadata(source=source)

    def test_reject_invalid_enums(self):
        for changes, reason in (({"transport": "200"}, "INVALID_TRANSPORT"),
                                ({"state": "UP"}, "INVALID_STATE")):
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ValueError, reason):
                    metadata(**changes)

    def test_no_authority_for_any_state(self):
        for source in m.SOURCES:
            for state in m.STATES:
                with self.subTest(source=source, state=state):
                    self.assertIs(metadata(source=source, state=state)
                                  ["network_mutations_authorized"], False)


if __name__ == "__main__":
    unittest.main()
