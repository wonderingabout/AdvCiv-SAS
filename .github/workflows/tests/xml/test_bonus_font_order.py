# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the production checker; unittest exercises its order rules on small in-memory lists. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/xml"))

# <!-- custom: Exercise the real audit rather than duplicating it. (Claude code Opus 5.5) -->
import bonus_font_order as check


BONUSES = [("BONUS_A", "ART_A"), ("BONUS_B", "ART_B")]


class BonusFontOrderTests(unittest.TestCase):
    def test_matching_order_passes_with_extra_art_after(self):
        self.assertEqual(check.check_bonus_font_order(BONUSES, [("ART_A", 0), ("ART_B", 1), ("ART_UNUSED", 2)]), [])

    def test_bonus_on_another_glyph_fails(self):
        failures = check.check_bonus_font_order(BONUSES, [("ART_B", 0), ("ART_A", 1)])
        self.assertEqual(len(failures), 2, failures)

    def test_unsorted_art_and_shared_glyph_fail(self):
        failures = check.check_bonus_font_order(BONUSES, [("ART_B", 1), ("ART_A", 0), ("ART_C", 1)])
        self.assertTrue(any("not sorted" in f for f in failures), failures)
        self.assertTrue(any("already used" in f for f in failures), failures)


if __name__ == "__main__":
    unittest.main()
