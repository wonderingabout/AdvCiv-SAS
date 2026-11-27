# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; tempfile isolates a minimal era XML; unittest exercises the tolerance and baseline coverage. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real XML reader and audit rather than duplicating them. (Claude code Opus 5.5) -->
import advanced_start_era_points as era_points


def flat_eras(**overrides):
    eras = {era: (points * 100 / percent, 100.0) for era, (points, percent) in era_points.ADVCIV_ERA_BASELINE.items()}
    eras.update(overrides)
    return eras


class AdvancedStartEraPointsTests(unittest.TestCase):
    def test_flat_costs_at_advciv_buying_power_pass(self):
        self.assertEqual(era_points.check_era_points(flat_eras()), [])

    def test_unscaled_points_fail_after_costs_are_flattened(self):
        failures = era_points.check_era_points(flat_eras(ERA_MODERN=(7500, 100.0)))
        self.assertEqual(len(failures), 1)
        self.assertIn("ERA_MODERN", failures[0])

    def test_tolerance_is_inclusive_and_covers_both_directions(self):
        self.assertEqual(era_points.check_era_points(flat_eras(ERA_ANCIENT=(440, 100.0))), [])
        self.assertEqual(era_points.check_era_points(flat_eras(ERA_ANCIENT=(360, 100.0))), [])
        self.assertEqual(len(era_points.check_era_points(flat_eras(ERA_ANCIENT=(441, 100.0)))), 1)
        self.assertEqual(len(era_points.check_era_points(flat_eras(ERA_ANCIENT=(359, 100.0)))), 1)

    def test_baseline_must_cover_every_era(self):
        eras = flat_eras(ERA_NEW=(100, 100.0))
        del eras["ERA_FUTURE"]
        failures = "\n".join(era_points.check_era_points(eras))
        self.assertIn("ERA_NEW", failures)
        self.assertIn("ERA_FUTURE", failures)

    def test_reader_averages_the_cost_percentages(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        path = root / era_points.ERA_INFOS_REL_PATH
        path.parent.mkdir(parents=True)
        path.write_text("<Root><EraInfo><Type>ERA_ANCIENT</Type><iAdvancedStartPoints>400</iAdvancedStartPoints><iTrainPercent>100</iTrainPercent><iConstructPercent>80</iConstructPercent><iGrowthPercent>90</iGrowthPercent></EraInfo></Root>", encoding="utf-8")
        self.assertEqual(era_points.read_eras(root), {"ERA_ANCIENT": (400, 90.0)})


if __name__ == "__main__":
    unittest.main()
