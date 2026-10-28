# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Guard the review finding that diagnostic canTrain calls can execute arbitrary Python or bypass the native player filter.
# This checks the protective call order, not every field or revision; native/in-game validation checks actual availability. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
from pathlib import Path
import unittest


class SGRMilitaryTrainabilityTests(unittest.TestCase):
    def test_callbacks_skip_census_before_player_or_city_queries(self):
        source = (Path(__file__).resolve().parents[4] / "CvGameCoreDLL/SASGameRecordLog.cpp").read_text(encoding="utf-8")
        start = source.index("static void logSASGameRecordMilitaryTrainability(")
        end = source.index("\nstatic void logSASGameRecordPlayerBonuses(", start)
        block = source[start:end]
        guard = block.index("if (GC.getPythonCaller()->isUseTrainCallbacks())")
        skip = block.index("return;", guard)
        self.assertLess(skip, block.index("kPlayer.canTrain(eUnit)"))
        self.assertLess(skip, block.index("pCapital->canTrain(eUnit)"))
        self.assertIn("snapshotValid=0 unavailableReason=TRAIN_CALLBACKS_ENABLED", block[guard:skip])


if __name__ == "__main__":
    unittest.main()
