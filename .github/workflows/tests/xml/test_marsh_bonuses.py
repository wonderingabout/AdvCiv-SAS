# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates a minimal bonus XML; unittest exercises the decision rules. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real XML reader and audit rather than duplicating them. (Claude code Opus 5.5) -->
import marsh_bonuses


def bonus(bonus_type, terrains=(), features=(), feature_terrains=(), flat=True):
    def entries(list_tag, entry_tag, type_tag, flag_tag, values):
        return "<%s>%s</%s>" % (list_tag, "".join("<%s><%s>%s</%s><%s>1</%s></%s>" % (entry_tag, type_tag, v, type_tag, flag_tag, flag_tag, entry_tag) for v in values), list_tag)
    return ("<BonusInfo><Type>%s</Type><bFlatlands>%d</bFlatlands>" % (bonus_type, flat)
            + entries("TerrainBooleans", "TerrainBoolean", "TerrainType", "bTerrain", terrains)
            + entries("FeatureBooleans", "FeatureBoolean", "FeatureType", "bFeature", features)
            + entries("FeatureTerrainBooleans", "FeatureTerrainBoolean", "TerrainType", "bFeatureTerrain", feature_terrains)
            + "</BonusInfo>")


class MarshBonusesTests(unittest.TestCase):
    def read(self, bonuses_xml):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        path = root / marsh_bonuses.BONUS_INFOS_REL_PATH
        path.parent.mkdir(parents=True)
        path.write_text("<Root>" + bonuses_xml + "</Root>", encoding="utf-8")
        return marsh_bonuses.read_bonuses(root)

    def test_allowed_excluded_and_marsh_only_bonuses_pass(self):
        bonuses = self.read(bonus("BONUS_PIG", ["TERRAIN_GRASS"], ["FEATURE_MARSH"], ["TERRAIN_GRASS"]) + bonus("BONUS_CORN", ["TERRAIN_GRASS"]) + bonus("BONUS_PEAT", [], ["FEATURE_MARSH"], ["TERRAIN_GRASS"]) + bonus("BONUS_COAL", ["TERRAIN_GRASS"], flat=False))
        self.assertEqual(marsh_bonuses.check_marsh_bonuses(bonuses, {"BONUS_CORN": "dryland crop"}), [])

    def test_undecided_grassland_bonus_fails(self):
        bonuses = self.read(bonus("BONUS_WHEAT", ["TERRAIN_GRASS"]))
        failures = marsh_bonuses.check_marsh_bonuses(bonuses, {})
        self.assertEqual(len(failures), 1)
        self.assertIn("BONUS_WHEAT", failures[0])

    def test_stale_exclusions_and_unplaceable_marsh_fail(self):
        bonuses = self.read(bonus("BONUS_CORN", ["TERRAIN_GRASS"], ["FEATURE_MARSH"], ["TERRAIN_GRASS"]) + bonus("BONUS_SUGAR", [], ["FEATURE_MARSH"], ["TERRAIN_PLAINS"]) + bonus("BONUS_HORSE", ["TERRAIN_PLAINS"]))
        failures = marsh_bonuses.check_marsh_bonuses(bonuses, {"BONUS_CORN": "dryland crop", "BONUS_HORSE": "wet ground", "BONUS_GONE": "removed"})
        self.assertEqual(len(failures), 4, failures)


if __name__ == "__main__":
    unittest.main()
