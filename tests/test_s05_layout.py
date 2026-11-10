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
                left = g["cx"] - g["step"] - 63
                right = g["cx"] + g["step"] + 63
                self.assertGreaterEqual(left, g["x"] + 15)
                self.assertLessEqual(right, g["x"] + g["w"] - 15)

    def test_wan_links_are_orthogonal_router_to_router(self):
        pattern = (
            r'"(WAN-(PRIMARIA|RESPALDO)-HQ-(S1|S2))":'
            r'\{sx:(\d+),sy:(\d+),outX:(\d+),crossY:(\d+),'
            r'edgeX:(\d+),dy:(\d+),dx:(\d+),lx:(\d+),ly:(\d+)\}'
        )
        links = {}
        for m in re.finditer(pattern, self.html):
            full, kind, site = m.group(1, 2, 3)
            vals = list(map(int, m.groups()[3:]))
            links[full] = (kind, site, dict(zip(
                ("sx", "sy", "outX", "crossY", "edgeX",
                 "dy", "dx", "lx", "ly"), vals
            )))
        self.assertEqual(len(links), 4, "Deben existir cuatro circuitos WAN")
        hq = self.geo["HQ"]
        self.assertEqual(hq["y"] + hq["h"], 362)
        self.assertIn('" H "+g.outX+', self.html)
        self.assertIn('" V "+g.crossY+', self.html)
        self.assertIn('" H "+g.edgeX+', self.html)
        self.assertIn('" V "+g.dy+', self.html)
        self.assertIn('" H "+g.dx;', self.html)
        self.assertNotIn('return "M "+x1+" "+y1+" C "', self.html)

        for name, (kind, site, g) in links.items():
            with self.subTest(wan=name):
                remote = self.geo[site]
                # Tanto el origen como el destino se fijan a laterales
                # del símbolo router, NO a los hosts ni al borde de VLAN.
                self.assertLessEqual(abs(g["sx"] - hq["cx"]), 33)
                self.assertEqual(abs(g["sy"] - hq["ry"]), 12)
                self.assertLessEqual(abs(g["dx"] - remote["cx"]), 33)
                self.assertEqual(abs(g["dy"] - remote["ry"]), 12)
                self.assertGreater(g["crossY"], hq["y"] + hq["h"] + 15)
                self.assertLess(g["crossY"], remote["y"] - 20)
                self.assertGreater(g["dy"], remote["y"] + 105)
                self.assertEqual(g["crossY"], g["ly"])
                self.assertGreaterEqual(g["lx"] - 114, 0)
                self.assertLessEqual(g["lx"] + 114, 1440)
                self.assertGreaterEqual(g["crossY"] - 23, 362 + 15)
                self.assertLessEqual(g["crossY"] + 23, 516 - 20)
                if kind == "PRIMARIA":
                    self.assertTrue(
                        g["edgeX"] < remote["x"] if site == "S1"
                        else g["edgeX"] > remote["x"] + remote["w"]
                    )
                else:
                    self.assertGreater(g["edgeX"], self.geo["S1"]["x"] + self.geo["S1"]["w"])
                    self.assertLess(g["edgeX"], self.geo["S2"]["x"])

    def test_wan_circuits_do_not_cross_each_other(self):
        pattern = (
            r'"(WAN-(?:PRIMARIA|RESPALDO)-HQ-(?:S1|S2))":'
            r'\{sx:(\d+),sy:(\d+),outX:(\d+),crossY:(\d+),'
            r'edgeX:(\d+),dy:(\d+),dx:(\d+),lx:(\d+),ly:(\d+)\}'
        )
        segments = {}
        for match in re.finditer(pattern, self.html):
            x0, y0, x1, y1, x2, y2, x3 = map(int, match.groups()[1:8])
            points = [(x0, y0), (x1, y0), (x1, y1),
                      (x2, y1), (x2, y2), (x3, y2)]
            segments[match.group(1)] = list(zip(points, points[1:]))

        def intersects(a, b):
            (x1, y1), (x2, y2) = a
            (x3, y3), (x4, y4) = b
            av, bv = x1 == x2, x3 == x4
            if av and not bv:
                return (min(y1, y2) <= y3 <= max(y1, y2) and
                        min(x3, x4) <= x1 <= max(x3, x4))
            if not av and bv:
                return (min(x1, x2) <= x3 <= max(x1, x2) and
                        min(y3, y4) <= y1 <= max(y3, y4))
            if av and bv:
                return x1 == x3 and max(min(y1, y2), min(y3, y4)) <= min(max(y1, y2), max(y3, y4))
            return y1 == y3 and max(min(x1, x2), min(x3, x4)) <= min(max(x1, x2), max(x3, x4))

        names = list(segments)
        self.assertEqual(len(names), 4)
        for i, first in enumerate(names):
            for second in names[i+1:]:
                with self.subTest(one=first, other=second):
                    self.assertFalse(any(
                        intersects(s1, s2)
                        for s1 in segments[first] for s2 in segments[second]
                    ), "Los enlaces deben transitar por carriles sin cruces")


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
