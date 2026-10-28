# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: A pre-move departure hook reported intended movement before immobile members could be left behind.
# Compilation cannot establish observation order, and an isolated recorder fixture does not exercise the gameplay call site; this small check protects that missing integration boundary.
# Native/in-game checks remain necessary for actual movement/count behavior. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
from pathlib import Path
import unittest


class SGREvacuationRecordTests(unittest.TestCase):
    def test_departure_verification_follows_movement_and_regrouping(self):
        source = (Path(__file__).resolve().parents[4] / "CvGameCoreDLL/CvSelectionGroup.cpp").read_text(encoding="utf-8")
        start = source.index("void CvSelectionGroup::groupMove(")
        block = source[start:source.index("\n\t//execute move", start)]
        hook = block.index("logSASGameRecordAIEvacuationDeparture(")
        self.assertGreater(hook, block.rindex("pUnit->move(*pPlot, true)"))
        self.assertGreater(hook, block.rindex("pUnit->joinGroup("))
        self.assertIn("if (bLogSGREvacuationDeparture) logSASGameRecordAIEvacuationDeparture", block)
        self.assertIn("aOriginalUnits", block[hook:])


if __name__ == "__main__":
    unittest.main()
