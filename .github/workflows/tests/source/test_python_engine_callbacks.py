# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib, sys and tempfile build a throwaway repository and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_engine_callbacks as checker


class PythonEngineCallbacksTests(unittest.TestCase):
	def test_only_top_level_defs_count(self):
		text = "def finishText(argsList):\n\treturn 0\nclass A:\n\tdef toggleDebugMode(self):\n\t\tpass\n# def run():\n"
		self.assertEqual(checker.defined_functions(text), {"finishText"})

	def test_def_in_a_string_does_not_count(self):
		text = 'DOC = """\ndef run():\n"""\ndef create():\n\tpass\n'
		self.assertEqual(checker.defined_functions(text), {"create"})

	def test_missing_callback_and_file_fail(self):
		with tempfile.TemporaryDirectory() as folder:
			root = Path(folder)
			path = root / "Assets/Python/EntryPoints/CvTranslator.py"
			path.parent.mkdir(parents=True)
			path.write_text("def printOutText(argsList):\n\tpass\n")
			problems = checker.find_problems(root)
		self.assertTrue(any("CvTranslator.py: no top-level def finishText" in problem for problem in problems))
		self.assertTrue(any("PbMain.py: missing" in problem for problem in problems))

	def test_repository_passes(self):
		self.assertEqual(checker.find_problems(Path(__file__).resolve().parents[4]), [])


if __name__ == "__main__":
	unittest.main()
