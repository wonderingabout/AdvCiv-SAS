# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_runtime_placement as checker


class PythonRuntimePlacementTests(unittest.TestCase):
	def test_engine_imports_are_found(self):
		text = 'from CvPythonExtensions import *\nimport os, CvPythonExtensions\nfrom CvPythonExtensions import CyGlobalContext\n'
		self.assertEqual(checker.imports_engine(text), [1, 2, 3])

	def test_mentions_and_other_modules_pass(self):
		# <!-- custom: The CI stubs name the module in sys.modules and comments, which is no import. (Claude code Opus 5.5) -->
		text = '# from CvPythonExtensions import *\nsys.modules["CvPythonExtensions"] = engine\nimport CvPythonExtensionsHelper\nfrom os import CvPythonExtensions\n'
		self.assertEqual(checker.imports_engine(text), [])

	def test_codex_cases(self):
		# <!-- custom: Codex's review (GPT-6.2-Sol) reproduced these against the first draft: two misses, an alias counted as the module, and a BOM before the first import. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		text = 'x = 1; import CvPythonExtensions\nif enabled: from CvPythonExtensions import *\nimport os as CvPythonExtensions\nfrom CvPythonExtensions import (a,\n\tb)\nimport CvPythonExtensions as engine\n'
		self.assertEqual(checker.imports_engine(text), [1, 2, 4, 6])
		path = Path(__file__).resolve().parent / "_bom_fixture.py"
		path.write_bytes(b"\xef\xbb\xbfimport CvPythonExtensions\n")
		try:
			self.assertEqual(checker.imports_engine(checker.read_text(path)), [1])
		finally:
			path.unlink()

	def test_runtime_folders_are_recognized(self):
		self.assertTrue(checker.is_runtime("Assets/Python/CvUtil.py"))
		self.assertTrue(checker.is_runtime("PrivateMaps/Pangaea.py"))
		self.assertFalse(checker.is_runtime("Assets/PythonOther/x.py"))
		self.assertFalse(checker.is_runtime("LLM_Helpers/saspilot/SASPilotCommands.py"))


if __name__ == "__main__":
	unittest.main()
