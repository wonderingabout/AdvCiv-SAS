# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: Keep only integration checks that the standalone native fixture cannot cover: production hook ordering and absence of a per-frame group scan.
# Removed revision/field-name presence assertions because they duplicated existing revision checks and the native JSON/lifecycle fixture, adding maintenance without testing more behavior. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
CPP = REPO_ROOT / "CvGameCoreDLL"
INTERFACE = (CPP / "CvGameInterface.cpp").read_text(encoding="latin-1")


class RuntimeTurnReadinessTests(unittest.TestCase):
    def test_end_turn_request_is_captured_before_send(self):
        do_control = INTERFACE.index("void CvGame::doControl(ControlTypes eControl)")
        start = INTERFACE.index("case CONTROL_ENDTURN:", do_control)
        end = INTERFACE.index("case CONTROL_AUTOMOVES:", start)
        block = INTERFACE[start:end]
        normal, forced = block.split("case CONTROL_FORCEENDTURN:", 1)
        for branch in (normal, forced):
            self.assertLess(branch.index("updateSASRuntimeStatusEndTurnRequest"), branch.index("CvMessageControl::getInstance().sendTurnComplete()"))
            self.assertLess(branch.index("if (isSASRuntimeStatusEnabled())"), branch.index("getHeadSelectedUnit()"))

    def test_ui_ready_boundaries_use_inherited_end_turn_message_transitions(self):
        start = INTERFACE.index("void CvGame::updateTestEndTurn()")
        end = INTERFACE.index("CvUnit* CvGame::getPlotUnits", start)
        block = INTERFACE[start:end]
        false_pos = block.index("kUI.setEndTurnMessage(false)")
        false_hook = block.index("updateSASRuntimeStatusEndTurnReady(getActivePlayer(), false)")
        true_pos = block.index("kUI.setEndTurnMessage(true)")
        true_hook = block.index("updateSASRuntimeStatusEndTurnReady(getActivePlayer(), true)")
        self.assertLess(false_pos, false_hook)
        self.assertLess(true_pos, true_hook)
        self.assertNotIn("getSASRuntimeTurnReadinessSnapshot", block, "readiness transitions must not add per-frame group scans")


if __name__ == "__main__":
    unittest.main()
