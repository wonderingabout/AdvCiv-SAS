# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile build a disposable DLL folder; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
# <!-- custom: python_wrapper_null_args is the checker under test. (Claude code Opus 5.5) -->
import python_wrapper_null_args as checker

HEADER = "class CvUnit {\npublic:\n\tint currCombatStr(CvPlot const* pPlot = NULL, CvUnit const* pAttacker = NULL) const;\n\tbool canMoveInto(CvPlot const& kPlot) const;\n\tint plain(CvPlot const* pPlot) const;\n};\n"


class WrapperNullArgsTests(unittest.TestCase):
	def errors(self, body):
		with tempfile.TemporaryDirectory() as folder:
			root = Path(folder)
			(root / "CvGameCoreDLL").mkdir()
			(root / "CvGameCoreDLL" / "CvUnit.h").write_text(HEADER, encoding="utf-8")
			defaults = checker.null_defaults(root)
			return checker.wrapper_errors("\n" + body + "\n", "CvGameCoreDLL/CyUnit.cpp", defaults)

	def test_dereferenced_null_default_fails(self):
		# <!-- custom: KI#1091's shape: the native function takes NULL for both, the wrapper dereferenced both. (Claude code Opus 5.5) -->
		self.assertEqual(len(self.errors("int CyUnit::currCombatStr(CyPlot* pPlot, CyUnit* pAttacker)\n{\n\treturn m_pUnit ? m_pUnit->currCombatStr(pPlot->getPlot(), pAttacker->getUnit()) : -1;\n}")), 2)

	def test_guarded_argument_passes(self):
		self.assertEqual(self.errors("int CyUnit::currCombatStr(CyPlot* pPlot, CyUnit* pAttacker)\n{\n\treturn m_pUnit ? m_pUnit->currCombatStr(pPlot == NULL ? NULL : pPlot->getPlot(), (pAttacker == NULL ? NULL : pAttacker->getUnit())) : -1;\n}"), [])

	def test_parameter_without_null_default_passes(self):
		# <!-- custom: A native parameter with no NULL default, such as canWork's plot, needs a real object, so dereferencing it is fine. (Claude code Opus 5.5) -->
		self.assertEqual(self.errors("int CyUnit::plain(CyPlot* pPlot)\n{\n\treturn m_pUnit ? m_pUnit->plain(pPlot->getPlot()) : -1;\n}"), [])

	def test_comments_are_ignored(self):
		self.assertEqual(self.errors("int CyUnit::currCombatStr(CyPlot* pPlot, CyUnit* pAttacker)\n{\n\t// was m_pUnit->currCombatStr(pPlot->getPlot(), pAttacker->getUnit())\n\treturn -1;\n}"), [])


if __name__ == "__main__":
	unittest.main()
