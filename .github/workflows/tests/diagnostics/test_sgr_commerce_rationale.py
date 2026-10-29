# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Keep only the final-hook placement regression guard: emitting before mandatory Gold verification would report an allocation the AI did not finish with.
# Avoid duplicating the row schema/revision prose in tests; branch evaluation and native formatting are checked with the local VC2003 review fixture. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]


class SGRCommerceRationaleTests(unittest.TestCase):
    def test_single_final_observation_follows_gold_verification(self):
        source = (ROOT / "CvGameCoreDLL/CvPlayerAI.cpp").read_text(encoding="utf-8")
        start = source.index("void CvPlayerAI::AI_doCommerce()")
        end = source.index("static void collectSASGameRecordCivicChanges", start)
        commerce = source[start:end]
        hook = "logSASGameRecordAICommerceDecision(*this, kSASCommerce)"
        self.assertEqual(commerce.count(hook), 1)
        self.assertLess(commerce.index("verifyGoldCommercePercent();"), commerce.index(hook))


if __name__ == "__main__":
    unittest.main()
