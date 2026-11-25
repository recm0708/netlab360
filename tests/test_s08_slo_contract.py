"""Pruebas offline del catálogo Blackbox y semántica de presupuesto de errores."""
import importlib.util
from pathlib import Path
import sys
import subprocess
import unittest

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_slo_test", PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_slo_test import slo_contract as S


class SLOTests(unittest.TestCase):
    def test_catalog(self):
        rows = [S.probe(key) for key in S.PROBES]
        self.assertEqual(len(rows), 5)
        self.assertEqual({r["origin"] for r in rows}, {"HQ", "S2"})
        self.assertEqual({r["module"] for r in rows}, {"icmp_v4", "tcp_v4", "http_service"})
        self.assertEqual(S.probe("s2-hq-http")["target"], "http://10.70.20.23:8080/api/v1/service")

    def test_no_free_target(self):
        for target in ("192.168.47.40", "http://127.0.0.1", None, True, {}):
            with self.assertRaises(ValueError):
                S.probe(target)

    def test_absent(self):
        row = S.summarize(5, 0, 0, 0, 0)
        self.assertEqual(row["quality"], "ABSENT")
        self.assertIsNone(row["observed_availability_pct"])
        self.assertIsNone(row["burn_rate_observed"])
        self.assertIsNone(row["meets_observed_target"])

    def test_partial_no_false_pass(self):
        row = S.summarize(5, 30, 28, 27, 27)
        self.assertEqual(row["quality"], "PARTIAL")
        self.assertEqual(row["observed_availability_pct"], 100)
        self.assertEqual(row["unobserved_scrapes"], 3)
        self.assertIsNone(row["meets_observed_target"])

    def test_error_budget_boundary(self):
        row = S.summarize(60, 360, 360, 360, 357)
        self.assertEqual(row["allowed_failures_observed"], 3)
        self.assertEqual(row["remaining_budget_observed"], 0)
        self.assertTrue(row["meets_observed_target"])
        failed = S.summarize(60, 360, 360, 360, 356)
        self.assertFalse(failed["meets_observed_target"])
        self.assertGreater(failed["burn_rate_observed"], 1)

    def test_nominal_shortfall(self):
        row = S.summarize(15, 89, 89, 89, 89)
        self.assertEqual(row["nominal_slots"], 90)
        self.assertEqual(row["nominal_shortfall"], 1)
        self.assertIsNone(row["meets_observed_target"])

    def test_pilot_icmp_capability_scope(self):
        # Importar en otro intérprete para no mezclar el paquete api de los demás tests.
        pilot = Path(__file__).resolve().parents[1] / "scripts/s08/piloto_sondas_y_stream.py"
        code = """
import runpy, sys
args = runpy.run_path(sys.argv[1])["unit_args"]
hq = "nl360-s02-h-hq-120"
s2 = "nl360-s02-h-s2-320"
for unit, ns in (("pilot-bb-hq", hq), ("pilot-bb-s2", s2)):
    command = args(unit, ns, icmp_raw=True)
    assert "--property=CapabilityBoundingSet=CAP_NET_RAW" in command
    assert "--property=AmbientCapabilities=CAP_NET_RAW" in command
    assert "--property=NoNewPrivileges=yes" in command
    assert "--property=User=netlab360-s08-worker" in command
for unit, ns in (("pilot-am", None), ("pilot-tcp-10s-tx", hq)):
    command = args(unit, ns)
    assert "--property=CapabilityBoundingSet=" in command
    assert "--property=AmbientCapabilities=" in command
for unit, ns, root in (("pilot-am", hq, False), ("pilot-bb-hq", None, False),
                       ("pilot-bb-hq", "nl360-s02-h-s1-220", False),
                       ("pilot-bb-hq", hq, True)):
    try:
        args(unit, ns, root=root, icmp_raw=True)
    except ValueError:
        continue
    raise AssertionError("ICMP capability granted outside permitted scope")
"""
        subprocess.run([sys.executable, "-I", "-B", "-c", code, str(pilot)],
                       check=True, timeout=10)

    def test_cached_package_integrity(self):
        pilot = Path(__file__).resolve().parents[1] / "scripts/s08/piloto_sondas_y_stream.py"
        code = """
import hashlib, runpy, sys, tempfile
from pathlib import Path
verify = runpy.run_path(sys.argv[1])["package_digest"]
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "test.deb"
    path.write_bytes(b"example")
    digest = hashlib.sha256(b"example").hexdigest()
    meta = "Package: demo\\nVersion: 1\\nArchitecture: amd64\\nSize: 7\\nSHA256: " + digest
    assert verify(path, meta, "demo", "1") == digest
    path.write_bytes(b"changed")
    try:
        verify(path, meta, "demo", "1")
    except ValueError as exc:
        assert str(exc) == "PACKAGE_DIGEST"
    else:
        raise AssertionError("Tampered package accepted")
"""
        subprocess.run([sys.executable, "-I", "-B", "-c", code, str(pilot)],
                       check=True, timeout=10)

    def test_alertmanager_uses_extracted_template(self):
        pilot = Path(__file__).resolve().parents[1] / "scripts/s08/piloto_sondas_y_stream.py"
        code = """
import runpy, sys, tempfile
from pathlib import Path
from types import SimpleNamespace
resolve = runpy.run_path(sys.argv[1])["alertmanager_template_args"]
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory) / "usr"
    binary = root / "bin/prometheus-alertmanager"
    template = root / "share/prometheus/alertmanager/default.tmpl"
    template.parent.mkdir(parents=True)
    template.write_text("test")
    resolve.__globals__["run"] = lambda args: SimpleNamespace(
        stdout="  --template.default=PATH", stderr="")
    assert resolve(binary) == ["--template.default=" + str(template)]
    template.unlink()
    try:
        resolve(binary)
    except ValueError as exc:
        assert str(exc).startswith("ALERTMANAGER_TEMPLATE_MISSING:")
    else:
        raise AssertionError("Missing template accepted")
"""
        subprocess.run([sys.executable, "-I", "-B", "-c", code, str(pilot)],
                       check=True, timeout=10)

    def test_iperf_stream_only(self):
        pilot = Path(__file__).resolve().parents[1] / "scripts/s08/piloto_sondas_y_stream.py"
        code = """
import json, runpy, sys, tempfile
from pathlib import Path
module = runpy.run_path(sys.argv[1])
flags = module["stream_args"]
events = module["events"]
assert flags(["/usr/bin/iperf3", "-J", "-P", "1", "--json-stream-full-output"]) == [
    "/usr/bin/iperf3", "-P", "1", "--json-stream", "--forceflush"]
assert flags(flags(["/usr/bin/iperf3"])) == flags(["/usr/bin/iperf3"])
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "stream.jsonl"
    frames = [{"event": event, "data": {}} for event in ("start", "interval", "end")]
    path.write_text("".join(json.dumps(row) + "\\n" for row in frames) + "{")
    assert events(path, partial=True) == frames
    try:
        events(path)
    except json.JSONDecodeError:
        pass
    else:
        raise AssertionError("Incomplete final frame accepted")
    path.write_text("".join(json.dumps(row) + "\\n" for row in frames))
    assert events(path) == frames
"""
        subprocess.run([sys.executable, "-I", "-B", "-c", code, str(pilot)],
                       check=True, timeout=10)

    def test_invalid_counts(self):
        for args in ((3, 30, 30, 30, 30), (5, True, 1, 1, 1), (5, 1, 2, 1, 1),
                     (5, 30, 20, 21, 21), (5, 30, 30, 20, 21)):
            with self.assertRaises(ValueError):
                S.summarize(*args)


if __name__ == "__main__":
    unittest.main()
