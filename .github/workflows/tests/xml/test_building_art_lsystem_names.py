# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates the fixture XML; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real art define scan rather than duplicating it. (Claude code Opus 5.5) -->
import building_art_lsystem_names as lsys


class BuildingArtLSystemNamesTests(unittest.TestCase):
    def run_check(self, lsystem, city_lsystem=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = {lsys.BUILDING_ART: f"<Root><BuildingArtInfo><Type>ART_DEF_BUILDING_TEST</Type><LSystem>{lsystem}</LSystem></BuildingArtInfo></Root>"}
            if city_lsystem is not None:
                files[lsys.SAS_CITY_LSYSTEM] = city_lsystem
            for rel_path, content in files.items():
                (root / rel_path).parent.mkdir(parents=True, exist_ok=True)
                (root / rel_path).write_text(content, encoding="utf-8")
            return lsys.check(root)

    def test_bts_name_passes(self):
        self.assertEqual(self.run_check("LSYSTEM_2x2"), [])

    # <!-- custom: The Chieftain's Hall case: an RI-only name with no SAS city L-system. See KI#1074. (Claude code Opus 5.5) -->
    def test_other_mod_name_fails(self):
        self.assertEqual(len(self.run_check("LSYSTEM_VIKING_TEMPLE")), 1)

    def test_sas_city_lsystem_replaces_bts_names(self):
        city = '<Root><ArtRef Name="building:LSYSTEM_VIKING_TEMPLE"/></Root>'
        self.assertEqual(self.run_check("LSYSTEM_VIKING_TEMPLE", city), [])
        self.assertEqual(len(self.run_check("LSYSTEM_2x2", city)), 1)


if __name__ == "__main__":
    unittest.main()
