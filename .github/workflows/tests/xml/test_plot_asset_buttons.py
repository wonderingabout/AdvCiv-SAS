# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; unittest exercises its sharing rules on small in-memory maps. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real audit rather than duplicating it. (Claude code Opus 5.5) -->
import plot_asset_buttons as check


class PlotAssetButtonsTests(unittest.TestCase):
    def test_improvement_and_its_build_may_share(self):
        buttons = {"IMPROVEMENT_FARM": "farm.dds", "BUILD_FARM": "farm.dds", "ROUTE_ROAD": "road.dds", "BUILD_ROAD": "road.dds"}
        self.assertEqual(check.check_plot_asset_buttons(buttons, {"BUILD_FARM": "IMPROVEMENT_FARM", "BUILD_ROAD": "ROUTE_ROAD"}), [])

    def test_two_improvements_sharing_fail(self):
        buttons = {"IMPROVEMENT_QUARRY": "quarry.dds", "IMPROVEMENT_PEAT_WORKS": "Quarry.dds", "BUILD_QUARRY": "quarry.dds"}
        failures = check.check_plot_asset_buttons(buttons, {"BUILD_QUARRY": "IMPROVEMENT_QUARRY"})
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("IMPROVEMENT_PEAT_WORKS", failures[0])

    def test_build_sharing_a_feature_button_fails(self):
        failures = check.check_plot_asset_buttons({"FEATURE_MARSH": "bog.dds", "BUILD_DRAIN_MARSH": "bog.dds"}, {})
        self.assertEqual(len(failures), 1, failures)

    def test_allowed_graphical_only_pair_passes(self):
        buttons = {"IMPROVEMENT_LAND_WORKED": "atlas,-1,-1", "IMPROVEMENT_WATER_WORKED": "atlas,-1,-1"}
        self.assertEqual(check.check_plot_asset_buttons(buttons, {}), [])


if __name__ == "__main__":
    unittest.main()
