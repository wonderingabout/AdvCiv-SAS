# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile build a small fake repository; sys locates the checker; unittest runs the cases. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
# <!-- custom: shared_define_values is the checker under test. (Claude code Opus 5.5) -->
import shared_define_values as checker


class SharedDefineValuesTests(unittest.TestCase):
	def problems(self, relative, source):
		with tempfile.TemporaryDirectory() as folder:
			path = Path(folder) / relative
			path.parent.mkdir(parents=True)
			path.write_text(source, encoding="utf-8")
			return checker.find_problems(Path(folder))

	def test_copied_values_fail(self):
		# <!-- custom: The old toggle table and the old inline runtime dict. (Claude code Opus 5.5) -->
		self.assertEqual(len(self.problems("LLM_Helpers/toggle.py", 'TABLE = {\n    "SAS_UI_DAWN_OF_MAN_ON": (1, 0),\n}\n')), 1)
		self.assertEqual(len(self.problems(".github/workflows/build/check.py", 'require({"SAS_RUNTIME_STATUS_ON": 0, "SAS_SGR_LOG": 3})\n')), 1)
		self.assertEqual(len(self.problems("LLM_Helpers/pairs.py", "VALUES = [('SAS_SGR_LOG', 0)]\n")), 1)

	def test_names_comments_tests_and_owner_pass(self):
		self.assertEqual(self.problems("Assets/Python/screen.py", 'level = gc.getDefineINT("SAS_SGR_LOG")\nnames = ("SAS_SGR_LOG", "SAS_UI_DAWN_OF_MAN_ON")\n'), [])
		self.assertEqual(self.problems("LLM_Helpers/notes.py", '# was {"SAS_SGR_LOG": 3}\n'), [])
		self.assertEqual(self.problems(".github/workflows/tests/test_x.py", 'defines = {"SAS_RUNTIME_STATUS_ON": 1}\n'), [])
		self.assertEqual(self.problems("LLM_Helpers/diagnostics/define_values.py",'X = {"SAS_SGR_LOG": 0}\n'), [])


if __name__ == "__main__":
	unittest.main()
