"""Regresión geométrica estática del visor S05: evitar solapamientos de texto/equipo."""
from pathlib import Path
import re
import unittest
import subprocess

PAGE = (Path(__file__).resolve().parents[1] /
        "servicios/topologia-s05/index.html")


class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        pattern = (
            r"\b(HQ|S1|S2):\{x:(\d+),y:(\d+),w:(\d+),h:(\d+),"
            r"cx:(\d+),ry:(\d+),sy:(\d+),hy:(\d+),step:(\d+)\}"
        )
        cls.geo = {
            parts[0]: dict(zip(
                ("x", "y", "w", "h", "cx", "ry", "sy", "hy", "step"),
                map(int, parts[1:])
            ))
            for parts in re.findall(pattern, cls.html)
        }

    def test_three_site_coordinates_and_header_clearance(self):
        self.assertEqual(set(self.geo), {"HQ", "S1", "S2"})
        for site, g in self.geo.items():
            with self.subTest(site=site):
                self.assertGreaterEqual(g["ry"] - 32, g["y"] + 92)
                self.assertGreaterEqual(g["sy"] - 25, g["ry"] + 32 + 20)
                self.assertGreaterEqual(g["hy"] - 26, g["sy"] + 25 + 15)
                self.assertLessEqual(g["hy"] + 26, g["y"] + g["h"] - 18)

    def test_hosts_within_each_site_card(self):
        for site, g in self.geo.items():
            with self.subTest(site=site):
                left = g["cx"] - g["step"] - 55
                right = g["cx"] + g["step"] + 55
                self.assertGreaterEqual(left, g["x"] + 15)
                self.assertLessEqual(right, g["x"] + g["w"] - 15)

    def wan_paths(self):
        pattern = (
            r'"(WAN-(PRIMARIA|RESPALDO)-HQ-(S1|S2))":'
            r'\{sx:(\d+),sy:(\d+),kneeX:(\d+),laneY:(\d+),'
            r'entryX:(\d+),tailY:(\d+),dx:(\d+),dy:(\d+),'
            r'lx:(\d+),ly:(\d+)\}'
        )
        result = {}
        for m in re.finditer(pattern, self.html):
            name, kind, site = m.group(1, 2, 3)
            keys = ("sx", "sy", "kneeX", "laneY", "entryX",
                    "tailY", "dx", "dy", "lx", "ly")
            result[name] = (kind, site, dict(zip(
                keys, map(int, m.groups()[3:])
            )))
        return result

    def test_wan_links_connect_router_ports_and_have_lanes(self):
        links = self.wan_paths()
        self.assertEqual(len(links), 4)
        self.assertIn("function drawWanBundles(parent)", self.html)
        self.assertIn('" H "+g.kneeX+" V "+g.laneY+', self.html)
        self.assertIn('" H "+g.entryX+" V "+g.tailY+" H "+g.dx;', self.html)
        self.assertNotIn('PRINCIPAL: CONTINUA · RESPALDO: DISCONTINUA', self.html)
        hq = self.geo["HQ"]
        for name, (kind, site, g) in links.items():
            with self.subTest(wan=name):
                branch = self.geo[site]
                # Los extremos reposan sobre el perímetro del icono router,
                # no sobre switches, hosts ni las tarjetas WAN.
                rs = ((g["sx"]-hq["cx"])**2+(g["sy"]-hq["ry"])**2)**0.5
                rd = ((g["dx"]-branch["cx"])**2+
                      (g["dy"]-branch["ry"])**2)**0.5
                self.assertAlmostEqual(rs, 32, delta=3)
                self.assertAlmostEqual(rd, 32, delta=3)
                self.assertGreater(g["kneeX"], hq["x"]+hq["w"])
                self.assertLess(g["entryX"], branch["x"])
                self.assertEqual(g["ly"], g["laneY"])
                self.assertGreaterEqual(g["lx"]-130, 605+20)
                self.assertLessEqual(g["lx"]+130, 950-20)
                self.assertEqual(g["laneY"] < 400, site=="S1")
                if kind=="RESPALDO":
                    self.assertIn('.wan-line.backup{stroke-dasharray:', self.html)

    def test_circuit_labels_have_no_overlap_or_header_collision(self):
        links=self.wan_paths()
        self.assertEqual(len(links), 4)
        for site, top in (("S1", 155), ("S2", 510)):
            subset=[g for _kind, where, g in links.values() if where==site]
            self.assertEqual(len(subset), 2)
            a,b=sorted(g["laneY"] for g in subset)
            self.assertGreaterEqual(b-a, 52)
            # Titulo a +32; pill de enlace ocupa lane ±17.
            self.assertGreaterEqual(a-17, top+45)
            self.assertLessEqual(b+17, top+173-14)
        self.assertEqual(self.geo["S1"]["x"], self.geo["S2"]["x"])
        self.assertGreater(self.geo["S2"]["y"]-(
            self.geo["S1"]["y"]+self.geo["S1"]["h"]), 60)

    def test_v6_hq_balanced_and_s2_backup_entry(self):
        hq, s1, s2 = self.geo["HQ"], self.geo["S1"], self.geo["S2"]
        # HQ permanece a la misma distancia vertical aproximada de S1 y S2.
        midpoint = (s1["ry"] + s2["ry"]) / 2
        self.assertLessEqual(abs(hq["ry"] - midpoint), 15)

        links = self.wan_paths()
        main_s2 = links["WAN-PRIMARIA-HQ-S2"][2]
        backup_s2 = links["WAN-RESPALDO-HQ-S2"][2]
        main_s1 = links["WAN-PRIMARIA-HQ-S1"][2]
        backup_s1 = links["WAN-RESPALDO-HQ-S1"][2]

        # Salidas ordenadas del lado derecho de R-HQ y sin invertir S2.
        start_ys = [
            main_s1["sy"], backup_s1["sy"],
            main_s2["sy"], backup_s2["sy"],
        ]
        self.assertEqual(start_ys, sorted(start_ys))
        self.assertGreaterEqual(main_s2["laneY"], 550)
        self.assertLessEqual(backup_s2["laneY"], 650)
        # El respaldo de S2 se acerca al router sin codo lejano/excesivo.
        self.assertLessEqual(
            abs(backup_s2["tailY"] - backup_s2["laneY"]), 30
        )
        self.assertLessEqual(
            abs(main_s2["tailY"] - main_s2["laneY"]), 80
        )
        self.assertGreater(
            backup_s2["laneY"] - main_s2["laneY"], 60
        )
        # Entrada principal más a la derecha que el retorno de respaldo:
        # evita que la vertical principal cruce la fila del respaldo.
        self.assertGreaterEqual(
            main_s2["entryX"] - backup_s2["entryX"], 20
        )
        self.assertLess(main_s2["entryX"], s2["x"])
        self.assertLess(backup_s2["entryX"], s2["x"])
        # Conservamos el orden funcional de las VLAN de ambas sucursales.
        self.assertLess(s1["ry"], s1["sy"])
        self.assertLess(s1["sy"], s1["hy"])
        self.assertLess(s2["ry"], s2["sy"])
        self.assertLess(s2["sy"], s2["hy"])
        self.assertIn('{site:"S2",y:510}', self.html)

    def test_wan_circuits_do_not_cross_each_other(self):
        links=self.wan_paths()

        def segments(g):
            path=[
                (g["sx"],g["sy"]),
                (g["kneeX"],g["sy"]),
                (g["kneeX"],g["laneY"]),
                (g["entryX"],g["laneY"]),
                (g["entryX"],g["tailY"]),
                (g["dx"],g["dy"]),
            ]
            return list(zip(path,path[1:]))

        def intersects(a,b):
            (x1,y1),(x2,y2)=a
            (x3,y3),(x4,y4)=b
            av,bv=x1==x2,x3==x4
            if av and not bv:
                return (min(y1,y2)<=y3<=max(y1,y2) and
                        min(x3,x4)<=x1<=max(x3,x4))
            if not av and bv:
                return (min(x1,x2)<=x3<=max(x1,x2) and
                        min(y3,y4)<=y1<=max(y3,y4))
            if av and bv:
                return x1==x3 and max(min(y1,y2),min(y3,y4))<=min(max(y1,y2),max(y3,y4))
            return y1==y3 and max(min(x1,x2),min(x3,x4))<=min(max(x1,x2),max(x3,x4))

        names=list(links)
        for i,first in enumerate(names):
            for second in names[i+1:]:
                with self.subTest(first=first,second=second):
                    self.assertFalse(any(
                        intersects(s1,s2)
                        for s1 in segments(links[first][2])
                        for s2 in segments(links[second][2])
                    ),"No se deben cruzar circuitos WAN diferentes")

    def test_accessibility_presentation_mode_and_no_duplicated_router(self):
        self.assertIn('id="focus-toggle"', self.html)
        self.assertIn('body.presentation .canvas', self.html)
        self.assertIn('aria-pressed', self.html)
        self.assertIn('function drawExtensions', self.html)
        self.assertIn('function drawInSite', self.html)
        self.assertNotIn('if(core)drawDevice(core,b.cx,b.ry)', self.html)
        self.assertIn("renderSelection();", self.html)
        self.assertNotIn("if(selectedId)pick(selectedId)", self.html)
        self.assertIn('txt("RTR",x,y-2', self.html)
        self.assertIn('txt(item.label,x,y+18', self.html)


    def test_v72_selection_is_green_and_not_a_false_route_status(self):
        """Selección independiente del estado FIB y sin bordes violetas."""
        self.assertIn("--focus:#b7ff69", self.html)
        self.assertIn(".wan-circuit.selected .wan-selection-halo", self.html)
        self.assertIn('class:"wan-selection-halo"', self.html)
        self.assertIn(".wan-circuit.selected .wan-line.primary.route-selected", self.html)
        self.assertIn(".wan-line.backup.route-selected", self.html)
        self.assertIn(".wan-line.route-standby", self.html)
        self.assertIn(".wan-line.route-unavailable", self.html)
        self.assertIn(".device.offline.selected", self.html)
        self.assertNotIn("violeta", self.html.lower())
        self.assertNotIn("morado", self.html.lower())
        self.assertNotIn("selection-note", self.html)
        self.assertNotIn("inspector-selected", self.html)
        self.assertIn("Seleccionado por ti", self.html)
        self.assertIn("Código de colores y estados", self.html)

    def test_v72_second_click_deselects_and_refresh_does_not_toggle(self):
        self.assertIn("selectedId=selectedId===id?null:id;", self.html)
        self.assertIn("function renderSelection()", self.html)
        self.assertIn("function clearInspector()", self.html)
        self.assertIn("if(!item){clearInspector();return;}", self.html)
        self.assertIn("n.classList.toggle(\"selected\",active)", self.html)
        self.assertIn('n.setAttribute("aria-pressed",String(active))', self.html)
        self.assertIn("function render(data)", self.html)
        self.assertIn("renderSelection();", self.html)
        self.assertNotIn("if(selectedId)pick(selectedId)", self.html)
        self.assertNotIn('selectedId=id;', self.html)

    def test_v72_real_javascript_toggle_in_node(self):
        """Ejecuta el controlador real de clic sin servicios ni red."""
        function = re.search(r"function pick\(id\)\{[\s\S]*?\n\}", self.html)
        self.assertIsNotNone(function)
        script = r"""
const vm = require("node:vm");
const snippet = process.argv[1];
const context = vm.createContext({});
vm.runInContext(
 "let selectedId=null;let calls=[];" +
 "function renderSelection(){calls.push(selectedId);}" + snippet +
 "pick('WAN1');pick('WAN1');pick('R-HQ');pick('WAN1');" +
 "if(JSON.stringify(calls)!==JSON.stringify(['WAN1',null,'R-HQ','WAN1']))" +
 " throw Error('Toggle JS no reversible: '+JSON.stringify(calls));",
 context
);
console.log("S05_V72_TOGGLE_NODE=OK");
"""
        result = subprocess.run(
            ["node", "-e", script, function.group(0)],
            text=True, capture_output=True, timeout=8, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("S05_V72_TOGGLE_NODE=OK", result.stdout)

    def test_v72_spanish_user_facing_state_labels(self):
        self.assertIn('"active":"ACTIVA"', self.html)
        self.assertIn('"offline":"FUERA DE LÍNEA"', self.html)
        self.assertIn('"unknown":"SIN DATOS"', self.html)
        self.assertIn('topologyText(state)', self.html)
        self.assertIn('Topología SIN DATOS', self.html)
        self.assertIn('Fuera de línea comprobado', self.html)
        self.assertIn('Enrutadores FRR', self.html)
        self.assertIn('Conmutadores virtuales', self.html)
        self.assertIn('Equipos / VLAN', self.html)
        self.assertNotIn('state.toUpperCase()', self.html)
        self.assertNotIn('Topología ACTIVE', self.html)
        self.assertNotIn('Topología OFFLINE', self.html)

    def test_fib_route_color_semantics_and_inspector(self):
        self.assertIn(".wan-line.primary.route-selected", self.html)
        self.assertIn(".wan-line.backup.route-selected", self.html)
        self.assertIn(".wan-line.route-standby", self.html)
        self.assertIn("function routeText(value)", self.html)
        self.assertIn("item.route_selection", self.html)
        self.assertIn('["Selección FIB R-HQ"', self.html)
        self.assertIn('["Próximo salto FIB"', self.html)
        self.assertIn("w.route_selection", self.html)
        self.assertIn("La ruta FIB elegida no acredita tráfico", self.html)

    def test_wiring_never_enters_host_or_switch(self):
        self.assertIn('const yJunction=b.sy+40;', self.html)
        for site, g in self.geo.items():
            with self.subTest(site=site):
                self.assertGreater(g["sy"] + 40, g["sy"] + 25)
                self.assertLess(g["sy"] + 40, g["hy"] - 26)
                self.assertGreater(g["hy"] - 26, g["sy"] + 25)

    def test_vm_panama_clock_and_router_status_badges(self):
        self.assertIn('function formatVMClock(data)', self.html)
        self.assertIn('America/Panama', self.html)
        self.assertIn('data.vm_clock', self.html)
        self.assertIn('Hora de la VM', self.html)
        self.assertIn('site-state-badge', self.html)
        self.assertIn('function drawSiteBox(site,nodes,parent)', self.html)
        self.assertIn('formatVMClock(data)', self.html)


if __name__ == "__main__":
    unittest.main()
