# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates a minimal unit XML; unittest exercises the shared-set rule. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real XML reader and audit rather than duplicating them. (Claude code Opus 5.5) -->
import feature_impassables as impassables


def unit(unit_type, features):
    entries = "".join("<FeatureImpassable><FeatureType>%s</FeatureType><bFeatureImpassable>1</bFeatureImpassable></FeatureImpassable>" % f for f in features)
    return "<UnitInfo><Type>%s</Type><FeatureImpassables>%s</FeatureImpassables></UnitInfo>" % (unit_type, entries)


class FeatureImpassablesTests(unittest.TestCase):
    def read(self, units_xml):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        path = root / impassables.UNIT_INFOS_REL_PATH
        path.parent.mkdir(parents=True)
        path.write_text("<Root>" + units_xml + "</Root>", encoding="utf-8")
        return impassables.read_impassables(root)

    def test_shared_set_passes_and_free_units_are_ignored(self):
        units = self.read(unit("UNIT_CHARIOT", ["FEATURE_FOREST", "FEATURE_MARSH"]) + unit("UNIT_CANNON", ["FEATURE_MARSH", "FEATURE_FOREST"]) + unit("UNIT_WARRIOR", []))
        self.assertEqual(sorted(units), ["UNIT_CANNON", "UNIT_CHARIOT"])
        self.assertEqual(impassables.check_impassables(units), [])

    def test_unit_missing_a_feature_fails(self):
        units = self.read(unit("UNIT_CHARIOT", ["FEATURE_FOREST", "FEATURE_MARSH"]) + unit("UNIT_CATAPULT", ["FEATURE_FOREST", "FEATURE_MARSH"]) + unit("UNIT_CANNON", ["FEATURE_FOREST"]))
        failures = impassables.check_impassables(units)
        self.assertEqual(len(failures), 1)
        self.assertIn("UNIT_CANNON", failures[0])
        self.assertIn("missing FEATURE_MARSH", failures[0])

    def test_disabled_entry_is_not_impassable(self):
        units = self.read("<UnitInfo><Type>UNIT_CHARIOT</Type><FeatureImpassables><FeatureImpassable><FeatureType>FEATURE_FOREST</FeatureType><bFeatureImpassable>0</bFeatureImpassable></FeatureImpassable></FeatureImpassables></UnitInfo>")
        self.assertEqual(units, {})


if __name__ == "__main__":
    unittest.main()
