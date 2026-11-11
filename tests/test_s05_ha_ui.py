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
        self.assertIn('a.x-172', self.html)
        self.assertIn('b.x-84', self.html)
        self.assertIn('const middleY=(a.y+b.y)/2;', self.html)
        self.assertIn('txt("PRINCIPAL",a.x-80,middleY+10', self.html)
        self.assertIn('txt("HTTP",a.x-80,middleY+28', self.html)
        self.assertIn('const backupLabelX=(a.x+b.x)/2;', self.html)
        self.assertIn('const backupLabelY=Math.min(a.y,b.y)-34;', self.html)
        self.assertIn('txt("RESPALDO HTTP",backupLabelX,backupLabelY,', self.html)
        self.assertIn('class:"ha-application-link "+state', self.html)
        self.assertIn(".ha-application-link.selected", self.html)
        self.assertIn(".ha-application-link.standby", self.html)
        self.assertIn('txt("SERVIDOR",x,y-3', self.html)
        self.assertIn("width:168,height:52", self.html)
        self.assertIn("rows?1140+(rows-1)*140", self.html)
        self.assertIn('y:1040+i*140', self.html)
        self.assertIn('const y=1040+i*140;', self.html)

    def test_main_http_rail_and_label_clearance(self):
        # Geometría SVG determinista del NOC, en coordenadas viewBox.
        x = 270
        upper_y, lower_y = 1040, 1180
        detail_y = upper_y + 52
        rail_x = x - 172
        self.assertGreater(rail_x, 36)  # Dentro del panel.
        self.assertLess(rail_x, x - 140)  # Fuera de la anotación IP.
        midpoint = (upper_y + lower_y) / 2
        label_top = midpoint + 10 - 14  # Primera línea, altura SVG 14.
        label_bottom = midpoint + 28
        lower_card_top = lower_y - 26
        self.assertGreater(label_top, detail_y + 8)
        self.assertLess(label_bottom, lower_card_top - 8)

    def test_backup_http_label_above_diagonal_without_node_overlap(self):
        # SVG: etiqueta de respaldo sobre la diagonal, entre HQ y S1.
        # Fórmula dependiente de ambos nodos: se reutiliza al ampliar sedes.
        x_hq, x_s1 = 270, 720
        y_hq = y_s1 = 1040
        label_x = (x_hq + x_s1) / 2
        label_baseline_y = min(y_hq, y_s1) - 34
        server_top = min(y_hq, y_s1) - 26
        self.assertEqual(label_x, 495)
        self.assertLess(label_baseline_y, server_top - 6)
        self.assertGreater(label_baseline_y - 14, 966 + 16)
        self.assertNotIn(
            'txt("RESPALDO HTTP",(a.x+b.x)/2,(a.y+b.y)/2-16',
            self.html,
        )

    def test_ui_keeps_application_selection_separate_from_wan(self):
        self.assertIn('appText(item.application_selection)', self.html)
        self.assertIn('item.type==="wan"?routeText(item.route_selection)', self.html)
        self.assertIn('Backend HTTP seleccionado:', self.html)
        self.assertIn('data.ha_service', self.html)
        self.assertNotIn('body.presentation .ha-overview{display:none}', self.html)


if __name__ == "__main__":
    unittest.main()
