# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib/sys locate the checker; tempfile builds a fixture repository; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "xml"))

# <!-- custom: The check that the DLL's hand-written enums match the carried XML's types and order (KI#1104.3). (Claude code Opus 5.5) -->
import dll_enum_xml_order as checker

ENUMS = "ENUM_START(AnimationPath, ANIMATIONPATH)\n\tANIMATIONPATH_NONE = -1,\n\t// Default\n\tANIMATIONPATH_IDLE,\n\tANIMATIONPATH_MOVE, //!< note\nENUM_END(AnimationPath, ANIMATIONPATH)\n"


def paths_xml(types):
	return "<Civ4AnimationPathInfos><AnimationPaths>" + "".join("<AnimationPath><Type>%s</Type></AnimationPath>" % name for name in types) + "</AnimationPaths></Civ4AnimationPathInfos>"


# <!-- custom: A matching list passes, skipping the -1 NONE value and comments; swapped rows, a row the enum lacks and an enum value after the last row each fail. (Claude code Opus 5.5) -->
class EnumOrderTests(unittest.TestCase):
	def setUp(self):
		temporary = tempfile.TemporaryDirectory()
		self.addCleanup(temporary.cleanup)
		self.repo = Path(temporary.name)
		(self.repo / "CvGameCoreDLL").mkdir()
		(self.repo / "Assets/XML/Units").mkdir(parents=True)
		self.enums(ENUMS)
		self.pairs = checker.PAIRS
		checker.PAIRS = (("AnimationPath", "Assets/XML/Units/Civ4AnimationPathInfos.xml", "AnimationPath"),)
		self.addCleanup(setattr, checker, "PAIRS", self.pairs)

	def enums(self, text):
		(self.repo / "CvGameCoreDLL/CvEnums.h").write_text(text, encoding="latin-1")

	def xml(self, types):
		(self.repo / "Assets/XML/Units/Civ4AnimationPathInfos.xml").write_text(paths_xml(types), encoding="utf-8")

	def test_same_order_passes(self):
		self.xml(["ANIMATIONPATH_IDLE", "ANIMATIONPATH_MOVE"])
		self.assertEqual(checker.check(self.repo), [])

	def test_swapped_rows_fail(self):
		self.xml(["ANIMATIONPATH_MOVE", "ANIMATIONPATH_IDLE"])
		self.assertEqual(len(checker.check(self.repo)), 1)

	def test_row_missing_from_the_enum_fails(self):
		self.xml(["ANIMATIONPATH_IDLE", "ANIMATIONPATH_MOVE", "ANIMATIONPATH_FLY"])
		self.assertEqual(len(checker.check(self.repo)), 1)

	def test_enum_value_after_the_last_row_fails(self):
		self.xml(["ANIMATIONPATH_IDLE"])
		self.assertEqual(len(checker.check(self.repo)), 1)

	# <!-- custom: An explicit value shifts the rows' indices while the names still compare in order, the case Codex's review (GPT-6.2-Sol) reproduced; a block comment's value is no row. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def test_explicit_value_fails_and_block_comment_is_skipped(self):
		self.enums("ENUM_START(AnimationPath, ANIMATIONPATH)\n\tANIMATIONPATH_NONE = -1,\n\t/* ANIMATIONPATH_OLD, */\n\tANIMATIONPATH_IDLE = 4,\n\tANIMATIONPATH_MOVE,\nENUM_END(AnimationPath, ANIMATIONPATH)\n")
		self.xml(["ANIMATIONPATH_IDLE", "ANIMATIONPATH_MOVE"])
		self.assertEqual(len(checker.check(self.repo)), 1)
		self.enums("ENUM_START(AnimationPath, ANIMATIONPATH)\n\tANIMATIONPATH_NONE = -1,\n\t/* ANIMATIONPATH_OLD, */\n\tANIMATIONPATH_IDLE,\n\tANIMATIONPATH_MOVE,\nENUM_END(AnimationPath, ANIMATIONPATH)\n")
		self.assertEqual(checker.check(self.repo), [])

	# <!-- custom: A comment naming ENUM_END must not cut the block short, and a row under #if 0 must fail rather than count, both reproduced by Codex's review (GPT-6.2-Sol). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def test_comment_naming_the_end_and_conditional_rows(self):
		self.enums("ENUM_START(AnimationPath, ANIMATIONPATH)\n\tANIMATIONPATH_NONE = -1,\n\tANIMATIONPATH_IDLE, // not ENUM_END yet\n\tANIMATIONPATH_MOVE,\nENUM_END(AnimationPath, ANIMATIONPATH)\n")
		self.xml(["ANIMATIONPATH_IDLE", "ANIMATIONPATH_MOVE"])
		self.assertEqual(checker.check(self.repo), [])
		self.enums("ENUM_START(AnimationPath, ANIMATIONPATH)\n\tANIMATIONPATH_NONE = -1,\n\tANIMATIONPATH_IDLE,\n#if 0\n\tANIMATIONPATH_OLD,\n#endif\n\tANIMATIONPATH_MOVE,\nENUM_END(AnimationPath, ANIMATIONPATH)\n")
		self.assertEqual(len(checker.check(self.repo)), 1)

	def test_enum_members_stop_at_the_count(self):
		text = "ENUM_START(Direction, DIRECTION)\n\tNO_DIRECTION = -1,\n\tDIRECTION_NORTH,\n\tDIRECTION_EAST,\n\tNUM_ENUM_TYPES(DIRECTION),\n\tDIRECTION_NORTH_MASK = 1 << DIRECTION_NORTH,\nENUM_END(Direction, DIRECTION)\n"
		self.assertEqual(checker.enum_members(text, "Direction"), ["DIRECTION_NORTH", "DIRECTION_EAST"])


if __name__ == "__main__":
	unittest.main()
