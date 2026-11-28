# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: importlib loads the check from its file, as in test_advisor_tab_registry.py. See KI#1110.2. (Claude code Opus 5.5) -->
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location("pedia_item_kinds", ROOT / ".github/workflows/build/source/pedia_item_kinds.py")
assert _SPEC is not None and _SPEC.loader is not None
pedia_item_kinds = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pedia_item_kinds)

ENUMS = '''class SevoScreenEnums:
	PEDIA_UNITS = 204
	PEDIA_BUILDINGS = 209
	PEDIA_WORLD_WONDERS = 211
PEDIA_ITEM_KINDS = (
	("UNIT_", "getNumUnitInfos", "getUnitInfo", SevoScreenEnums.PEDIA_UNITS, (SevoScreenEnums.PEDIA_UNITS,), True),
	("BUILDING_", "getNumBuildingInfos", "getBuildingInfo", SevoScreenEnums.PEDIA_BUILDINGS, (SevoScreenEnums.PEDIA_BUILDINGS, SevoScreenEnums.PEDIA_WORLD_WONDERS), True),
	("HANDICAP_", "getNumHandicapInfos", "getHandicapInfo", None, (), False),
)
'''
JUMPS = '''def pediaJumpToUnit(argsList):
	if (bUsingSevopedia):
		pediaMainScreen.pediaJump(SevoScreenEnums.PEDIA_UNITS, argsList[0], True, False)

def pediaJumpToVote(argsList):
	pediaMainScreen.pediaJump(SevoScreenEnums.PEDIA_VOTES, argsList[0], True, False)

def pediaJumpToGameSpeed(argsList):
	pediaMainScreen.pediaJump(SevoScreenEnums.PEDIA_GAME_SPEED_CHART, argsList[0], True, False)
'''


class PediaItemKindsTests(unittest.TestCase):
	def kinds(self, text=ENUMS):
		(kinds, problems) = pedia_item_kinds.parse_kinds(text)
		self.assertEqual(problems, [])
		return kinds

	def test_table_parses(self):
		self.assertEqual([kind["prefix"] for kind in self.kinds()], ["UNIT_", "BUILDING_", "HANDICAP_"])

	def test_unknown_category_fails(self):
		(kinds, problems) = pedia_item_kinds.parse_kinds(ENUMS.replace("SevoScreenEnums.PEDIA_UNITS,), True", "SevoScreenEnums.PEDIA_UNIT,), True"))
		self.assertTrue([problem for problem in problems if "no PEDIA_UNIT" in problem])

	def test_category_outside_its_landing_fails(self):
		(kinds, problems) = pedia_item_kinds.parse_kinds(ENUMS.replace("(SevoScreenEnums.PEDIA_BUILDINGS, SevoScreenEnums.PEDIA_WORLD_WONDERS)", "(SevoScreenEnums.PEDIA_WORLD_WONDERS,)"))
		self.assertTrue([problem for problem in problems if "among its own landing" in problem])

	def test_entry_point_without_row_fails(self):
		# <!-- custom: The gap the table closed: the Sevopedia had vote pages that neither list named.
		# The game-speed chart is excused, as its item is packed. (Claude code Opus 5.5) -->
		problems = pedia_item_kinds.check_jumps(self.kinds(), JUMPS)
		self.assertEqual(len(problems), 1)
		self.assertIn("pediaJumpToVote", problems[0])

	def test_consumer_with_own_list_fails(self):
		problems = pedia_item_kinds.check_consumers({"SevoPediaMain.py": ("self.SAS_linkMatchDefs", "\t\tself.SAS_linkMatchDefs = (\n")})
		self.assertEqual(len(problems), 1)
		self.assertEqual(pedia_item_kinds.check_consumers({"SevoPediaMain.py": ("self.SAS_linkMatchDefs", "\t\tself.SAS_linkMatchDefs = tuple([row for row in PEDIA_ITEM_KINDS])\n")}), [])
		# <!-- custom: Codex's two false passes (2026-11-28): the table named in a comment, and a jump split over lines. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		self.assertEqual(len(pedia_item_kinds.check_consumers({"SevoPediaMain.py": ("self.SAS_linkMatchDefs", "\t\tself.SAS_linkMatchDefs = ((1, 2),)  # PEDIA_ITEM_KINDS\n")})), 1)

	def test_split_jump_is_found(self):
		problems = pedia_item_kinds.check_jumps(self.kinds(), "def pediaJumpToVote(argsList):\n\tpediaMainScreen.pediaJump(\n\t\tSevoScreenEnums.PEDIA_VOTES, argsList[0], True, False)\n")
		self.assertEqual(len(problems), 1)


if __name__ == "__main__":
	unittest.main()
