"""Regresión geométrica estática del visor S05: evitar solapamientos de texto/equipo."""
from pathlib import Path
import re
import unittest

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
        for site, top in (("S1", 155), ("S2", 540)):
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
        self.assertIn('if(selectedId)pick(selectedId)', self.html)
        self.assertIn('txt("RTR",x,y-2', self.html)
        self.assertIn('txt(item.label,x,y+18', self.html)


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
