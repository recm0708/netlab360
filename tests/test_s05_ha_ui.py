"""S05: regresión de fecha Panamá y presentación principal/respaldo HTTP."""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "servicios/topologia-s05/index.html"


class HAUserInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_same_formatter_for_vm_clock_and_http_ha_timestamp(self):
        self.assertIn("function formatPanamaStamp(value)", self.html)
        self.assertIn('formatPanamaStamp(ha.observed_at_utc)', self.html)
        self.assertIn('formatPanamaStamp(value)', self.html)
        self.assertIn('timeZone:"America/Panama"', self.html)
        self.assertNotIn('+(ha.observed_at_utc||"sin hora")', self.html)
        self.assertIn("Observado desde S2 · ", self.html)

    def test_real_js_date_in_panama_and_no_raw_iso(self):
        snippet = re.search(
            r"function formatPanamaStamp\(value\)\{[\s\S]*?\n\}\n"
            r"function formatVMClock\(data\)\{[\s\S]*?\n\}",
            self.html,
        )
        self.assertIsNotNone(snippet)
        script = r"""
const vm = require("node:vm");
const snippet=process.argv[1];
const context=vm.createContext({});
vm.runInContext(snippet+
 'globalThis.result={' +
 'ha:formatPanamaStamp("2026-11-11T14:15:50+00:00"),' +
 'vm:formatVMClock({vm_clock:{panama:"2026-11-11T09:15:50-05:00"}}),' +
 'bad:formatPanamaStamp("unparseable-date")};',context);
const d=context.result;
if(!d.ha.includes("9:15:50")||!d.ha.includes("Panamá (UTC−5)"))
 throw Error("HA no se convirtió a Panamá: "+d.ha);
if(!d.vm.includes("9:15:50")||!d.vm.startsWith("Hora de la VM · "))
 throw Error("Reloj VM con formato distinto: "+d.vm);
if(d.ha.includes("T14:15:50")||d.bad!==null)
 throw Error("ISO sin convertir o fecha inválida aceptada");
console.log("S05_HA_FORMATO_HORA_PANAMA=OK");
"""
        r = subprocess.run(
            ["node", "-e", script, snippet.group(0)],
            capture_output=True, text=True, timeout=10
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("S05_HA_FORMATO_HORA_PANAMA=OK", r.stdout)

    def test_main_http_rail_does_not_cover_ip_labels(self):
        self.assertIn('a.x-124', self.html)
        self.assertIn('b.x-84', self.html)
        self.assertIn('txt("PRINCIPAL",a.x-175', self.html)
        self.assertIn('txt("HTTP",a.x-175', self.html)
        self.assertIn('RESPALDO HTTP', self.html)
        self.assertIn('class:"ha-application-link "+state', self.html)
        self.assertIn(".ha-application-link.selected", self.html)
        self.assertIn(".ha-application-link.standby", self.html)
        self.assertIn('txt("SERVIDOR",x,y-3', self.html)
        self.assertIn("width:168,height:52", self.html)
        self.assertIn("rows?1140+(rows-1)*106", self.html)

    def test_ui_keeps_application_selection_separate_from_wan(self):
        self.assertIn('appText(item.application_selection)', self.html)
        self.assertIn('item.type==="wan"?routeText(item.route_selection)', self.html)
        self.assertIn('Backend HTTP seleccionado:', self.html)
        self.assertIn('data.ha_service', self.html)
        self.assertNotIn('body.presentation .ha-overview{display:none}', self.html)


if __name__ == "__main__":
    unittest.main()
