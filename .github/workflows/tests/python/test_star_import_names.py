# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile hold a fixture repository, sys makes the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

# <!-- custom: Import the same helper python-ruff.yml runs. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "python"))
import star_import_names as checker


class StarImportNameTests(unittest.TestCase):
	# <!-- custom: KI#165.2's religionList was reported by Ruff only as F405, as the file star-imports CvPythonExtensions; names a star-imported module defines, recursively, must still pass. (Claude code Opus 5.5) -->
	def test_only_names_nothing_provides_fail(self):
		with tempfile.TemporaryDirectory() as folder:
			repo = Path(folder)
			python = repo / "Assets" / "Python"
			python.mkdir(parents=True)
			reference = repo / checker.API_REFERENCE
			reference.parent.mkdir(parents=True)
			reference.write_text("class CyGlobalContext\n", "utf-8")
			(python / "Helpers.py").write_text("from Constants import *\nHELPER_SIZE = 3\ndef drawHelper(x):\n\treturn x\n", "utf-8")
			(python / "Constants.py").write_text("PANE_SIZE = 8\n", "utf-8")
			(python / "Screen.py").write_text("from CvPythonExtensions import *\nfrom Helpers import *\n", "utf-8")
			report = [{"filename": "Assets/Python/Screen.py", "location": {"row": row}, "message": "`%s` may be undefined, or defined from star imports" % name}
				for row, name in ((3, "CyGlobalContext"), (4, "HELPER_SIZE"), (5, "drawHelper"), (6, "PANE_SIZE"), (7, "xrange"), (8, "religionList"))]
			found = checker.problems(repo, report)
			self.assertEqual(len(found), 1)
			self.assertIn("Screen.py:8: religionList", found[0])


	def test_legacy_except_binding_stays_in_its_handler(self):
		# <!-- custom: Python 2.4 binds the exception target even though Ruff reports it as F405.
		# A different scope still needs a binding. (GPT-6.2-Sol) -->
		source = ("def save():\n\ttry:\n\t\twrite()\n\texcept (IOError, ValueError), inst:\n"
			"\t\tif enabled:\n\t\t\tlog(inst)\n\t\tlog(inst)\ndef other():\n\tlog(inst)\n")
		self.assertEqual(checker.legacy_exception_bindings(source), {"inst": [(4, 7)]})

	def test_engine_names_require_an_engine_star_import(self):
		# <!-- custom: A class heading or DLL registration can name an extension export.
		# Method parameters cannot, and an unrelated star import does not bring in the engine. (GPT-6.2-Sol) -->
		with tempfile.TemporaryDirectory() as folder:
			repo = Path(folder)
			python = repo / "Assets" / "Python"
			python.mkdir(parents=True)
			reference = repo / checker.API_REFERENCE
			reference.parent.mkdir(parents=True)
			reference.write_text("CyInterface - not in SDK\nINT getCols (int iCols)\n", encoding="utf-8")
			dll = repo / "CvGameCoreDLL"
			dll.mkdir()
			(dll / "CyEnumsInterface.cpp").write_text('python::enum_<OptionTypes>("OptionTypes");\n', encoding="utf-8")
			(python / "Helpers.py").write_text("SIZE = 12\n", encoding="utf-8")
			(python / "Screen.py").write_text("from CvPythonExtensions import *\n", encoding="utf-8")
			(python / "Other.py").write_text("from Helpers import *\n", encoding="utf-8")
			report = [{"filename": "Assets/Python/" + file, "location": {"row": row}, "message": "`%s` may be undefined" % name}
				for file, row, name in (("Screen.py", 2, "CyInterface"), ("Screen.py", 3, "OptionTypes"),
					("Screen.py", 4, "iCols"), ("Screen.py", 5, "self"), ("Other.py", 2, "CyInterface"))]
			found = checker.problems(repo, report)
			self.assertEqual(len(found), 3)
			self.assertIn("Other.py:2: CyInterface", found[0])
			self.assertIn("Screen.py:4: iCols", found[1])
			self.assertIn("Screen.py:5: self", found[2])


if __name__ == "__main__":
	unittest.main()
