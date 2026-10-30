# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Keep one integration guard against duplicating the real randomized chooser's RNG, eligibility or price queries for diagnostics.
# This does not prove full query ordering or gameplay neutrality; optimized compilation, the local sampler fixture and comparative game replays cover different risks. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]


class SGRUpgradeScrapReasoningTests(unittest.TestCase):
    def test_upgrade_context_observes_existing_randomized_loop(self):
        source = (ROOT / "CvGameCoreDLL/CvUnitAI.cpp").read_text(encoding="utf-8")
        start = source.index("bool CvUnitAI::AI_upgrade(")
        end = source.index("void CvUnitAI::AI_promote()", start)
        upgrade = source[start:end]
        self.assertEqual(upgrade.count("syncRand().get(21,"), 1)
        self.assertEqual(upgrade.count("canUpgrade(eLoopUnit)"), 1)
        self.assertEqual(upgrade.count("upgradePrice(eLoopUnit)"), 1)
        self.assertNotIn("AI_upgradePriority()", upgrade)


if __name__ == "__main__":
    unittest.main()
