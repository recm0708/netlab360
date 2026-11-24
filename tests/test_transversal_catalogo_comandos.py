"""Comprobamos la integridad del catálogo de operación."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "operacion/comandos"


class CommandCatalogTests(unittest.TestCase):

    def test_phase_coverage(self):
        files = sorted(CATALOG.glob("s*.md"))

        self.assertEqual(
            [p.name[:3] for p in files],
            [f"s{n:02d}" for n in range(1, 8)],
        )

    def test_index_contains_every_phase(self):
        text = (CATALOG / "README.md").read_text()

        for path in CATALOG.glob("s*.md"):
            self.assertIn(f"]({path.name})", text)

    def test_relative_links_exist(self):
        for path in CATALOG.glob("*.md"):
            text = path.read_text()

            for target in re.findall(
                r"\]\(([^)]+)\)", text
            ):
                if "://" not in target:
                    destination = (
                        path.parent / target.split("#")[0]
                    ).resolve()

                    self.assertTrue(
                        destination.exists(),
                        f"{path.name}: {target}",
                    )

    def test_referenced_source_commands_exist(self):
        for path in CATALOG.glob("*.md"):
            text = path.read_text()

            blocks = re.findall(
                r"```bash\n(.*?)```", text, re.S
            )

            for block in blocks:
                sources = re.findall(
                    r"\b(?:operacion|scripts|ansible|"
                    r"servicios|inventario)/"
                    r"[a-zA-Z0-9_./-]+"
                    r"\.(?:py|sh|yml|yaml|tf)",
                    block,
                )

                for source in sources:
                    self.assertTrue(
                        (ROOT / source).is_file(),
                        source,
                    )

    def test_no_historical_session_identifiers(self):
        for path in CATALOG.glob("*.md"):
            self.assertNotRegex(
                path.read_text(),
                r"S06_(?:BASELINE|PERF)_20\d{6}T",
            )

    def test_no_automatic_intervention_commands(self):
        for path in CATALOG.glob("*.md"):
            text = path.read_text()

            blocks = re.findall(
                r"```bash\n(.*?)```", text, re.S
            )

            for block in blocks:
                self.assertNotRegex(
                    block,
                    r"--apply|--confirm-fault|--approve-batch"
                    r"|approve-execute|systemctl stop"
                    r"|systemctl restart",
                )


if __name__ == "__main__":
    unittest.main()
