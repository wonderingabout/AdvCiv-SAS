# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates minimal building XML and CustomDomAdv layouts; unittest exercises the derived BLDGCIV key contract. (ChatGPT-5.6-Sol) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real CustomDomAdv key scan and building XML readers rather than duplicating them. (Claude code Opus 5.5) -->
import civ_specific_assets as civ_assets


CLASS_XML = """<Root>
<BuildingClassInfo><Type>BUILDINGCLASS_MARKET</Type><DefaultBuilding>BUILDING_MARKET</DefaultBuilding></BuildingClassInfo>
</Root>"""
BUILDING_XML = """<Root>
<BuildingInfo><BuildingClass>BUILDINGCLASS_MARKET</BuildingClass><Type>BUILDING_MARKET</Type></BuildingInfo>
<BuildingInfo><BuildingClass>BUILDINGCLASS_MARKET</BuildingClass><Type>BUILDING_TEST_BAZAAR</Type></BuildingInfo>
</Root>"""


class CustomDomAdvCivBuildingTests(unittest.TestCase):
    def run_check(self, key):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            class_path = root / "Assets/XML/Buildings/CIV4BuildingClassInfos.xml"
            info_path = root / "Assets/XML/Buildings/CIV4BuildingInfos.xml"
            settings_path = root / "Settings/CustomDomAdv/CustomDomAdv.txt"
            class_path.parent.mkdir(parents=True, exist_ok=True)
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            class_path.write_text(CLASS_XML, encoding="utf-8")
            info_path.write_text(BUILDING_XML, encoding="utf-8")
            settings_path.write_bytes(("a(S'%s'\n" % key).encode("ascii"))
            return civ_assets.check_custom_dom_adv_civ_specific_building_refs(root)

    def test_current_civ_specific_building_key_passes(self):
        self.assertEqual(self.run_check("BLDGCIV_BUILDING_TEST_BAZAAR"), [])

    def test_stale_building_key_fails(self):
        failures = self.run_check("BLDGCIV_BUILDING_TEST_OLD_BAZAAR")
        self.assertEqual(len(failures), 1)
        self.assertIn("missing building BUILDING_TEST_OLD_BAZAAR", failures[0])

    def test_generic_building_key_fails(self):
        failures = self.run_check("BLDGCIV_BUILDING_MARKET")
        self.assertEqual(len(failures), 1)
        self.assertIn("non-civ-specific building BUILDING_MARKET", failures[0])


if __name__ == "__main__":
    unittest.main()
