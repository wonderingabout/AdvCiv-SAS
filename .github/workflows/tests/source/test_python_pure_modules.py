# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_pure_modules as checker


class PythonPureModulesTests(unittest.TestCase):
	def test_plain_values_pass(self):
		text = '# ci_pure_module: test\nA = 1\nB = -2\nC = "x"\nD = (1, "a", None, True)\nE = {"k": [1, 2]}\nF = G = 0\n'
		self.assertTrue(checker.marked(text))
		self.assertEqual(checker.impure_statements(text), [])

	def test_imports_calls_and_computed_values_fail(self):
		text = 'import os\nA = 1 + 2\nB = len("x")\ndef f():\n\tpass\nC.x = 1\n'
		self.assertEqual([line for line, _ in checker.impure_statements(text)], [1, 2, 3, 4, 6])

	def test_codex_cases_fail(self):
		# <!-- custom: Codex's review (GPT-6.2-Sol) reproduced literal_eval letting these through or raising; each now fails cleanly. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		text = 'A = set()\nB = {1, 2}\nC = 1 + 2j\nD = {[1]: 2}\nE: int = 1\nF += 1\nG = {{}: 1}\nH = {([],): 1}\nI = {(1, "a"): 2}\n'
		self.assertEqual([line for line, _ in checker.impure_statements(text)], [1, 2, 3, 4, 5, 6, 7, 8])

	def test_marker_in_a_string_does_not_mark(self):
		text = 'NOTE = "ci_pure_module: no"\n'
		self.assertFalse(checker.marked(text))


if __name__ == "__main__":
	unittest.main()
