"""Pruebas offline del catálogo de adquisición y configuración preservada."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContinuousTests(unittest.TestCase):
    def run_code(self, name, code):
        subprocess.run([sys.executable, "-I", "-B", "-c", code,
                        str(ROOT / "scripts/s08" / name)], check=True, timeout=10)

    def test_fixed_routes(self):
        self.run_code("sondas_continuas.py", """
import runpy, sys
m = runpy.run_path(sys.argv[1])
select = m["selection"]
assert select("/probe/hq-s1-icmp", "HQ")["target"] == "10.71.20.20"
assert select("/probe/s2-hq-http", "S2")["target"] == "http://10.70.20.23:8080/api/v1/service"
for path, origin in (("/probe/hq-s1-icmp", "S2"),
                     ("/probe?target=192.168.47.40", None),
                     ("/probe/hq-s1-icmp?target=x", None),
                     ("/probe/../s2-hq-http", None)):
    try:
        select(path, origin)
    except ValueError:
        continue
    raise AssertionError("Unexpected target accepted")
""")

    def test_measured_failure(self):
        self.run_code("sondas_continuas.py", """
import runpy, sys
m = runpy.run_path(sys.argv[1])
item = m["selection"]("/probe/s2-hq-http")
raw = b"probe_success 0\\nprobe_duration_seconds 3\\nprobe_http_status_code 503\\n"
assert b"probe_success 0\\n" in m["checked_metrics"](raw, item)
for bad in (b"", b"probe_success 1\\nprobe_duration_seconds 1\\nprobe_http_status_code 503\\n",
            b"probe_success 1\\nprobe_success 0\\nprobe_duration_seconds 1\\n"):
    try:
        m["checked_metrics"](bad, item)
    except ValueError:
        continue
    raise AssertionError("Invalid data accepted")
""")

    def test_prometheus_preservation(self):
        self.run_code("desplegar_sondas_continuas.py", """
import runpy, sys
from pathlib import Path
m = runpy.run_path(sys.argv[1])
source = Path(sys.argv[1]).resolve().parents[2] / "servicios/observabilidad/prometheus/s04-prometheus.yml"
old = source.read_text()
new = m["render"](old)
assert new.count("job_name: netlab360-s04-multisede") == 1
assert new.count("job_name: netlab360-s08-blackbox") == 1
assert "rules/s04-alerts.yml" in new
assert "scrape_interval: 2s" in new
assert "scrape_interval: 10s" in new
assert new.count('targets: ["127.0.0.1:9116"]') == 5
try:
    m["render"](new)
except ValueError:
    pass
else:
    raise AssertionError("Duplicate configuration accepted")
""")


if __name__ == "__main__":
    unittest.main()
