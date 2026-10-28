# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: The native fixture executes Runtime in isolation, so it cannot catch misplaced hooks inside CvPlayer; preserve the required end-before-recursive-next-activation ordering here. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
# <!-- custom: pathlib locates the real native hook sites and unittest checks their relative order without asserting every recorder field or revision number. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
CPP = REPO_ROOT / "CvGameCoreDLL"
PLAYER = (CPP / "CvPlayer.cpp").read_text(encoding="latin-1")


class RuntimePlayerTurnTimingTests(unittest.TestCase):
    def test_native_player_lifecycle_hooks_keep_next_activation_after_end(self):
        function = PLAYER[PLAYER.index("void CvPlayer::setTurnActive(bool bNewValue, bool bDoTurn)"):PLAYER.index("void CvPlayer::onTurnLogging() const")]
        positions = [
            function.index("updateSASRuntimeStatusPlayerTurnStarted(getID())"),
            function.index("updateSASRuntimeStatusPlayerTurnMain(getID())"),
            function.index("updateSASRuntimeStatusPlayerTurnEnding(getID())"),
            function.index("updateSASRuntimeStatusPlayerTurnEnded(getID(), true)"),
        ]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(
            function.index("updateSASRuntimeStatusPlayerTurnEnded(getID(), true)"),
            function.index("GET_PLAYER((PlayerTypes)iI).setTurnActive(true)"),
            "current player timing must finish before recursive next-player activation",
        )
        self.assertIn("updateSASRuntimeStatusPlayerTurnEnded(getID(), false)", function)


if __name__ == "__main__":
    unittest.main()
