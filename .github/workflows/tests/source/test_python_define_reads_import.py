# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_define_reads_import as checker


class PythonDefineReadsImportTests(unittest.TestCase):
	def test_module_constant_fails(self):
		text = 'IS_SHOW_AI_INFO = (gc.getDefineINT("SAS_SEVO_UNIT_SHOW_AI_INFORMATION") > 0)\n'
		self.assertEqual(checker.import_time_reads(text), [(1, "getDefineINT")])

	def test_read_in_function_passes(self):
		text = 'def f():\n\treturn gc.getDefineINT("PEACE_TREATY_LENGTH")\n'
		self.assertEqual(checker.import_time_reads(text), [])

	def test_class_body_fails_and_method_passes(self):
		text = 'class A:\n\tX = gc.getDefineINT("A")\n\tdef f(self):\n\t\tself.Y = gc.getDefineINT("B")\n'
		self.assertEqual(checker.import_time_reads(text), [(2, "getDefineINT")])

	def test_module_if_block_fails(self):
		text = 'if True:\n\tX = gc.getDefineSTRING("A")\n'
		self.assertEqual(checker.import_time_reads(text), [(2, "getDefineSTRING")])

	def test_multiline_signature_with_dedented_comment_passes(self):
		# <!-- custom: CvMapGeneratorUtil's __init__ signatures span lines with AdvCiv's "# </advc.137>" at a lower indent, which misled the line-based audit. (Claude code Opus 5.5) -->
		text = 'class F:\n\tdef __init__(self, a=None,\n\t# </advc.137>\nb=None):\n\t\tif a is None:\n\t\t\ta = gc.getDefineINT("A")\n'
		self.assertEqual(checker.import_time_reads(text), [])

	def test_one_line_def_and_lambda_pass(self):
		text = 'def f(): return gc.getDefineINT("A")\ng = lambda: gc.getDefineINT("B")\n'
		self.assertEqual(checker.import_time_reads(text), [])

	def test_default_arguments_and_lambda_neighbours_fail(self):
		# <!-- custom: Codex's three reproduced misses: these all run at import. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		text = 'def f(x=gc.getDefineINT("X")): pass\ng = lambda x=gc.getDefineINT("X"): x\nh = (lambda: None, gc.getDefineINT("X"))\n'
		self.assertEqual(checker.import_time_reads(text), [(1, "getDefineINT"), (2, "getDefineINT"), (3, "getDefineINT")])

	def test_lambda_in_default_keeps_its_body_lazy(self):
		text = 'def f(x=lambda: gc.getDefineINT("X")):\n\treturn x\n'
		self.assertEqual(checker.import_time_reads(text), [])

	def test_current_defines_at_import_fails(self):
		text = 'X = SASCurrentDefines.getInt("SAS_UI_FONT_LABEL")\ndef f():\n\treturn SASCurrentDefines.getInt("SAS_UI_FONT_LABEL")\n'
		self.assertEqual(checker.import_time_reads(text), [(1, "getInt")])

	def test_name_in_comment_or_string_passes(self):
		text = '# X = gc.getDefineINT("A")\nNAME = "getDefineINT"\n'
		self.assertEqual(checker.import_time_reads(text), [])


if __name__ == "__main__":
	unittest.main()
