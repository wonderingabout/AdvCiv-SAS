# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys find the helper, types stands in for desktop_windows, whose import calls ctypes.windll and fails on CI's Linux; unittest runs the fixtures. (Claude Code Opus 5.5) -->
from pathlib import Path
import sys
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "LLM_Helpers" / "desktop"))
sys.modules.setdefault("desktop_windows", types.ModuleType("desktop_windows"))
# <!-- custom: agent_message, the helper under test, imported after its Windows-only dependency is stubbed. (Claude Code Opus 5.5) -->
import agent_message

TEXT_LINE = (240, 1950, 1600, 1990)
TOOLBAR = (240, 2000, 1600, 2040)


# <!-- custom: Fixtures for decide_box, which tells an empty message box from a draft before agent_message.py pastes into another agent's app; each reading is (name, area, dark, gray, gray_left, frame found).
# They encode the 2026-11-26 cases: a zoom change left stale areas, and Codex's review (GPT-6.2-Sol) showed that picking the area with the most ink could choose a toolbar crop over the real text line holding a short draft. (Claude Code Opus 5.5 + GPT-6.2-Sol) -->
class DecideBoxTests(unittest.TestCase):
	def test_placeholder_at_the_left_edge_is_empty(self):
		self.assertEqual(agent_message.decide_box([("line", TEXT_LINE, 0, 253, 240, True)]), ("EMPTY", 0))

	def test_short_draft_is_not_empty(self):
		self.assertEqual(agent_message.decide_box([("line", TEXT_LINE, 20, 30, 240, True)]), ("NOT_EMPTY", 0))

	def test_toolbar_with_more_ink_does_not_hide_a_draft(self):
		readings = [("toolbar", TOOLBAR, 0, 400, 300, False), ("line", TEXT_LINE, 20, 30, 240, True)]
		self.assertEqual(agent_message.decide_box(readings)[0], "NOT_EMPTY")

	def test_gray_away_from_the_left_edge_is_unknown(self):
		self.assertEqual(agent_message.decide_box([("toolbar", TOOLBAR, 0, 400, 300, False)])[0], "UNKNOWN")

	def test_stale_area_clipping_the_placeholder_is_unknown(self):
		self.assertEqual(agent_message.decide_box([("stale", TEXT_LINE, 0, 38, 240, True)])[0], "UNKNOWN")

	def test_two_matching_areas_are_unknown(self):
		readings = [("a", TEXT_LINE, 0, 253, 240, True), ("b", TOOLBAR, 0, 120, 242, True)]
		self.assertEqual(agent_message.decide_box(readings)[0], "UNKNOWN")

	def test_left_aligned_gray_outside_the_frame_is_unknown(self):
		# <!-- custom: Codex's reproduction (GPT-6.2-Sol): a gray toolbar starting at the area's left edge read as an empty box before the frame check. (Claude Code Opus 5.5 + GPT-6.2-Sol) -->
		self.assertEqual(agent_message.decide_box([("toolbar", TOOLBAR, 0, 400, 242, False)])[0], "UNKNOWN")

	def test_caret_alone_stays_empty(self):
		self.assertEqual(agent_message.decide_box([("line", TEXT_LINE, 5, 253, 240, True)]), ("EMPTY", 0))


if __name__ == "__main__":
	unittest.main()
