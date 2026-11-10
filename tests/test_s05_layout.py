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

    def test_wan_exclusive_corridor(self):
        hq = self.geo["HQ"]
        self.assertEqual(hq["y"] + hq["h"], 390)
        for site in ("S1", "S2"):
            self.assertEqual(self.geo[site]["y"], 606)
        self.assertIn('y1=390,y2=606', self.html)
        for ly in (488, 546):
            self.assertGreaterEqual(ly - 23, 390 + 30)
            self.assertLessEqual(ly + 23, 606 - 30)

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


if __name__ == "__main__":
    unittest.main()
