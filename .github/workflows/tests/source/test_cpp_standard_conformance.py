# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys locate the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
# <!-- custom: cpp_standard_conformance is the checker under test. (Claude code Opus 5.5) -->
import cpp_standard_conformance as checker


class CppStandardConformanceTests(unittest.TestCase):
	def problems(self, text):
		return checker.file_problems("CvGameCoreDLL/Test.cpp", text)

	def test_void_conditional_return_fails(self):
		# <!-- custom: The BtS form AdvCiv's 616238930 rewrote in CyPlayer::disbandUnit. (Claude code Opus 5.5) -->
		text = "void CyPlayer::disbandUnit(bool bAnnounce)\n{\n\treturn m_pPlayer ? m_pPlayer->disbandUnit(bAnnounce) : NULL;\n}\n"
		problems = self.problems(text)
		self.assertEqual(len(problems), 1)
		self.assertIn("Test.cpp:3: void function CyPlayer::disbandUnit", problems[0])

	def test_valid_returns_pass(self):
		text = (
			"void CyUnit::setXY(int iX, int iY)\n{\n\tif (m_pUnit)\n\t\treturn m_pUnit->setXY(iX, iY);\n}\n"
			"void CySelectionGroup::pushMission(int i)\n{\n\treturn m_p->pushMission(i, p == NULL ? NULL : p->getPlot());\n}\n"
			"int CyPlayer::getID()\n{\n\treturn m_pPlayer ? m_pPlayer->getID() : -1;\n}\n"
			"void f()\n{\n\t// return a ? b() : NULL;\n\tchar const* sz = \"return a ? b : c;\";\n\treturn;\n}\n"
		)
		self.assertEqual(self.problems(text), [])

	def test_include_backslash_and_varargs_fail(self):
		self.assertEqual(len(self.problems('#include ".\\cvreplaymessage.h"\n')), 1)
		self.assertEqual(self.problems('#include "CvReplayMessage.h"\n'), [])
		self.assertEqual(len(self.problems("void log(char const* format, ...)\n{\n\t_vsnprintf(buf, 10, format, (char*)(&format+1));\n}\n")), 1)


if __name__ == "__main__":
	unittest.main()
